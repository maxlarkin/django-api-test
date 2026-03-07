# Django API

## Запуск
### Запуск venv и установка зависимостей
```bash
python -m venv venv
. venv/scripts/activate
pip install -r requirements.txt
```

### Миграции django и запуск сервера
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

## Использование
### Отправка письма (Работает только с английским языком, потому что curl)
```bash
curl -X POST http://localhost:8000/api/emails/ \
  -H "Content-Type: application/json" \
  -d "{
    \"sender\": \"alice@example.com\",
    \"recipient\": \"bob@example.com\",
    \"subject\": \"test letter\",
    \"body\": \"test message\"
  }"
```

### Получение писем в папке ('inbox', 'sent', 'archive', 'trash')
```bash
curl -X GET "http://localhost:8000/api/emails/?folder=inbox"
```

### Получение письма
```bash
curl -X GET http://localhost:8000/api/emails/1/
```

### Перемещение письма в другую папку ('inbox', 'sent', 'archive', 'trash')
```bash
curl -X PATCH http://localhost:8000/api/emails/1/move/ \
  -H "Content-Type: application/json" \
  -d '{"folder": "archive"}'
```

### Удаление письма
```bash
curl -X DELETE http://localhost:8000/api/emails/1/
```