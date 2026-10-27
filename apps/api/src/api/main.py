from jinja2.sandbox import MAX_RANGE
import os
from starlette.middleware.sessions import SessionMiddleware
from api.auth import router as auth_router
from fastapi import FastAPI
from sqlalchemy import text
from api.db import engine
from api.exams import router as exams_router
from api.attempts import router as attempts_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ["SESSION_SECRET"],
    session_cookie="learning_session",
    max_age=24*60*60,
    same_site="lax",
    https_only=False,
)

app.include_router(auth_router)
app.include_router(exams_router)
app.include_router(attempts_router)

@app.get("/health")
def health() -> dict[str, str]:
    """APIが応答できることを確認する。"""
    return {"status": "ok"}

@app.get("/health/db")
def database_health() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {"database": "ok"}
