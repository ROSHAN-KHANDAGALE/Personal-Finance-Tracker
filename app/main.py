from fastapi import FastAPI

from app.db.database import engine
from app.db.models import Base
from app.routes import transactions, debts, planner, user, budgets, recurring, wallets

app = FastAPI(title="Personal Finance Manager")

Base.metadata.create_all(bind=engine)

app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(planner.router)
app.include_router(user.router)
app.include_router(budgets.router)
app.include_router(recurring.router)
app.include_router(wallets.router)

@app.get("/")
def root():
    return {"status": "Money Manager backend running"}
