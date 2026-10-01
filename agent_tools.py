import sqlite3
import json
from langchain_core.tools import tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

CHROMA_PATH = "chroma_db"
DB_PATH = "customer_db.sqlite"

# Re-initialize embeddings & vector store connection
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

@tool
def get_customer_account_details(customer_id: str) -> str:
    """
    Look up customer account tenure, prior fraud claims in the last 30 days, 
    risk score, and current account status from the database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT account_created_date, prior_fraud_claims_30d, risk_score, account_status
        FROM customer_profiles 
        WHERE customer_id = ?
    """, (customer_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return json.dumps({"error": f"Customer ID {customer_id} not found."})
        
    return json.dumps({
        "customer_id": customer_id,
        "account_created_date": row[0],
        "prior_fraud_claims_30d": row[1],
        "risk_score": row[2],
        "account_status": row[3]
    })

@tool
def query_visa_policy(search_query: str) -> str:
    """
    Query internal Visa dispute policies to verify thresholds, time limits, 
    and mandatory procedures for chargebacks and fraud claims.
    """
    docs = retriever.invoke(search_query)
    if not docs:
        return "No matching policy found."
    return "\n\n".join([d.page_content for d in docs])


if __name__ == "__main__":
    import pandas as pd
    sample_df = pd.read_csv("data/batch_disputes.csv")
    sample_cid = str(sample_df.iloc[0]["customer_id"])
    
    print("\n--- Testing Tool: get_customer_account_details ---")
    print(get_customer_account_details.invoke({"customer_id": sample_cid}))
    
    print("\n--- Testing Tool: query_visa_policy ---")
    print(query_visa_policy.invoke({"search_query": "time limit to file dispute"}))