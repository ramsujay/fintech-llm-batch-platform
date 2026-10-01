import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

def generate_disputes(num_records=100):
    categories = ["Fraudulent Transaction", "Merchant Non-Delivery", "Subscription Cancellation"]
    
    data = []
    for _ in range(num_records):
        # Simulate transactions between 1 and 90 days ago
        days_ago = random.randint(1, 90)
        transaction_date = datetime.now() - timedelta(days=days_ago)
        
        record = {
            "ticket_id": fake.uuid4()[:8],
            "customer_id": fake.uuid4()[:8],
            "transaction_date": transaction_date.strftime("%Y-%m-%d"),
            "dispute_date": datetime.now().strftime("%Y-%m-%d"),
            "amount_usd": round(random.uniform(5.0, 300.0), 2),
            "claim_category": random.choice(categories),
            "customer_notes": fake.sentence(nb_words=10)
        }
        data.append(record)
        
    df = pd.DataFrame(data)
    df.to_csv("data/batch_disputes.csv", index=False)
    print(f"Generated {num_records} synthetic disputes at data/batch_disputes.csv")

if __name__ == "__main__":
    generate_disputes()