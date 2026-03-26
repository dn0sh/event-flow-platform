from prometheus_client import Counter, Gauge, Histogram

orders_created_total = Counter("orders_created_total", "Total created orders")
order_status_updates_total = Counter("order_status_updates_total", "Total status updates")
order_processing_seconds = Histogram("order_processing_seconds", "Order processing latency")
queue_depth_gauge = Gauge("queue_depth", "Current queue depth", ["queue_name"])
error_rate_total = Counter("error_rate_total", "Total errors", ["service"])
