"""Expense Tracker — небольшой сервис для учёта личных расходов.

Основан на учебном примере app_final.py:
https://github.com/maximblaze/test_project_inf_course
"""

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

APP_VERSION = "0.1.0"

app = FastAPI(title="Expense Tracker")


@app.get("/")
def root():
    return {
        "service": "Expense Tracker",
        "description": "Учёт личных расходов по категориям",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}
