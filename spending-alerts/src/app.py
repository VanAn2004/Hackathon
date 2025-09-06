from fastapi import FastAPI
import pandas as pd
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
    return {"status": "done", "alerts": int((df["anomaly"]==-1).sum())}

@app.get("/alerts")
def get_alerts():
    import pandas as pd
    df = pd.read_sql("SELECT * FROM alerts ORDER BY created_at DESC", engine)
    return df.to_dict(orient="records")
