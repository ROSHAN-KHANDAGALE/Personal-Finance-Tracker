from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies import get_current_user_id
from app.schemas.recurring import (
    RecurringCreate,
    RecurringUpdate,
    RecurringResponse,
)
from app.services import recurring_service


router = APIRouter(prefix="/recurring", tags=["Recurring Transactions"])


@router.get(
    "/",
    response_model=list[RecurringResponse],
    status_code=status.HTTP_200_OK,
)
def list_recurring(
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    return recurring_service.list_recurring(db, user_id)


@router.post(
    "/",
    response_model=RecurringResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recurring(
    payload: RecurringCreate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    rt = recurring_service.create_recurring(db, user_id, payload)
    return rt


@router.get(
    "/{recurring_id}",
    response_model=RecurringResponse,
    status_code=status.HTTP_200_OK,
)
def get_recurring_by_id(
    recurring_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    rt = recurring_service.get_recurring(db, user_id, recurring_id)
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )
    return rt


@router.put(
    "/{recurring_id}",
    response_model=RecurringResponse,
    status_code=status.HTTP_200_OK,
)
def update_recurring(
    recurring_id: UUID,
    payload: RecurringUpdate,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    rt = recurring_service.update_recurring(db, user_id, recurring_id, payload)
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )
    return rt


@router.delete(
    "/{recurring_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_recurring(
    recurring_id: UUID,
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    ok = recurring_service.delete_recurring(db, user_id, recurring_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurring transaction not found",
        )


@router.post(
    "/run",
    status_code=status.HTTP_200_OK,
)
def run_scheduler(
    run_date: date | None = Query(
        default=None,
        description="Optional override for today; if omitted, server date is used",
    ),
    db: Session = Depends(get_db),
    user_id=Depends(get_current_user_id),
):
    """
    Manually trigger the recurring scheduler for the current user.
    """
    created_count = recurring_service.run_recurring_scheduler(
        db=db,
        user_id=user_id,
        today=run_date,
    )
    return {"created_transactions": created_count}

