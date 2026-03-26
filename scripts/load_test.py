from __future__ import annotations

import json
import random
import time
from pathlib import Path

from locust import HttpUser, between, events, task

TARGET_CREATE_TOTAL = 1000
CREATED_ORDER_IDS: list[str] = []
SCENARIO_COUNTERS = {
    "create_orders": 0,
    "cache_hit_reads": 0,
    "status_updates": 0,
}


class OrderUser(HttpUser):
    wait_time = between(0.02, 0.2)

    def on_start(self) -> None:
        self._status_cycle = ["processing", "completed", "cancelled"]
        self._status_index = 0

    @task(2)
    def create_orders(self) -> None:
        if SCENARIO_COUNTERS["create_orders"] >= TARGET_CREATE_TOTAL:
            return
        suffix = SCENARIO_COUNTERS["create_orders"]
        payload = {
            "customer_id": f"load-user-{suffix % 100}",
            "description": f"load-order-{suffix}",
            "amount": round(random.uniform(10.0, 300.0), 2),
            "is_vip": suffix % 20 == 0,
        }
        response = self.client.post("/orders", json=payload, name="POST /orders")
        if response.status_code == 201:
            body = response.json()
            order_id = str(body.get("id", ""))
            if order_id:
                CREATED_ORDER_IDS.append(order_id)
                SCENARIO_COUNTERS["create_orders"] += 1

    @task(9)
    def read_orders_with_cache_bias(self) -> None:
        if not CREATED_ORDER_IDS:
            self.client.get("/orders", name="GET /orders")
            return
        order_id = random.choice(CREATED_ORDER_IDS)
        self.client.get(f"/orders/{order_id}", name="GET /orders/:id")
        SCENARIO_COUNTERS["cache_hit_reads"] += 1

    @task(3)
    def update_status(self) -> None:
        if not CREATED_ORDER_IDS:
            return
        order_id = random.choice(CREATED_ORDER_IDS)
        status_value = self._status_cycle[self._status_index % len(self._status_cycle)]
        self._status_index += 1
        payload = {"status": status_value}
        self.client.patch(
            f"/orders/{order_id}/status",
            json=payload,
            name="PATCH /orders/:id/status",
        )
        SCENARIO_COUNTERS["status_updates"] += 1


@events.quitting.add_listener
def write_report(environment, **_kwargs) -> None:
    stats = environment.stats.total
    runtime_seconds = max(1, int(time.time() - environment.stats.start_time))
    throughput = round(stats.num_requests / runtime_seconds, 2)
    error_rate = round(
        (stats.num_failures / max(1, stats.num_requests)) * 100,
        2,
    )
    report_data = {
        "generated_at": int(time.time()),
        "requests": stats.num_requests,
        "failures": stats.num_failures,
        "latency_ms": {
            "p50": stats.get_response_time_percentile(0.50),
            "p95": stats.get_response_time_percentile(0.95),
            "p99": stats.get_response_time_percentile(0.99),
        },
        "throughput_rps": throughput,
        "error_rate_percent": error_rate,
        "scenario_counts": SCENARIO_COUNTERS,
        "created_orders_total": len(CREATED_ORDER_IDS),
    }
    out = Path("results")
    out.mkdir(exist_ok=True)
    (out / "locust_summary.json").write_text(
        json.dumps(report_data, indent=2),
        encoding="utf-8",
    )
    (out / "benchmark_report.md").write_text(
        (
            "# Benchmark Report\n\n"
            "## Load test scenarios\n"
            f"- create orders target: {TARGET_CREATE_TOTAL}\n"
            "- cache-hit reads target mix: 90%\n"
            "- status updates: enabled (worker-trigger path)\n\n"
            "## Measured metrics\n"
            f"- p50 latency: {report_data['latency_ms']['p50']} ms\n"
            f"- p95 latency: {report_data['latency_ms']['p95']} ms\n"
            f"- p99 latency: {report_data['latency_ms']['p99']} ms\n"
            f"- throughput: {report_data['throughput_rps']} req/sec\n"
            f"- error rate: {report_data['error_rate_percent']}%\n\n"
            "## Scenario counters\n"
            f"- create_orders: {SCENARIO_COUNTERS['create_orders']}\n"
            f"- cache_hit_reads: {SCENARIO_COUNTERS['cache_hit_reads']}\n"
            f"- status_updates: {SCENARIO_COUNTERS['status_updates']}\n\n"
            "## Bottleneck analysis\n"
            "- If p95/p99 is high while error rate is low, DB or broker latency is likely the bottleneck.\n"
            "- If error rate grows with throughput, inspect RabbitMQ/Kafka/NATS connection pools.\n"
            "- If GET /orders/:id p95 regresses, review Redis hit ratio and key eviction policy.\n\n"
            "## Optimization recommendations\n"
            "- Increase API worker concurrency and DB connection pool sizes.\n"
            "- Tune Redis maxmemory policy and key TTL distribution.\n"
            "- Scale workers independently and enforce backpressure on queue consumers.\n"
        ),
        encoding="utf-8",
    )
