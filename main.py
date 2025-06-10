from fastapi import FastAPI, Request, HTTPException
import logging
from agents.wp_inspector import handle_error

app = FastAPI()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "WP Agent is live 🚀"}

@app.post("/handle-error")
async def receive_wp_error(request: Request):
    try:
        # Attempt JSON parsing with error handling
        data = await request.json()
    except Exception as e:
        logger.error(f"JSON parsing failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format. Check your request body syntax."
        )
    
    # Validate required fields
    if "error_type" not in data:
        raise HTTPException(
            status_code=400,
            detail="Missing required field: error_type"
        )
    
    try:
        result = await handle_error(data)
        return {"result": result}
    except Exception as e:
        logger.exception("Processing failed")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )