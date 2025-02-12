# from fastapi import FastAPI
# from app.routes import users
# from app.database import create_tables

# app = FastAPI()

# create_tables()

# app.include_router(users.router, prefix="/api", tags=["Users"])
# # app.include_router(expenses.router, prefix="/api", tags=["Expenses"])
# # app.include_router(summary.router, prefix="/api", tags=["Summary"])


# @app.get("/")
# def root():
#     return {"message": "Expense Tracker API is running!"}

from fastapi import FastAPI
from app.routes import users, expenses, summary

app = FastAPI()
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

# create_tables()

app.include_router(users.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")

@app.get("/")
def root():
     return {"message": "Expense Tracker API is running!"}