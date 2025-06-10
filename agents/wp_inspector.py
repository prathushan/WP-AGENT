import httpx
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ✅ Get token from environment variable (do NOT pass the actual token to getenv)
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

async def handle_error(data):
    issue_type = data.get("error_type")

    if issue_type == "fatal":
        code = data.get("error_log")
        fix = await fetch_fix_suggestion(code)
        return {"fix": fix}

    elif issue_type == "404":
        return {"fix": "Check permalink structure or page slug"}

    return {"fix": "Unhandled issue"}

async def fetch_fix_suggestion(code_snippet):
    url = "https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-Instruct-hf"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"Fix this WordPress PHP fatal error:\n{code_snippet}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result[0]["generated_text"]
