"""Expense Tracker — небольшой сервис для учёта личных расходов.

Основан на учебном примере app_final.py:
https://github.com/maximblaze/test_project_inf_course
"""

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

load_dotenv()

APP_VERSION = "0.1.0"

app = FastAPI(title="Expense Tracker")


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


@app.post("/expenses", status_code=201)
def create_expense(data: ExpenseIn) -> Expense:
    global next_id
    expense = Expense(id=next_id, **data.model_dump())
    expenses[expense.id] = expense
    next_id += 1
    return expense


@app.get("/expenses")
def list_expenses(category: str | None = None) -> list[Expense]:
    if category is None:
        return list(expenses.values())
    return [e for e in expenses.values() if e.category.lower() == category.lower()]


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int) -> Expense:
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail=f"Расход {expense_id} не найден")
    return expenses[expense_id]


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    if expense_id not in expenses:
        raise HTTPException(status_code=404, detail=f"Расход {expense_id} не найден")
    del expenses[expense_id]
    return {"deleted": expense_id}
