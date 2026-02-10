from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db import models


def get_current_user(
    db: Session = Depends(get_db),
    x_user_id: str | None = Header(
        default=None,
        alias="X-User-Id",
        description="Temporary user identifier until auth is implemented",
    ),
) -> models.User:
    """
    Lightweight stand-in for real authentication.

    The client must send `X-User-Id` header with a valid UUID
    corresponding to an existing user record. This keeps the
    request user-scoped without hardcoding IDs, and can later be
    swapped with a proper JWT-based dependency.
    """
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-User-Id header is required until authentication is implemented",
        )

    try:
        user_id = UUID(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id must be a valid UUID string",
        )

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found for provided X-User-Id",
        )

    return user


def get_current_user_id(user: models.User = Depends(get_current_user)) -> UUID:
    """
    Convenience dependency for routes/services that only need the user id.
    """
    return user.id

