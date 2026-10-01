import os
import json
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from agent_tools import get_customer_account_details, query_visa_policy

# Load the Groq API key from the .env file
load_dotenv()
if not os.environ.get("GROQ_API_KEY"):
    raise ValueError("GROQ_API_KEY not found in .env file.")

# 1. Initialize the free Groq LLM (Llama 3 70B is excellent at tool calling)
llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

# 2. Define the tools the agent is allowed to use
tools = [get_customer_account_details, query_visa_policy]

# 3. Define the Agent's Brain (System Prompt)
system_prompt = """You are a strictly logical Visa Dispute Resolution AI. 
Your objective is to evaluate transaction disputes based ONLY on Visa's internal policies and the customer's account data.

For every dispute, you MUST:
1. Call `query_visa_policy` to find the rules for the specific claim category and amount.
2. Call `get_customer_account_details` using the provided customer_id to check account age and prior fraud history.

Decision Rules:
- If the policy says it requires manual review, your decision must be ESCALATE.
- If the dispute fails the policy criteria (e.g., past the 60-day limit), your decision must be DENY.
- If the dispute meets all criteria for automatic approval, your decision must be APPROVE.

You must return your FINAL answer as raw text in STRICT JSON format like this:
{
    "decision": "APPROVE" | "DENY" | "ESCALATE",
    "reasoning": "Step-by-step explanation of why..."
}
DO NOT call a tool named 'json'. Output the raw JSON text directly as your final response.
"""

# 4. Compile the LangGraph Agent
dispute_agent = create_react_agent(llm, tools, prompt=system_prompt)

def process_single_ticket(ticket_data: dict) -> str:
    """Passes a single dispute ticket to the agent and returns its JSON decision."""
    
    prompt = f"""
    Please evaluate the following dispute ticket:
    Ticket ID: {ticket_data['ticket_id']}
    Customer ID: {ticket_data['customer_id']}
    Claim Category: {ticket_data['claim_category']}
    Amount: ${ticket_data['amount_usd']}
    Dispute Date: {ticket_data['dispute_date']}
    Transaction Date: {ticket_data['transaction_date']}
    Customer Notes: {ticket_data['customer_notes']}
    """
    
    # Run the agent
    response = dispute_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    
    # Extract the final message from the agent
    final_output = response["messages"][-1].content
    return final_output

if __name__ == "__main__":
    import pandas as pd
    
    print("Loading test ticket...")
    df = pd.read_csv("data/batch_disputes.csv")
    test_ticket = df.iloc[0].to_dict()
    
    print("\n--- Processing Ticket via LangGraph Agent ---")
    print(f"Ticket Details: {test_ticket['claim_category']} for ${test_ticket['amount_usd']}")
    
    result_json = process_single_ticket(test_ticket)
    
    print("\n--- Agent Final Decision ---")
    print(result_json)