from fastapi import FastAPI
from routers import chat_router, tts_router

app = FastAPI()

app.include_router(chat_router)

app.include_router(tts_router)

# uvicorn main:app --port 7788