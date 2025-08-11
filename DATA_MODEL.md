# Модель данных (описание)
- users(id, phone, password_hash, display_name, created_at)
- profiles(user_id, bio, interests[], gender, looking_for, city, birthdate, verified, ...)
- likes(from_user, to_user, created_at)
- matches(a, b, created_at)
- messages(id, from_user, to_user, text, created_at)

Связи:
- 1:1 users ↔ profiles
- N:M users ↔ users через likes; matches — симметричная пара (a<b)
