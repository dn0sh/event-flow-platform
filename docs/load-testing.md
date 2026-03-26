# Нагрузочное тестирование (Locust) и бенчмарк

## Зачем

Проверка задержек и пропускной способности HTTP API при множестве одновременных клиентов. Отчёт Locust показывает RPS, процент ошибок и перцентили времени ответа.

## Предусловия

1. Стек запущен, API доступен на `http://localhost:8060` (после `up`, миграций и при необходимости `seed`).
2. **Rate limiting:** middleware считает запросы **на IP**. Все пользователи Locust с хоста идут с **одного адреса** → при стандартном лимите (`RATE_LIMIT_PER_MINUTE=100`) быстро наступает **HTTP 429** и Locust показывает почти 100% «failures».

### Избежать 429 при нагрузочном прогоне

В `.env`:

```env
RATE_LIMIT_PER_MINUTE=0
```

Значение **`0` отключает** лимит (см. `src/api/middleware/rate_limiter.py`). Перезапустите контейнер API, чтобы подтянуть переменные:

```powershell
.\scripts\task.ps1 up -d api
```

После теста в продакшене верните разумный лимит (например `100`).

## Запуск

```powershell
.\scripts\task.ps1 load-test
```

По умолчанию: [Locust](https://locust.io/) headless, **50** пользователей, набор **10**/с, длительность **2** минуты, `--host http://localhost:8060`. Свои параметры:

```powershell
.\scripts\task.ps1 load-test -- --headless -u 20 -r 5 -t 1m --host http://localhost:8060
```

Скрипт: [`scripts/load_test.py`](../scripts/load_test.py).

## Как устроен сценарий

| Вес | Задача | Описание |
|-----|--------|----------|
| 2 | `POST /orders` | Создание заказов до глобального потолка **`TARGET_CREATE_TOTAL` (1000)** |
| 9 | `GET /orders/:id` | Чтение случайного из уже созданных (уклон в cache-aside / Redis) |
| 3 | `PATCH /orders/:id/status` | Смена статуса по циклу `processing` → `completed` → `cancelled` |

Пока список созданных ID пуст, часть воркеров бьёт в `GET /orders`.

**Ожидаемая картина в отчёте:**

- Запросов **`GET /orders/:id`** больше всего (вес 9 и кэшируемые чтения).
- **`POST /orders`** стабилизируется около **1000–1001** успешных созданий за прогон (лимит в коде сценария).
- При **`RATE_LIMIT_PER_MINUTE=0`**: **0% failures**, код выхода **0**.
- При включённом лимите: массовые **429 Too Many Requests** — это ограничение middleware, а не «падение» приложения.

## Отчёт `benchmark.py`

После прогона Locust можно сгенерировать сводку:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark.py
```

Файл: **`results/benchmark_report.md`** (латентность p50/p95/p99, RPS, счётчики сценария, гипотезы узких мест). Цифры соответствуют финальной статистике последнего запуска Locust (через общий механизм в `load_test.py` / `events.quitting`).

## Кодировка консоли (Windows)

Строка-подсказка в `task.ps1` перед Locust выводится **латиницей**, чтобы в классическом PowerShell не было искажения кириллицы (UTF-8 без BOM).

## Связанные настройки

- `RATE_LIMIT_PER_MINUTE` — [`README.md`](../README.md) (безопасность), [`.env.example`](../.env.example).
