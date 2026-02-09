# app/routes/planner.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.services.planner_service import (
    calculate_financial_summary,
    run_financial_planner,
)
from app.services.debt_simulator import DebtItem, simulate_debt_clearance
from app.services.savings_planner import calculate_savings_plan

router = APIRouter(prefix="/planner", tags=["Planner"])


@router.get("/summary")
def get_financial_summary(db: Session = Depends(get_db)):
    return calculate_financial_summary(db)


@router.get("/debt-plan")
def get_debt_plan(
    reserved_cash: float = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    summary = calculate_financial_summary(db)

    free_cash = summary["free_cash"]
    usable_cash = max(free_cash - reserved_cash, 0)

    debt_items = []
    for d in db.query(models.Debt).all():
        debt_items.append(
            DebtItem(
                name=d.creditor_name,
                remaining=float(d.remaining_amount),
                emi=float(d.emi_amount) if d.emi_amount is not None else None,
                is_flexible=d.is_flexible,
                priority=d.priority,
            )
        )

    return simulate_debt_clearance(
        monthly_income=summary["total_income"],
        living_expenses=summary["living_expenses"],
        debts=debt_items,
    )


@router.get("/savings-plan")
def get_savings_plan(
    target_amount: float = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    summary = calculate_financial_summary(db)
    free_cash = summary["free_cash"]

    return calculate_savings_plan(db, free_cash, target_amount)


@router.get("/overview")
def planner_overview(db: Session = Depends(get_db)):
    return run_financial_planner(db)
