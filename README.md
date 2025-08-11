# Dating App Starter (MVP)

Быстрый скелет для старта приложения знакомств: FastAPI + Postgres + Redis.
Это демо с in-memory логикой матчинга в API, чтобы быстро пощупать флоу.

## Быстрый старт
1. Скопируйте `.env.example` в `.env` и при необходимости измените значения.
2. Запустите:
   ```bash
   docker compose up --build
   ```
3. Откройте Swagger: http://localhost:8000/docs

## Что внутри
- `backend/` — FastAPI API (auth, profiles, candidates, swipes, matches, messages)
- `db/schema.sql` — минимальная схема Postgres
- `docs/` — PRD, API, модель данных, события аналитики

## Дальше
- Подключайте реальную БД через SQLAlchemy.
- Добавьте верификацию (liveness/face match) через внешнего провайдера.
- Перенесите матчинг в отдельный сервис и добавьте фичи совместимости.
