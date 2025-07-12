# Complaint System API

## Установка
1. Создать виртуальное окружение: `python -m venv venv`
2. Активировать окружение: `source venv/bin/activate` (Linux/Mac) или `venv\Scripts\activate` (Windows)
3. Установить зависимости: `pip install -r requirements.txt`
4. Создать файл `.env` по примеру `.env.example`

## Запуск
`uvicorn app.main:app --reload`

## Пример запроса
```bash
curl -X POST "http://localhost:8000/complaints/" \
-H "Content-Type: application/json" \
-d '{"text":"Не приходит SMS-код"}'
