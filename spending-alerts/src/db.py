from sqlalchemy import create_engine

DB_URL = "postgresql://user:password@localhost:5432/spending_db"
engine = create_engine(DB_URL)
