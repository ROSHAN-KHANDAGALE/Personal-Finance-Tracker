from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.schemas.debt import DebtCreate, DebtResponse
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/debts", tags=["Debts"])


@router.get(
    "/",
    response_model=list[DebtResponse],
    status_code=status.HTTP_200_OK,
)
def get_debts(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    List debts for the current user only.
    """
    return (
        db.query(models.Debt)
        .filter(models.Debt.user_id == user_id)
        .all()
    )


@router.get(
    "/{debt_id}",
    response_model=DebtResponse,
    status_code=status.HTTP_200_OK,
)
def get_debt_by_id(
    debt_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Get a single debt, ensuring it belongs to the current user.
    """
    debt = (
        db.query(models.Debt)
        .filter(
            models.Debt.id == debt_id,
            models.Debt.user_id == user_id,
        )
        .first()
    )
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found",
        )
    return debt


@router.post(
    "/",
    response_model=DebtResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_debt(
    payload: DebtCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Create a debt for the current user.
    """
    debt = models.Debt(
        user_id=user_id,
        creditor_name=payload.creditor_name,
        total_amount=payload.total_amount,
        remaining_amount=payload.total_amount,
        emi_amount=payload.emi_amount,
        interest_rate=payload.interest_rate,
        is_flexible=payload.is_flexible,
        priority=payload.priority,
        status="active",
    )

    db.add(debt)
    db.commit()
    db.refresh(debt)

    return debt


@router.put(
    "/{debt_id}",
    response_model=DebtResponse,
    status_code=status.HTTP_200_OK,
)
def update_debt(
    debt_id: UUID,
    payload: DebtCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Update a debt owned by the current user.
    """
    debt = (
        db.query(models.Debt)
        .filter(
            models.Debt.id == debt_id,
            models.Debt.user_id == user_id,
        )
        .first()
    )
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found",
        )

    debt.creditor_name = payload.creditor_name
    debt.total_amount = payload.total_amount
    # When updating, keep remaining_amount as-is unless the client wants
    # to reset it to the new total explicitly.
    if debt.remaining_amount is None:
        debt.remaining_amount = payload.total_amount
    debt.emi_amount = payload.emi_amount
    debt.interest_rate = payload.interest_rate
    debt.is_flexible = payload.is_flexible
    debt.priority = payload.priority

    db.add(debt)
    db.commit()
    db.refresh(debt)

    return debt


@router.delete(
    "/{debt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_debt(
    debt_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Delete a debt owned by the current user.
    """
    debt = (
        db.query(models.Debt)
        .filter(
            models.Debt.id == debt_id,
            models.Debt.user_id == user_id,
        )
        .first()
    )
    if not debt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debt not found",
        )

    db.delete(debt)
    db.commit()

