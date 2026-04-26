import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
print("Key loaded:", OPENROUTER_API_KEY[:15] if OPENROUTER_API_KEY else "NOT FOUND")

def generate_movie_description(title: str, year: int = None) -> str:
    year_str = f" ({year})" if year else ""
    prompt = (
        f"Write a concise 2-3 sentence description for the movie '{title}'{year_str}. "
        "Focus on genre, plot themes, tone, and what kind of audience would enjoy it. "
        "Do not use spoilers. Output only the description, no extra text."
    )

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "openrouter/auto",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 200
        }
    )

    data = response.json()
    print("API Response:", data)

    if "error" in data:
        print("Error:", data["error"])
        return None

    content = data["choices"][0]["message"]["content"]
    if not content:
        return None

    return content.strip()
