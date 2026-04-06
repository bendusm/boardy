# Create and Apply Migration

Создай Alembic миграцию и примени её.

## Steps

1. Проверь текущий статус миграций:
```bash
cd backend && alembic current
```

2. Создай новую миграцию (autogenerate из моделей):
```bash
cd backend && alembic revision --autogenerate -m "$ARGS"
```

3. Проверь созданный файл миграции в `backend/alembic/versions/`

4. Примени миграцию:
```bash
cd backend && alembic upgrade head
```

5. Подтверди успешное применение:
```bash
cd backend && alembic current
```

Если `$ARGS` не указан, спроси у пользователя описание миграции.
