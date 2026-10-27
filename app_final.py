"""Expense Tracker — небольшой сервис для учёта личных расходов.

Основан на учебном примере app_final.py:
https://github.com/maximblaze/test_project_inf_course
"""

import logging
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "Expense Tracker")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
CURRENCY = os.getenv("CURRENCY", "RUB")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("expense_tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s v%s (currency=%s, log_level=%s)",
        APP_NAME, APP_VERSION, CURRENCY, LOG_LEVEL,
    )
    yield
    logger.info("Shutting down %s", APP_NAME)


app = FastAPI(title=APP_NAME, version=APP_VERSION, lifespan=lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1f ms)",
        request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


class ExpenseIn(BaseModel):
    amount: float = Field(gt=0, description="Сумма расхода, больше 0")
    category: str = Field(min_length=1, max_length=50)
    description: str | None = Field(default=None, max_length=200)


class Expense(ExpenseIn):
    id: int


# Хранилище в памяти: данные сбрасываются при перезапуске сервиса.
expenses: dict[int, Expense] = {}
next_id = 1


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "description": "Учёт личных расходов по категориям",
        "currency": CURRENCY,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": APP_VERSION}


@app.post("/expenses", status_code=201)
def create_expense(data: ExpenseIn) -> Expense:
    global next_id
    expense = Expense(id=next_id, **data.model_dump())
    expenses[expense.id] = expense
    next_id += 1
    logger.info(
        "Created expense id=%s amount=%s category=%s",
        expense.id, expense.amount, expense.category,
    )
    return expense


@app.get("/expenses")
def list_expenses(category: str | None = None) -> list[Expense]:
    if category is None:
        return list(expenses.values())
    return [e for e in expenses.values() if e.category.lower() == category.lower()]


def find_expense(expense_id: int) -> Expense:
    if expense_id not in expenses:
        logger.warning("Expense %s not found", expense_id)
        raise HTTPException(status_code=404, detail=f"Расход {expense_id} не найден")
    return expenses[expense_id]


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int) -> Expense:
    return find_expense(expense_id)


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    find_expense(expense_id)
    del expenses[expense_id]
    logger.info("Deleted expense id=%s", expense_id)
    return {"deleted": expense_id}
