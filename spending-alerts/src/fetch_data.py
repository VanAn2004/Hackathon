import pandas as pd
from src.db import engine

def get_transactions():
    return pd.read_sql("SELECT * FROM transactions", engine)

if __name__ == "__main__":
    df = get_transactions()
    print(df.head())
