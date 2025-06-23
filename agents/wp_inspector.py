import os
import logging
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from typing import Dict, List

# Load .env variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is missing")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wp_agent")

# In-memory chat memory (for demo purposes, not suitable for production)
chat_memory: Dict[str, List[Dict[str, str]]] = {}

# FastAPI instance
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "WP AI Agent with Memory is live 🚀"}

@app.post("/handle-message")
async def receive_wp_message(request: Request):
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    message = data.get("message")
    user_id = data.get("user_id")  # You should pass this from your plugin

    if not message or not user_id:
        raise HTTPException(status_code=400, detail="Missing 'message' or 'user_id'")

    try:
        result = await handle_message(user_id, message)
        return {"result": result}
    except Exception as e:
        logger.exception("Error while processing message")
        raise HTTPException(status_code=500, detail=str(e))

async def handle_message(user_id: str, user_message: str):
    # Initialize memory if not present
    if user_id not in chat_memory:
        chat_memory[user_id] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant that fixes WordPress and PHP issues."
            }
        ]

    # Add user message to memory
    chat_memory[user_id].append({"role": "user", "content": user_message})

    # Limit to last 10 messages to avoid token limit issues
    message_history = chat_memory[user_id][-10:]

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": message_history,
        "temperature": 0.7,
        "max_tokens": 400,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            logger.error(f"OpenRouter error {response.status_code}: {response.text}")
            return f"Model unavailable (status {response.status_code})."

        result = response.json()
        ai_reply = result["choices"][0]["message"]["content"]

        # Store AI response in memory
        chat_memory[user_id].append({"role": "assistant", "content": ai_reply})

        return ai_reply

    except httpx.TimeoutException:
        return "Model request timed out."
    except Exception as e:
        logger.exception("OpenRouter request failed")
        return f"Error contacting model: {e}"
