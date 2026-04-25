from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:Shreeya%40210926@localhost:5432/healthcare33_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,   # set True temporarily if you need to see raw SQL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()