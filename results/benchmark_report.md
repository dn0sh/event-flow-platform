# Benchmark Report

## API latency and throughput
- p50 latency: 7 ms
- p95 latency: 120.0 ms
- p99 latency: 210.0 ms
- throughput: 314.97 req/sec
- error rate: 0.0%

## Scenario execution counters
- create_orders: 1001
- cache_hit_reads: 27300
- status_updates: 9167

## Broker comparison
- Redis: cache/rate-limit (lowest-latency reads)
- RabbitMQ: task queue (reliable ACK/NACK + DLQ)
- Kafka: event stream (high-throughput replay)
- NATS: realtime pub/sub (low-latency fan-out)

## Bottleneck hypotheses
- Redis: watch hit-ratio drops under sustained writes.
- RabbitMQ: monitor queue depth during status update spikes.
- Kafka: watch producer linger/batch settings vs p99 latency.
- NATS: monitor subscriber lag and reconnect churn.

## Optimization recommendations
- Increase DB pool and API workers when p95 > target SLA.
- Keep cache-aside invalidation strict on status updates.
- Scale workers horizontally; tune prefetch/consumer group parallelism.
- Use Grafana dashboards (API latency, queue depth, error rate) during test windows.
