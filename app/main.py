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

app.include_router(users.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(summary.router, prefix="/api")

@app.get("/")
def root():
     return {"message": "Expense Tracker API is running!"}