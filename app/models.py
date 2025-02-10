from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    expenses = relationship("Expense", back_populates="user")

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String, nullable=True)
    payment_method = Column(String(50), nullable=True)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, default=func.now())

    user = relationship("User", back_populates="expenses")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    payment_method = Column(String(50), nullable=False)
    date = Column(Date, nullable=False)