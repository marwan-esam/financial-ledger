from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

# Connect to PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@db/ledger_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to open and close the database connection per request
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


# The Base class
class Base(DeclarativeBase):
  pass
