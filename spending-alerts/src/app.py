from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import numpy as np
from src.fetch_data import get_transactions
from src.preprocess import preprocess
from src.anomaly import detect_anomalies
from src.save_alerts import save_alerts
from src.db import engine

app = FastAPI()

@app.get("/run-anomaly")
def run_anomaly():
    df = get_transactions()
    df = preprocess(df)
    df = detect_anomalies(df)
    save_alerts(df)
    return {"status": "done", "alerts": int((df["anomaly"] == -1).sum())}

@app.get("/alerts")
def get_alerts():
    df = pd.read_sql("SELECT * FROM alerts ORDER BY created_at DESC", engine)

    # Chuyển datetime về string ISO format để JSON serialize được
    for col in df.select_dtypes(include=["datetime", "datetimetz"]).columns:
        df[col] = df[col].astype(str)

    # Thay thế NaN/Inf bằng None
    df = df.replace([np.nan, np.inf, -np.inf], None)

    return JSONResponse(content=df.to_dict(orient="records"))
