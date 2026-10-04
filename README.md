# NeuroQuest

Образовательная квест платформа для детей 

## Stack

- React + TypeScript
- FastAPI
- PostgreSQL
- Docker

## Запуск локально (Windows, без Docker)

Если Docker Desktop/WSL недоступен или барахлит, Postgres можно поставить
нативно — это даже проще.

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