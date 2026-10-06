# Запуск NeuroQuest локально на Windows 10/11

Полная инструкция от нуля до работающего приложения в браузере. Docker
не нужен — PostgreSQL ставится напрямую, это оказалось проще и надёжнее
(Docker Desktop на Windows нередко падает с ошибками WSL вроде
`ERROR_NO_SYSTEM_RESOURCES`).

## Что нужно скачать заранее

| Программа | Откуда | Зачем |
|---|---|---|
| Git | [git-scm.com](https://git-scm.com/downloads) | скачать код проекта |
| Python 3.12+ | [python.org/downloads](https://www.python.org/downloads/) | backend |
| Node.js 20+ | [nodejs.org](https://nodejs.org/) | frontend |
| PostgreSQL 16/17 | [postgresql.org/download/windows](https://www.postgresql.org/download/windows/) | база данных (ставится вместе с pgAdmin) |

При установке Python **обязательно отметь галочку "Add python.exe to PATH"**
на первом экране установщика.

При установке PostgreSQL установщик попросит задать пароль для
пользователя `postgres` — запомни его, он понадобится один раз при
создании роли и базы (шаг 2).

---

## Шаг 1. Скачать проект

Открой PowerShell и выполни:

```powershell
git clone https://github.com/KimDmitriyR/NeuroQuest.git
cd NeuroQuest
```

---

## Шаг 2. Настроить базу данных через pgAdmin

pgAdmin ставится автоматически вместе с PostgreSQL, ищи его в меню Пуск.

1. Открой pgAdmin → слева в дереве разверни **Servers → PostgreSQL 17**
   (или 16). При первом подключении попросит пароль — тот, что задавал
   при установке. Сохрани его, чтобы не вводить каждый раз.
2. Правый клик на **Login/Group Roles → Create → Login/Group Role**:
   - вкладка **General** → Name: `neuroquest`
   - вкладка **Definition** → Password: `neuroquest`
   - вкладка **Privileges** → включить **Can login?**
   - **Save**
3. Правый клик на **Databases → Create → Database**:
   - Database: `neuroquest`
   - Owner: `neuroquest` (выбрать из списка — ту роль, что только что создал)
   - **Save**
4. *(Нужно только если будешь запускать автотесты backend)* повтори шаг 3
   ещё раз с именем базы `neuroquest_test`, тот же владелец `neuroquest`.

---

## Шаг 3. Backend

В том же PowerShell (из папки `NeuroQuest`):

```powershell
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
```

Если PowerShell откажется выполнять скрипт активации с ошибкой про
execution policy — выполни один раз:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
ответь `Y` на вопрос и повтори `venv\Scripts\Activate.ps1`. В начале
строки терминала должно появиться `(venv)` — значит окружение активно.

Дальше (каждая команда отдельно, дожидаясь, пока предыдущая закончится
без ошибок):

```powershell
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.content.seed
```

`alembic upgrade head` создаёт таблицы в базе. `python -m app.content.seed`
загружает весь игровой контент — в выводе должны появиться строки
`loaded card: ...` для 12 карточек и `loaded mission: ...` для 3 миссий.

Запусти сервер:
```powershell
uvicorn app.main:app --reload
```
Должно появиться `Uvicorn running on http://127.0.0.1:8000`. **Это окно
терминала теперь нужно оставить открытым** — сервер работает, пока оно
не закрыто.

---

## Шаг 4. Frontend

Открой **новое** окно PowerShell (backend должен продолжать работать в
первом):

```powershell
cd NeuroQuest\frontend
npm install
copy .env.example .env
npm run dev
```

Должно появиться что-то вроде `Local: http://localhost:5173/`. Это окно
тоже оставь открытым.

---

## Шаг 5. Проверка в браузере

1. Открой **http://localhost:5173**
2. Внизу страницы нажми **«Кабинет родителя»**
3. Переключись на вкладку **«Регистрация»**, введи любой email и пароль
   (от 8 символов), поставь галочку согласия, нажми **«Создать аккаунт»**
4. В кабинете нажми **«+ Добавить ребёнка»**, введи имя
5. На карточке ребёнка нажми **«Играть на этом устройстве»**
6. На главной введи код карточки, например `finstartup-2-0-01`, нажми
   **«Начать квест»** — должен открыться чат с первым вопросом квеста

Если дошёл до этого места и видишь текст квеста с вариантами ответа —
всё настроено верно.

---

## Как перезапустить в другой день

Оба сервера (backend и frontend) нужно поднимать заново при каждой
перезагрузке компьютера — Postgres как служба Windows запускается
автоматически, а вот сами серверы проекта — нет.

```powershell
# окно 1
cd NeuroQuest\backend
venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# окно 2
cd NeuroQuest\frontend
npm run dev
```

---

## Решение проблем

**`alembic` / `uvicorn` / `npm` "не является внутренней или внешней командой"**
Забыл активировать venv (`venv\Scripts\Activate.ps1`) перед командой backend,
либо не установил Node.js для команд frontend.

**При `pip install` пишет "script ... is not on PATH"**
Безвредное предупреждение, если работаешь внутри активированного venv —
просто убедись, что видишь `(venv)` в начале строки терминала.

**`alembic upgrade head` падает с `WinError 64` /
`ConnectionDoesNotExistError: connection was closed in the middle of operation`**
Известный баг связки asyncpg + Windows. В коде уже есть обход
(`backend/app/core/windows_compat.py`) — убедись, что сделал `git pull`
и подтянул свежий `main`.

**`sqlalchemy.exc.OperationalError` / не может подключиться к базе**
Скорее всего в pgAdmin не создана роль `neuroquest` и/или база `neuroquest`
(шаг 2), либо PostgreSQL слушает не порт 5432 — проверить: правый клик на
сервере в pgAdmin → Properties → Connection → Port, и при необходимости
поправить порт в `backend/.env` в строке `DATABASE_URL`.

**Docker Desktop падает с `ERROR_NO_SYSTEM_RESOURCES` / ошибками WSL**
Эта инструкция Docker не использует вообще, можно игнорировать. Если
Docker всё же нужен для чего-то другого — помогает полная перезагрузка
компьютера, `wsl --update` и `wsl --shutdown` из PowerShell от имени
администратора.

**Страница открывается, но запросы к серверу не проходят (ошибки в
консоли браузера про CORS или Failed to fetch)**
Проверь, что окно с backend (`uvicorn`) всё ещё открыто и не выдало
ошибку, и что в `frontend/.env` указано
`VITE_API_URL=http://localhost:8000` — ровно тот адрес, на котором
поднялся backend.

Если ошибка не из этого списка — пришли полный текст ошибки из
терминала (или консоли браузера, клавиша F12 → вкладка Console).
