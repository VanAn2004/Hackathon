import pandas as pd
from src.db import engine
from sqlalchemy import inspect, text

def save_alerts(df: pd.DataFrame):
    if "anomaly" not in df.columns:
        return

    alerts = df[df["anomaly"] == -1].copy()

    # Mapping các cột nếu có
    if "id" in alerts.columns:
        alerts = alerts.rename(columns={"id": "transaction_id"})
    if "timestamp" in alerts.columns:
        alerts = alerts.rename(columns={"timestamp": "created_at"})

    # Thêm message
    alerts["alert_msg"] = "Giao dịch bất thường được phát hiện"

    # Kiểm tra bảng alerts có cột nào
    insp = inspect(engine)
    db_cols = [col["name"] for col in insp.get_columns("alerts")]

    # Chỉ giữ lại cột có trong DB
    alerts = alerts[[c for c in alerts.columns if c in db_cols]]

    # Lưu vào DB
    alerts.to_sql("alerts", engine, if_exists="append", index=False)

    # Cleanup trùng lặp (giữ bản mới nhất theo ctid)
    with engine.begin() as conn:
        conn.execute(text("""
            DELETE FROM alerts a
            USING alerts b
            WHERE a.ctid < b.ctid
              AND a.* IS NOT DISTINCT FROM b.*
        """))
