import psycopg2, random, datetime

DB = dict(dbname="spending_db", user="user", password="password", host="localhost", port=5432)

def insert_dummy():
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    categories = ["food", "shopping", "rent", "entertainment", "travel"]

    for _ in range(20):
        user_id = random.randint(1, 5)   # user_id là số nguyên từ 1 → 5
        amount = round(random.uniform(10, 500), 2)
        category = random.choice(categories)
        timestamp = datetime.datetime.now()

        cur.execute(
            "INSERT INTO transactions (user_id, amount, category, timestamp) VALUES (%s, %s, %s, %s)",
            (user_id, amount, category, timestamp)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Dummy transactions inserted.")

if __name__ == "__main__":
    insert_dummy()
