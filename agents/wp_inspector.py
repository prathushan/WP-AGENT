import httpx
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
if not HUGGINGFACE_API_TOKEN:
    raise RuntimeError("HUGGINGFACE_API_TOKEN environment variable is missing")

logger = logging.getLogger(__name__)

async def handle_error(data):
    issue_type = data.get("error_type")
    error_log = data.get("error_log", "")

    if issue_type == "fatal":
        if not error_log:
            return {"fix": "No error log provided for fatal error"}
        return {"fix": await fetch_fix_suggestion(error_log)}
    
    elif issue_type == "404":
        return {"fix": "Check permalink structure or page slug"}
    
    return {"fix": "Unhandled issue type"}

async def fetch_fix_suggestion(code_snippet):
    url = "https://api-inference.huggingface.co/models/codellama/CodeLlama-7b-Instruct-hf"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": f"Fix this WordPress PHP fatal error:\n{code_snippet}",
        "parameters": {
            "max_new_tokens": 200,
            "return_full_text": False
        }
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            # Handle Hugging Face API errors
            if response.status_code != 200:
                error_msg = f"Hugging Face API error: {response.status_code} {response.text}"
                logger.error(error_msg)
                return f"Model unavailable. Please try again later. (Status: {response.status_code})"
            
            result = response.json()
            
            # Handle model loading errors
            if "error" in result:
                if "loading" in result["error"].lower():
                    return "Model is still loading. Please try again in 20 seconds."
                return f"Model error: {result['error']}"
            
            # Parse successful response
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "No suggestion generated")
            
            return "Unexpected response format from model"
    
    except httpx.TimeoutException:
        logger.error("Hugging Face API timeout")
        return "Model timed out. Please try again."
    except Exception as e:
        logger.exception("Hugging Face request failed")
        return f"Error contacting model: {str(e)}"