import sqlite3
import pandas as pd
import time
import json
from agent_workflow import process_single_ticket

CSV_PATH = "data/batch_disputes.csv"
DB_PATH = "customer_db.sqlite"

def setup_results_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_decisions (
            ticket_id TEXT PRIMARY KEY,
            customer_id TEXT,
            decision TEXT,
            reasoning TEXT,
            processed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def run_batch_job():
    print("Initializing Batch AI Scoring Platform with Throttling...")
    setup_results_table()
    
    # Let's process just 5 tickets to prove the pipeline works without hitting token limits
    df = pd.read_csv(CSV_PATH)
    tickets = df.to_dict('records')[:5] 
    
    print(f"Loaded {len(tickets)} tickets. Processing sequentially with 5-second backoff...")
    start_time = time.time()
    
    results = []
    for i, ticket in enumerate(tickets, 1):
        print(f"\nProcessing ticket {i}/{len(tickets)} (ID: {ticket['ticket_id']})...")
        try:
            raw_result = process_single_ticket(ticket)
            
            # Sanitize the output: remove markdown formatting if the LLM added it
            cleaned_result = raw_result.replace("```json", "").replace("```", "").strip()
            result_dict = json.loads(cleaned_result)
            
            decision = result_dict.get('decision', 'UNKNOWN')
            reasoning = result_dict.get('reasoning', 'No reasoning provided.')
            
            results.append((ticket['ticket_id'], ticket['customer_id'], decision, reasoning))
            print(f"✅ Success -> Decision: {decision}")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((ticket['ticket_id'], ticket['customer_id'], "ERROR", str(e)))
            
        # Rate Limit Throttling: Pause for 5 seconds to let the Groq token bucket refill
        if i < len(tickets):
            time.sleep(5)

    print("\nWriting results to Data Warehouse (SQLite)...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    db_records = [(r[0], r[1], r[2], r[3], timestamp) for r in results]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO ai_decisions 
        (ticket_id, customer_id, decision, reasoning, processed_at)
        VALUES (?, ?, ?, ?, ?)
    """, db_records)
    
    conn.commit()
    conn.close()
    
    duration = time.time() - start_time
    print(f"Batch complete! Processed {len(tickets)} tickets in {duration:.2f} seconds.")

if __name__ == "__main__":
    run_batch_job()