# app/routes/users.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
)
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    # 🔒 AUTH & PASSWORD HASHING TEMPORARILY DISABLED
    # Will be enabled after auth module integration

    user = models.User(
        email=payload.email,
        name=payload.name,
        password_hash="TEMP_DISABLED",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
