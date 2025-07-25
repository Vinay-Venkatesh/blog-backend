import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{os.getenv('postgres_username')}:"
    f"{os.getenv('postgres_password')}@"
    f"{os.getenv('hostname')}/"
    f"{os.getenv('database')}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# Base class for our models
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
