from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import URL, create_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/postgres")

SYNC_DATABASE_URL = DATABASE_URL.replace("+asyncpg", "")  

engine = create_async_engine(DATABASE_URL, echo=True)

sync_engine = create_engine(SYNC_DATABASE_URL, echo=True)


postgres_factory = None


async def create_postgres_factory():
    ti_db_engine = create_async_engine(
        URL.create(
            drivername="postgresql+asyncpg",
            username="postgres",
            password="password",
            host="localhost",
            port="5432",
            database="postgres",
        ),
        isolation_level="READ COMMITTED",
        pool_size=40,
        max_overflow=10,
        pool_pre_ping=True
    )
    async_sessionmaker = sessionmaker(ti_db_engine, class_=AsyncSession)
    return async_sessionmaker



async def init_database():
    global postgres_factory
    if not postgres_factory:
        postgres_factory = await create_postgres_factory()


async def get_postgres_factory():
    global postgres_factory
    if not postgres_factory:
        postgres_factory = await create_postgres_factory()
    return postgres_factory

# SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Base = declarative_base()
# def create_tables():
#     from app.models import User, Expense  
#     Base.metadata.create_all(sync_engine)

# async def get_db():
#     async with SessionLocal() as session:
#         yield session


@asynccontextmanager
async def async_get_postgres():
    postgres_factory = await get_postgres_factory()
    db = postgres_factory()
    try:
        yield db
        await db.commit()
    except Exception as e:
        await db.rollback()
    finally:
        await db.close()
