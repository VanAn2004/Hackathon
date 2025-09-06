import psycopg2
import pandas as pd

def send_sms(user_id, message):
    print(f"[SMS] To: {user_id} | Message: {message}")

def save_alerts(df):
    try:
        conn = psycopg2.connect(
            dbname="spending_db",
            user="user",
            password="password",
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()

        for _, row in df.iterrows():
            alert_msg = f"⚠️ Unusual spending detected: {row['amount']} in {row['category']}"

            try:
                cur.execute(
                    "INSERT INTO alerts (user_id, message) VALUES (%s, %s)",
                    (row["user_id"], alert_msg)
                )
                send_sms(row["user_id"], alert_msg)

            except Exception as e:
                print("❌ Error inserting alert:", e)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Database connection error:", e)
