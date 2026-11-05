# NeuroQuest

Образовательная квест платформа для детей 

## Stack

- React + TypeScript
- FastAPI
- PostgreSQL
- Docker

## Документация

- [`WINDOWS_SETUP.md`](WINDOWS_SETUP.md) — полный запуск на Windows от нуля, с разбором типичных ошибок
- [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md) — архитектура, API, состояние проекта, ограничения, планы
- [`CONTENT_SOURCES.md`](CONTENT_SOURCES.md) — откуда взят игровой контент и какие решения по нему приняты
- [`tools/browser-checks`](tools/browser-checks/README.md) — проверки интерфейса в реальном браузере (сценарий, мобильная вёрстка, скриншоты)

## Запуск локально (Windows, без Docker)

Основной сценарий и тот, на котором всё проверялось: Postgres ставится
нативно, Docker не нужен. (Запуск в Docker описан ниже, но образы ни разу не
собирались.)

**1. PostgreSQL**
Поставь [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
(ставится вместе с pgAdmin). В pgAdmin создай:
- роль-пользователя `neuroquest` с паролем `neuroquest` (Login/Group Roles →
  Create, на вкладке Privileges включить "Can login?")
- базу `neuroquest` с владельцем `neuroquest`
- (опционально, только для запуска тестов) ещё базу `neuroquest_test`,
  тот же владелец

**2. Backend**
```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.content.seed
uvicorn app.main:app --reload
```
Оставь это окно терминала открытым — сервер работает, пока оно не закрыто.
При следующих запусках venv нужно активировать заново (`venv\Scripts\Activate.ps1`)
перед каждой командой.

> Если на `alembic upgrade head` вылетает `WinError 64` /
> `ConnectionDoesNotExistError` — это известный баг связки asyncpg +
> Windows (ProactorEventLoop). Код уже содержит обход
> (`app/core/windows_compat.py`); если ошибка всё ещё есть — убедись, что
> `git pull` подтянул актуальный `main`.

**3. Frontend** (в новом окне терминала)
```powershell
cd frontend
npm install
copy .env.example .env
npm run dev
```
Открой http://localhost:5173, зайди в «Кабинет родителя» (/parent),
зарегистрируйся, добавь ребёнка, нажми «Играть на этом устройстве».

## Показ комиссии: весь сайт на одном порту + туннель

Сервер стоит дома, человек в другом городе открывает ссылку. Без Docker и без
второго порта: backend сам отдаёт собранный фронтенд.

```powershell
# 1. собрать фронтенд (адрес API в сборке — тот же origin, см. ниже)
cd frontend
npm run build

# 2. запустить один сервер на :8000 (окно оставить открытым)
cd ..\backend
venv\Scripts\Activate.ps1
$env:JWT_SECRET_KEY = "длинная-случайная-строка"
$env:FRONTEND_DIST = "..\frontend\dist"
$env:REGISTER_MAX_PER_IP = "1000"
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 3. в новом окне — туннель (cloudflared установлен отдельно)
cloudflared tunnel --url http://localhost:8000
```

`cloudflared` напечатает адрес вида `https://….trycloudflare.com` — его и
отправляй. Адрес **меняется при каждом запуске** туннеля; если нужны QR-коды
под этот адрес: `python -m scripts.generate_qr_codes https://….trycloudflare.com`.

Как это устроено:
- `FRONTEND_DIST` — папка со сборкой. Если задана, backend отдаёт файлы из неё,
  а любой путь, не найденный среди файлов и не начинающийся с `/api`, получает
  `index.html` (маршруты React). Неизвестный `/api/...` остаётся JSON-404.
  Если в папке нет `index.html`, сервер не стартует и говорит, что собрать.
- В продакшен-сборке адрес API по умолчанию — тот же origin. Пустую
  переменную окружения на Windows задать нельзя (она считается неустановленной),
  поэтому это сделано умолчанием в `client.ts`, а `frontend/.env.production`
  (пустой `VITE_API_URL=`) страхует от старого `frontend/.env` с
  `http://localhost:8000`: иначе этот адрес зашился бы в сборку и у
  посетителя сайт стучался бы на **его** localhost. Для `npm run dev`
  ничего не меняется.
- `REGISTER_MAX_PER_IP=1000`: через туннель все посетители могут приходить с
  одного адреса (с адреса `cloudflared`), и лимит 10 регистраций в час на
  всех закончился бы на втором человеке. Лимит **входа** (20 неудач на IP) тоже
  общий в этом случае — для показа это допустимо.
- Компьютер не должен засыпать, окно с `uvicorn` и туннель должны работать.
- Quick tunnel — для показа, не для постоянной работы.

## Лимит регистрации

`POST /api/auth/register`: не больше 10 попыток в час с одного IP
(`REGISTER_MAX_PER_IP`, `REGISTER_RATE_LIMIT_WINDOW_SECONDS`, по умолчанию 10 и
3600). Считаются **все** попытки, дошедшие до обработчика, включая `409` (так
нельзя бесплатно перебирать, какие email уже есть). Запросы с невалидным телом
(`422`) попытку не тратят. Отказ — `429` с заголовком `Retry-After`; сам отказ
в счёт не идёт. Хранится в памяти процесса (как лимит входа). Во фронтенде на
`429` показывается сообщение с временем ожидания.

## Docker (опционально; образы не собирались)

> **Не проверено:** `Dockerfile`-ы, `nginx.conf` и `docker-compose.yml` написаны,
> но `docker build` / `docker compose up` ни разу не запускались. Проверены
> по отдельности: скрипт запуска backend (отказы и старт), синтаксис nginx и
> его проксирование на живой backend, YAML compose.

Только Postgres (для разработки, как раньше): `docker compose up -d`.
Всё приложение в контейнерах:

```powershell
copy .env.example .env        # задать JWT_SECRET_KEY (инструкция в файле)
docker compose --profile app up -d --build
```

Сайт — на http://localhost:8080 (`WEB_PORT`). Что внутри:
- `backend` отказывается стартовать без `JWT_SECRET_KEY`, с публичным dev-значением
  и со значением короче 32 символов; затем `alembic upgrade head`, загрузка
  контента, uvicorn. Порт наружу не публикуется — только nginx внутри сети compose.
- `frontend` — nginx со сборкой; `/api/` проксирует на backend и **перезаписывает**
  `X-Forwarded-For` адресом клиента, чтобы подставленный клиентом заголовок не
  обходил лимиты. Если перед этим nginx стоит ещё один прокси/туннель, все
  посетители увидят один IP — см. `REGISTER_MAX_PER_IP` выше.
- `.gitattributes` держит окончания строк LF (иначе скрипт с CRLF не
  запустится в контейнере).

## Печатные материалы (QR-коды карточек и миссий)

```bash
cd backend
python -m scripts.generate_qr_codes [base_url]   # default: http://localhost:5173
```

Генерирует QR-коды и заготовки лицевой стороны карточек в
`backend/print_assets/{qr,cards}/` для всех карточек квеста и конвертов с
миссиями, читая актуальный контент прямо из БД. Для прода запусти с
реальным доменом фронтенда, например:
`python -m scripts.generate_qr_codes https://neuroquest.example.com`.