import os
from dotenv import load_dotenv
from groq import Groq

# Load the API key from your .env file
load_dotenv()

# Initialize the Groq client
client = Groq()

print("Fetching available models for your API key...\n")
models = client.models.list()

print("--- AVAILABLE MODELS ---")
for model in models.data:
    print(model.id)