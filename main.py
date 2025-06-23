from fastapi import FastAPI, Request, HTTPException
import logging
from agents.wp_inspector import handle_message  # import the logic from wp_inspector.py

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wp_agent")

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
    user_id = data.get("user_id")

    if not message or not user_id:
        raise HTTPException(status_code=400, detail="Missing 'message' or 'user_id'")

    try:
        result = await handle_message(user_id, message)
        return {"result": result}
    except Exception as e:
        logger.exception("Error while processing message")
        raise HTTPException(status_code=500, detail=str(e))
