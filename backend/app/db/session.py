from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_URL="postgresql://postgres:akash45@localhost:5432/ecom8"
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