from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:password@pg-spending:5432/spending_db"

engine = create_engine(DB_URL)
