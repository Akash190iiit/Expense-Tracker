from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import async_get_postgres
from app.auth import hash_password, verify_password, create_access_token

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password:str

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    hashed_password=hash_password(password=user.password)

    async with async_get_postgres() as db:
        res = await db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": user.email})
        print("Database factory acquired")
        res = res.fetchall()

    existing_user = res[0] if res else None

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # import pdb
    # pdb.set_trace()
    async with async_get_postgres() as db:
        # async with async_get_postgres() as db:
        #     print(f"Inserting user: username={user.username}, email={user.email}, password={hashed_password}") 
        await db.execute(
            text("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)"),
            {"username": user.username, "email": user.email, "password": hashed_password}
        )
        await db.commit()
        
    
   
    return {"message": "User registered successfully."}


@router.post("/login")
async def login(user: UserLogin):
    async with async_get_postgres() as db:
        res = await db.execute(text("SELECT id, email, password FROM users WHERE email = :email"), {"email": user.email})
        user_data = res.fetchone()

    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, email, hashed_password = user_data

    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"id": user_id, "email": email})

    return {"access_token": access_token, "token_type": "bearer"}