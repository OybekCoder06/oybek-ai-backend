import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AI_API_KEY")
API_URL = os.getenv("AI_API_URL")


async def generate_ai_response(user_id: str, user_message: str):

    # AI stilini shu yerda belgilaymiz:
    system_prompt = """You are a friendly, humorous Uzbek AI assistant. 
    Always reply warmly, with mild jokes and helpful tone. 
    Never be rude. Keep context short and meaningful."""

    payload = {
        "model": "gpt-4o-mini",  # keyin o'zgartiramiz
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        r = await client.post(API_URL, json=payload, headers=headers)

    data = r.json()
    return data["choices"][0]["message"]["content"]

