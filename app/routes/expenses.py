from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from app.database import async_get_postgres
from app.auth import verify_token
from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from app.auth import verify_token  

router = APIRouter()

class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str
    payment_method: str
    date: date

class ExpenseResponse(ExpenseCreate):
    id: int

@router.post("/expenses", status_code=201)
async def add_expense(
    expense_data: ExpenseCreate,
    token: dict = Depends(verify_token)
):
    async with async_get_postgres() as db:
        query = text("""
            INSERT INTO expenses (user_id, amount, category, description, payment_method, date)
            VALUES (:user_id, :amount, :category, :description, :payment_method, :date)
            RETURNING id
        """)

        expense_id = None

        u_email = token["sub"]
        # user-> u_email -> id
        try:
            result = await db.execute(query, {
                "user_id": token["sub"],  
                "amount": expense_data.amount,
                "category": expense_data.category,
                "description": expense_data.description,
                "payment_method": expense_data.payment_method,
                "date": expense_data.date
            })
            await db.commit()
            import pdb
            pdb.set_trace()
            inserted_row = result.fetchone()
            expense_id = inserted_row[0] if inserted_row else None


            if expense_id is None:
                raise HTTPException(status_code=500, detail="Failed to add expense.")

            await db.commit()
        
        except Exception as e:
            await db.rollback() 
            print(e)
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    print(expense_id)

    return {"message": "Expense added successfully.", "expense_id": expense_id}
    
    # return {"message": "Expense added successfully.", "expense_id": expense_id}


@router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    token: dict = Depends(verify_token),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    category: Optional[str] = Query(None),
    payment_method: Optional[str] = Query(None)
):
    user_id = token["user_id"]
    async with async_get_postgres() as db:
        query = text("""
            SELECT id, amount, category, description, payment_method, date
            FROM expenses
            WHERE user_id = :user_id
        """)

        params = {"user_id": token["sub"]}
        
        if start_date:
            query = text(query.text + " AND date >= :start_date")
            params["start_date"] = start_date
        if end_date:
            query = text(query.text + " AND date <= :end_date")
            params["end_date"] = end_date
        if category:
            query = text(query.text + " AND category = :category")
            params["category"] = category
        if payment_method:
            query = text(query.text + " AND payment_method = :payment_method")
            params["payment_method"] = payment_method

        result = await db.execute(query, params)
        expenses = result.mappings().all()

    return expenses


@router.get("/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense_by_id(expense_id: int, token: dict = Depends(verify_token)):
    async with async_get_postgres() as db:
        query = text("""
            SELECT id, amount, category, description, payment_method, date
            FROM expenses
            WHERE id = :expense_id AND user_id = :user_id
        """)
        result = await db.execute(query, {"expense_id": expense_id, "user_id": token["sub"]})
        expense = result.mappings().first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    return expense
