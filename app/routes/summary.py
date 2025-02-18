from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text
from app.database import async_get_postgres
from app.auth import verify_token
from typing import Optional, List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/summary")
async def get_expense_summary(
    token: dict = Depends(verify_token),
    month: str = Query(..., regex=r"^\d{4}-\d{2}$"), 
    categories: Optional[List[str]] = Query(None)
    # category: Optional[str] = Query(None)
    
):
    user_id = token.get("user_id")  
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token: User ID missing")
    
    start_date = datetime.strptime(f"{month}-01", "%Y-%m-%d").date()
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1)

    async with async_get_postgres() as db:
        try:
            expenses = []
            
            query = text("""
                SELECT COALESCE(SUM(amount), 0) as total_expense, category, COALESCE(SUM(amount), 0) as category_total
                FROM expenses
                WHERE user_id = :user_id AND date >= :start_date AND date < :end_date
            """)

            params = {"user_id": user_id, "start_date": start_date, "end_date": end_date}

            # if categories:
            #     # query = text(query.text + " AND category = :category")
            #     # params["category"] = category
            #     query = text(query.text + " AND category IN :categories")
            #     params["categories"] = categories
            if categories:
                query = text(query.text + " AND category = ANY(:categories)")
                params["categories"] = categories


            query = text(query.text + " GROUP BY category")  

            print(query)

            print(f"Executing query: {query.text} with params: {params}")

            result = await db.execute(query, params)
            expenses = result.mappings().all() if result else []  

        except Exception as e:
            print(f"Database error: {e}")  
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    
    total_expense = sum(exp["category_total"] for exp in expenses) if expenses else 0
    breakdown = {exp["category"]: exp["category_total"] for exp in expenses} if expenses else {}

    return {"total_expense": total_expense, "breakdown": breakdown}

