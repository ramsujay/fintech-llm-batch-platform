import sqlite3
import pandas as pd
import random
from datetime import datetime, timedelta

CSV_PATH = "data/batch_disputes.csv"
DB_PATH = "customer_db.sqlite"

def seed_database():
    df = pd.read_csv(CSV_PATH)
    customer_ids = df["customer_id"].unique()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_profiles (
            customer_id TEXT PRIMARY KEY,
            account_created_date TEXT,
            prior_fraud_claims_30d INTEGER,
            risk_score INTEGER,
            account_status TEXT
        )
    """)
    
    cursor.execute("DELETE FROM customer_profiles")
    
    records = []
    now = datetime.now()
    for cid in customer_ids:
        # Randomize account age: 20% newer than 6 months, 80% older
        days_old = random.randint(30, 700)
        created_date = (now - timedelta(days=days_old)).strftime("%Y-%m-%d")
        
        # 15% chance of prior fraud claims in last 30 days
        prior_claims = random.choices([0, 1, 2], weights=[0.85, 0.10, 0.05])[0]
        risk_score = random.randint(300, 850)
        account_status = "ACTIVE" if risk_score > 400 else "FLAGGED"
        
        records.append((str(cid), created_date, prior_claims, risk_score, account_status))
        
    cursor.executemany("""
        INSERT INTO customer_profiles (customer_id, account_created_date, prior_fraud_claims_30d, risk_score, account_status)
        VALUES (?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(records)} customer profiles into {DB_PATH}")

if __name__ == "__main__":
    seed_database()