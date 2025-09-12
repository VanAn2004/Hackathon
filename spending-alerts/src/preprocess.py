import pandas as pd

def preprocess(df: pd.DataFrame):
    df = df.copy()
    df["amount"] = df["amount"].astype(float)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
