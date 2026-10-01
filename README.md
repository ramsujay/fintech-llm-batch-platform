# Async LLM Batch Scoring Platform

An asynchronous, fault-tolerant batch processing platform built with **LangGraph**, **ChromaDB**, and **Groq (OpenAI-OSS models)**. Designed to automate high-throughput transaction dispute resolutions for financial systems.

## Architecture
- **Orchestration:** Python-based throttled batch processor with error handling for API rate limits (HTTP 429).
- **Agent Runtime:** LangGraph ReAct agent that enforces strict JSON output schemas.
- **RAG / Vector Store:** Local ChromaDB instance using `all-MiniLM-L6-v2` embeddings for querying unstructured policy documents.
- **SQL Tooling:** SQLite-backed tool functions for the agent to verify customer account history and prior fraud claims.
- **Storage:** Final LLM decisions and reasoning traces are sanitized and committed to a local Data Warehouse (SQLite).

## How to Run Locally
1. Clone the repository and install dependencies: `pip install -r requirements.txt`
2. Add your Groq API key to a `.env` file: `GROQ_API_KEY=gsk_...`
3. Generate the mock data: `python generate_data.py`
4. Build the vector database: `python build_vector_store.py`
5. Seed the SQLite database: `python seed_customer_db.py`
6. Run the batch pipeline: `python batch_processor.py`