# API Guide

OpenAPI доступен по адресу `/docs` после запуска API.

Примеры:

```bash
curl -X POST http://localhost:8060/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":"c1","description":"new order","amount":12.5,"is_vip":false}'
```

```bash
curl -X GET "http://localhost:8060/orders?limit=20&offset=0"
```

```bash
curl -X GET http://localhost:8060/orders/<order_id>
```

```bash
curl -X PATCH http://localhost:8060/orders/<order_id>/status \
  -H "Content-Type: application/json" \
  -d '{"status":"processing"}'
```

```bash
curl -X DELETE http://localhost:8060/orders/<order_id>
```

```bash
curl -X GET http://localhost:8060/health
```

```bash
curl -X GET http://localhost:8060/metrics
```

See also: `docs/api/websocket.md` for realtime contract.
