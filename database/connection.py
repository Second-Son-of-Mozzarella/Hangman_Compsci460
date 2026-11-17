
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME")
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=False,
    implicit_returning=False
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def test_connection():
    """Test whether the database connection is working."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connected successfully!")
            return result.scalar() == 1

    except Exception as error:
        print(f"Database connection failed: {error}")
        return False

