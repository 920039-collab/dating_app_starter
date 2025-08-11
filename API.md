# API (MVP)
Базовые эндпоинты (см. также Swagger):
- POST /auth/signup
- POST /auth/signin
- GET  /profiles/me
- PUT  /profiles/me
- GET  /candidates?limit=10
- POST /swipe {target_user_id, action: like|pass}
- GET  /matches
- POST /messages
- GET  /messages/{peer_id}
Авторизация — через заголовок `Authorization: Bearer <token>`.
