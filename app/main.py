from fastapi import FastAPI
from app.db.database import engine
from app.db.models import Base
from app.routes import transactions, debts, planner, user

app = FastAPI(title="Personal Finance Manager")

Base.metadata.create_all(bind=engine)

app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(planner.router)
app.include_router(user.router)

@app.get("/")
def root():
    return {"status": "Money Manager backend running"}
