# WebSocket Contract

Endpoint: `GET /ws/notifications?token=<JWT>`

## Auth
- JWT обязателен в query-параметре `token`.
- При невалидном/отсутствующем токене сервер закрывает соединение с кодом `1008`.

## Room subscriptions
Клиент отправляет JSON-сообщения:

```json
{"action":"subscribe","order_id":"<order_id>"}
```

```json
{"action":"unsubscribe","order_id":"<order_id>"}
```

## Heartbeat
- Клиент отправляет `ping`
- Сервер отвечает `pong`

## Auto-reconnect (клиентский контракт)
1. При обрыве ждать backoff: 1s, 2s, 4s, 8s (max 10s).
2. Переоткрыть соединение с тем же JWT.
3. Повторно отправить все `subscribe` для нужных `order_id`.
4. При `1008` запрашивать новый JWT перед reconnect.
