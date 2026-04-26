import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def embed_text(text: str) -> list:
    response = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openai/text-embedding-3-small",
            "input": text,
            "dimensions": 384
        }
    )
    data = response.json()
    print("Embedding response:", data)

    if "error" in data:
        print("Embedding error:", data["error"])
        return None

    return data["data"][0]["embedding"]
