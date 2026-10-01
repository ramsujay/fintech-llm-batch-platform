import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

# Configuration
DOC_PATH = "data/visa_dispute_policy.md"
CHROMA_PATH = "chroma_db"

def build_chroma_db():
    print("Loading policy document...")
    # 1. Load the document
    with open(DOC_PATH, 'r') as f:
        doc_text = f.read()

    # 2. Split based on Markdown Headers (Keeps context intact)
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    chunks = markdown_splitter.split_text(doc_text)
    
    print(f"Split document into {len(chunks)} contextual chunks.")

    # 3. Initialize local open-source embeddings (Cost Optimization)
    print("Downloading/Loading local embedding model (all-MiniLM-L6-v2)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 4. Store in ChromaDB locally
    print("Building ChromaDB vector store...")
    db = Chroma.from_documents(
        chunks, 
        embeddings, 
        persist_directory=CHROMA_PATH
    )
    
    print(f"Vector store successfully built and saved to ./{CHROMA_PATH}")
    
    # 5. Quick Test
    test_query = "What happens if a dispute is under $50?"
    results = db.similarity_search(test_query, k=1)
    print("\n--- Test Retrieval ---")
    print(f"Query: {test_query}")
    print(f"Retrieved Context: {results[0].page_content}")

if __name__ == "__main__":
    build_chroma_db()