# ADR 001: Redis Caching

## Статус
accepted

## Контекст
`GET /orders/{id}` является самым частым read-path. При росте трафика прямые чтения из PostgreSQL увеличивают p95 latency и нагрузку на БД.

## Решение
Использовать Redis как cache-aside:
- ключ `order:<id>`;
- TTL 300 секунд;
- invalidate на `PATCH /orders/{id}/status` и `DELETE /orders/{id}`.

## Последствия
- Существенное снижение latency для hot keys.
- Риск короткой устарелости данных между записью и invalidation.
- Необходим мониторинг hit ratio и memory eviction.

## Альтернативы
- Только SQL-оптимизация и индексы.
- In-memory cache в API инстансах (плохо масштабируется горизонтально).
