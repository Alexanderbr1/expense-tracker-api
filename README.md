# Expense Tracker API

[![CI](https://github.com/Alexanderbr1/expense-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Alexanderbr1/expense-tracker-api/actions/workflows/ci.yml)

Небольшой сервис на FastAPI для учёта личных расходов: добавление расходов,
просмотр с фильтром по категории, удаление и сводная статистика по категориям.

**Для кого:** для тех, кто хочет вести простой учёт трат через HTTP API
(из скрипта, Postman или Swagger UI), а также как учебный пример полного пути
сервиса: код → Git → тесты → CI → запуск и диагностика.

Данные хранятся в памяти процесса и сбрасываются при перезапуске — база данных
не нужна.

## Источник и доработки

Основа — учебный пример `app_final.py` из репозитория
https://github.com/maximblaze/test_project_inf_course

Что изменено и добавлено:

- своя тема — учёт расходов;
- новые маршруты `/expenses` и `/stats` с собственной логикой;
- параметры пути (`/expenses/{expense_id}`) и запроса (`?category=`);
- проверка входных данных (сумма больше 0, ограничения длины строк);
- настройки через переменные окружения (`APP_NAME`, `APP_VERSION`, `CURRENCY`, `LOG_LEVEL`);
- логи запуска, каждого запроса и событий приложения;
- собственные тесты и CI с публикацией artifact.

## Маршруты

| Метод | Путь | Описание |
|---|---|---|
| GET | `/` | Название сервиса, валюта, ссылка на документацию |
| GET | `/health` | Проверка работоспособности: `{"status": "ok"}` |
| GET | `/version` | Версия приложения |
| POST | `/expenses` | Добавить расход, ответ `201` |
| GET | `/expenses?category=food` | Список расходов, фильтр по категории необязателен и не зависит от регистра |
| GET | `/expenses/{expense_id}` | Расход по id, `404` если не найден |
| DELETE | `/expenses/{expense_id}` | Удалить расход, `404` если не найден |
| GET | `/stats` | Количество, общая сумма и суммы по категориям |

Пример тела для `POST /expenses`:

```json
{"amount": 350.5, "category": "food", "description": "Обед"}
```

`amount` — число больше 0, `category` — от 1 до 50 символов,
`description` — необязательно, до 200 символов. Неверные данные → `422`.

## Установка

Нужен Python 3.12 (подойдёт и 3.10+).

```bash
git clone https://github.com/Alexanderbr1/expense-tracker-api.git
cd expense-tracker-api

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

python -m pip install -r requirements.txt       # только для запуска
python -m pip install -r requirements-dev.txt   # для запуска и тестов

cp .env.example .env               # необязательно: свои настройки
```

## Запуск

Обычный запуск (без `--reload`):

```bash
python -m uvicorn app_final:app --host 127.0.0.1 --port 8000
```

Режим разработки — сервер перезапускается при изменении кода:

```bash
python -m uvicorn app_final:app --reload
```

После запуска:

- приложение: http://127.0.0.1:8000
- интерактивная документация (Swagger UI): http://127.0.0.1:8000/docs

Остановить сервер — `Ctrl+C`.

## Тесты

```bash
python -m pytest -v
```

Тесты проверяют `/health`, `/version`, `/`, создание и получение расхода,
фильтр по категории, ошибки `404` и `422`, удаление и `/stats`.

## Переменные окружения

Читаются из окружения или из файла `.env` (шаблон — `.env.example`).
Все необязательны.

| Переменная | По умолчанию | Назначение |
|---|---|---|
| `APP_NAME` | `Expense Tracker` | Название сервиса в `/` и `/docs` |
| `APP_VERSION` | `0.1.0` | Версия в `/version` |
| `CURRENCY` | `RUB` | Валюта в `/` и `/stats` |
| `LOG_LEVEL` | `INFO` | Уровень логов: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

Пример запуска с другими настройками:

```bash
APP_VERSION=1.2.3 CURRENCY=USD python -m uvicorn app_final:app --port 8000
```

Файл `.env` с настоящими значениями в репозиторий не добавляется (он в `.gitignore`).

## Проверка работы

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}

curl http://127.0.0.1:8000/version
# {"version":"0.1.0"}

curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"amount": 350.5, "category": "food", "description": "Обед"}'
# {"amount":350.5,"category":"food","description":"Обед","id":1}

curl "http://127.0.0.1:8000/expenses?category=food"
curl http://127.0.0.1:8000/stats
```

## Логи

Логи выводятся в консоль, в которой запущен uvicorn. Формат строк приложения:
`время | уровень | сообщение`.

```
2026-10-27 21:09:36,870 | INFO | Starting Expense Tracker v0.1.0 (currency=RUB, log_level=INFO)
2026-10-27 21:09:37,044 | INFO | Created expense id=1 amount=350.5 category=Food
2026-10-27 21:09:37,044 | INFO | POST /expenses -> 201 (1.0 ms)
2026-10-27 21:09:37,053 | WARNING | Expense 99 not found
2026-10-27 21:09:37,053 | INFO | GET /expenses/99 -> 404 (0.5 ms)
```

Что пишется в лог:

- запуск и остановка сервиса с текущими настройками;
- каждый запрос: метод, путь, код ответа, время обработки;
- создание и удаление расхода, запрос статистики;
- попытка обратиться к несуществующему расходу (`WARNING`).

Рядом выводятся стандартные строки uvicorn вида `INFO: 127.0.0.1 - "GET /health HTTP/1.1" 200 OK`.

Сохранить логи в файл и смотреть их в реальном времени:

```bash
python -m uvicorn app_final:app --port 8000 2>&1 | tee app.log
tail -f app.log          # в другом терминале
```

## Диагностика

| Симптом | Причина и решение |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | Не активировано окружение или не установлены зависимости: `source .venv/bin/activate`, затем `python -m pip install -r requirements-dev.txt` |
| `[Errno 48] Address already in use` (Windows: `10048`) | Порт 8000 занят. Запустите на другом: `--port 8001`, или найдите процесс: `lsof -i :8000` |
| `Error loading ASGI app. Could not import module "app_final"` | Команда запущена не из папки проекта — перейдите в папку с `app_final.py` |
| `curl: (7) Failed to connect` к `/health` | Сервер не запущен или слушает другой порт/адрес — проверьте консоль uvicorn и строку `Uvicorn running on ...` |
| `/version` показывает не ту версию | Проверьте `APP_VERSION` в окружении и в `.env`; после изменения перезапустите сервер |
| Расходы пропали | Данные хранятся в памяти и сбрасываются при перезапуске — это ожидаемое поведение |
| Нужно больше подробностей в логах | Запустите с `LOG_LEVEL=DEBUG` |
| CI упал на шаге `Run tests` | Запустите `python -m pytest -v` локально, исправьте ошибку и сделайте push |

Быстрая проверка, что всё в порядке:

```bash
python -m pytest -v && curl -s http://127.0.0.1:8000/health
```

## CI

Workflow `.github/workflows/ci.yml` запускается при каждом `push` и `pull_request`
в ветку `main`:

1. `test` — устанавливает зависимости и запускает `python -m pytest -v`;
2. `package` — только после успешных тестов публикует artifact `expense-tracker`
   с файлами `app_final.py`, `requirements.txt`, `README.md`, `.env.example`.

Artifact можно скачать на странице запуска во вкладке **Actions** → нужный запуск →
раздел **Artifacts**. Хранится 7 дней.
