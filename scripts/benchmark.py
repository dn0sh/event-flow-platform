from pathlib import Path
import json


def main() -> None:
    out = Path("results")
    out.mkdir(exist_ok=True)
    report = out / "benchmark_report.md"
    summary_path = out / "locust_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    else:
        summary = {
            "latency_ms": {"p50": "n/a", "p95": "n/a", "p99": "n/a"},
            "throughput_rps": "n/a",
            "error_rate_percent": "n/a",
            "scenario_counts": {"create_orders": 0, "cache_hit_reads": 0, "status_updates": 0},
        }

    broker_comparison = [
        {"broker": "Redis", "role": "cache/rate-limit", "strength": "lowest-latency reads"},
        {"broker": "RabbitMQ", "role": "task queue", "strength": "reliable ACK/NACK + DLQ"},
        {"broker": "Kafka", "role": "event stream", "strength": "high-throughput replay"},
        {"broker": "NATS", "role": "realtime pub/sub", "strength": "low-latency fan-out"},
    ]

    lines = [
        "# Benchmark Report",
        "",
        "## API latency and throughput",
        f"- p50 latency: {summary['latency_ms']['p50']} ms",
        f"- p95 latency: {summary['latency_ms']['p95']} ms",
        f"- p99 latency: {summary['latency_ms']['p99']} ms",
        f"- throughput: {summary['throughput_rps']} req/sec",
        f"- error rate: {summary['error_rate_percent']}%",
        "",
        "## Scenario execution counters",
        f"- create_orders: {summary['scenario_counts']['create_orders']}",
        f"- cache_hit_reads: {summary['scenario_counts']['cache_hit_reads']}",
        f"- status_updates: {summary['scenario_counts']['status_updates']}",
        "",
        "## Broker comparison",
    ]
    for item in broker_comparison:
        lines.append(f"- {item['broker']}: {item['role']} ({item['strength']})")

    lines.extend(
        [
            "",
            "## Bottleneck hypotheses",
            "- Redis: watch hit-ratio drops under sustained writes.",
            "- RabbitMQ: monitor queue depth during status update spikes.",
            "- Kafka: watch producer linger/batch settings vs p99 latency.",
            "- NATS: monitor subscriber lag and reconnect churn.",
            "",
            "## Optimization recommendations",
            "- Increase DB pool and API workers when p95 > target SLA.",
            "- Keep cache-aside invalidation strict on status updates.",
            "- Scale workers horizontally; tune prefetch/consumer group parallelism.",
            "- Use Grafana dashboards (API latency, queue depth, error rate) during test windows.",
        ]
    )
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
