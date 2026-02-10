from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user_id
from app.schemas.budget import BudgetCreate, BudgetResponse, BudgetSummary
from app.services import budget_service


router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get(
    "/",
    response_model=list[BudgetResponse],
    status_code=status.HTTP_200_OK,
)
def list_budgets(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    return budget_service.list_budgets(db, user_id)


@router.post(
    "/",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    try:
        budget = budget_service.create_budget(db, user_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return budget


@router.get(
    "/{budget_id}",
    response_model=BudgetSummary,
    status_code=status.HTTP_200_OK,
)
def get_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    summary = budget_service.get_budget_summary(db, user_id, budget_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )
    return summary


@router.put(
    "/{budget_id}",
    response_model=BudgetResponse,
    status_code=status.HTTP_200_OK,
)
def update_budget(
    budget_id: UUID,
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    budget = budget_service.update_budget(db, user_id, budget_id, payload)
    if budget is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )
    return budget


@router.delete(
    "/{budget_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_budget(
    budget_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    ok = budget_service.delete_budget(db, user_id, budget_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found",
        )

