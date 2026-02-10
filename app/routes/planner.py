# app/routes/planner.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.dependencies import get_current_user_id
from app.schemas.planner import FinancialSummary, DebtPlanResponse
from app.services.planner_service import (
    calculate_financial_summary,
    run_financial_planner,
)
from app.services.debt_simulator import DebtItem, simulate_debt_clearance
from app.services.savings_planner import calculate_savings_plan

router = APIRouter(prefix="/planner", tags=["Planner"])


@router.get(
    "/summary",
    response_model=FinancialSummary,
)
def get_financial_summary(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Per-user financial summary.
    """
    return calculate_financial_summary(db, user_id=user_id)


@router.get(
    "/debt-plan",
    response_model=DebtPlanResponse,
)
def get_debt_plan(
    reserved_cash: float = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Run per-user debt clearance simulation.
    """
    summary = calculate_financial_summary(db, user_id=user_id)

    free_cash = summary["free_cash"]
    usable_cash = max(free_cash - reserved_cash, 0)

    debts = (
        db.query(models.Debt)
        .filter(models.Debt.user_id == user_id)
        .all()
    )

    debt_items: list[DebtItem] = []
    for d in debts:
        debt_items.append(
            DebtItem(
                name=d.creditor_name,
                remaining=float(d.remaining_amount),
                # Only non-flexible debts are treated as fixed EMI
                emi=float(d.emi_amount)
                if d.emi_amount is not None and not d.is_flexible
                else None,
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
    user_id=Depends(get_current_user_id),
):
    """
    Per-user savings planner using:
    monthly_saving_power = free_cash + total EMI.
    """
    summary = calculate_financial_summary(db, user_id=user_id)
    free_cash = summary["free_cash"]

    return calculate_savings_plan(
        db=db,
        user_id=user_id,
        free_cash=free_cash,
        target_amount=target_amount,
    )


@router.get("/overview")
def planner_overview(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Combined summary + debt plan for a single user.
    """
    return run_financial_planner(db, user_id=user_id)
