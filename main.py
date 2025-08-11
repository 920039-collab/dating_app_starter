from fastapi import FastAPI

# Создаём приложение FastAPI
app = FastAPI(
    title="Dating API",
    description="Пример API для теста деплоя на Render",
    version="1.0.0"
)

# Корневой маршрут для проверки
@app.get("/")
def root():
    return {"message": "API is working!"}

# Пример тестового маршрута
@app.get("/ping")
def ping():
    return {"message": "pong"}

# Если запуск локально (не на Render)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
