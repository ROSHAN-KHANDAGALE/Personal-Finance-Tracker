from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import List
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.models import Budget, BudgetCategory, Transaction
from app.schemas.budget import (
    BudgetCreate,
    BudgetResponse,
    BudgetSummary,
    BudgetCategorySummary,
)


def create_budget(
    db: Session,
    user_id: UUID,
    payload: BudgetCreate,
) -> Budget:
    existing = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.year == payload.year,
            Budget.month == payload.month,
        )
        .first()
    )
    if existing:
        raise ValueError("Budget for this month already exists")

    budget = Budget(
        user_id=user_id,
        name=payload.name,
        year=payload.year,
        month=payload.month,
    )
    db.add(budget)
    db.flush()  # ensure budget.id is available

    for cat in payload.categories:
        db.add(
            BudgetCategory(
                budget_id=budget.id,
                category=cat.category,
                limit_amount=cat.limit_amount,
            )
        )

    db.commit()
    db.refresh(budget)
    return budget


def list_budgets(db: Session, user_id: UUID) -> List[Budget]:
    return (
        db.query(Budget)
        .filter(Budget.user_id == user_id)
        .order_by(Budget.year.desc(), Budget.month.desc())
        .all()
    )


def _get_budget_or_none(
    db: Session,
    user_id: UUID,
    budget_id: UUID,
) -> Budget | None:
    return (
        db.query(Budget)
        .filter(
            Budget.id == budget_id,
            Budget.user_id == user_id,
        )
        .first()
    )


def get_budget_summary(
    db: Session,
    user_id: UUID,
    budget_id: UUID,
) -> BudgetSummary | None:
    budget = _get_budget_or_none(db, user_id, budget_id)
    if not budget:
        return None

    start_day = date(budget.year, budget.month, 1)
    last_day = monthrange(budget.year, budget.month)[1]
    end_day = date(budget.year, budget.month, last_day)

    rows = (
        db.query(
            Transaction.category,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "Expense",
            Transaction.date >= start_day,
            Transaction.date <= end_day,
        )
        .group_by(Transaction.category)
        .all()
    )
    spent_by_category = {row[0]: Decimal(str(row[1])) for row in rows}

    category_summaries: List[BudgetCategorySummary] = []
    total_limit = Decimal("0")
    total_spent = Decimal("0")

    for cat in budget.categories:
        limit_amount = Decimal(str(cat.limit_amount))
        spent = spent_by_category.get(cat.category, Decimal("0"))
        remaining = limit_amount - spent
        utilization = float(spent / limit_amount * 100) if limit_amount > 0 else 0.0

        total_limit += limit_amount
        total_spent += spent

        category_summaries.append(
            BudgetCategorySummary(
                category=cat.category,
                limit_amount=limit_amount,
                spent=spent,
                remaining=remaining,
                utilization_percent=round(utilization, 2),
            )
        )

    total_remaining = total_limit - total_spent

    budget_response = BudgetResponse.model_validate(budget)

    return BudgetSummary(
        budget=budget_response,
        categories=category_summaries,
        total_limit=total_limit,
        total_spent=total_spent,
        total_remaining=total_remaining,
    )


def update_budget(
    db: Session,
    user_id: UUID,
    budget_id: UUID,
    payload: BudgetCreate,
) -> Budget | None:
    budget = _get_budget_or_none(db, user_id, budget_id)
    if not budget:
        return None

    budget.name = payload.name
    budget.year = payload.year
    budget.month = payload.month

    db.query(BudgetCategory).filter(
        BudgetCategory.budget_id == budget.id
    ).delete()

    for cat in payload.categories:
        db.add(
            BudgetCategory(
                budget_id=budget.id,
                category=cat.category,
                limit_amount=cat.limit_amount,
            )
        )

    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def delete_budget(
    db: Session,
    user_id: UUID,
    budget_id: UUID,
) -> bool:
    budget = _get_budget_or_none(db, user_id, budget_id)
    if not budget:
        return False

    db.delete(budget)
    db.commit()
    return True

