import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()

# Get OpenRouter API Key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY environment variable is missing")

logger = logging.getLogger(__name__)

async def handle_error(data):
    error_log = data.get("error_log", "")
    if not error_log:
        return {"fix": "No error log provided"}
    return {"fix": await fetch_fix_suggestion(error_log)}

async def fetch_fix_suggestion(error_log):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://yourdomain.com",  # Optional, but recommended
        "X-Title": "WP Site Inspector AI Agent"
    }

    # Using free and reliable OpenRouter model
    payload = {
        "model": "deepseek/deepseek-chat-v3-0324:free",  # or "mistralai/mistral-7b-instruct"
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful AI assistant that fixes WordPress PHP errors."
            },
            {
                "role": "user",
                "content": f"Fix this WordPress PHP error:\n{error_log}"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code != 200:
                logger.error(f"OpenRouter error: {response.status_code} {response.text}")
                return f"Model unavailable. Try again later. (Status: {response.status_code})"

            result = response.json()
            return result["choices"][0]["message"]["content"]

    except httpx.TimeoutException:
        logger.error("OpenRouter API timeout")
        return "Model timed out. Please try again."

    except Exception as e:
        logger.exception("OpenRouter request failed")
        return f"Error contacting model: {str(e)}"

