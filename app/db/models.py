# app/db/models.py
import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    Boolean,
    Integer,
    Numeric,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="user")
    debts = relationship("Debt", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    date = Column(Date, nullable=False)
    type = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(50), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="transactions")


class Debt(Base):
    __tablename__ = "debts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    creditor_name = Column(String(255), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    remaining_amount = Column(Numeric(12, 2), nullable=False)

    emi_amount = Column(Numeric(12, 2), nullable=True)
    interest_rate = Column(Numeric(5, 2), nullable=True)

    is_flexible = Column(Boolean, default=False)
    priority = Column(Integer, default=0)
    status = Column(String(50), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="debts")
    payments = relationship("Payment", back_populates="debt")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    debt_id = Column(UUID(as_uuid=True), ForeignKey("debts.id"), nullable=False)

    amount_paid = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_mode = Column(String(50), nullable=True)
    note = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")
    debt = relationship("Debt", back_populates="payments")
