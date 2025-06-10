from fastapi import FastAPI, Request
from agents.wp_inspector import handle_error

app = FastAPI()

@app.post("/handle-error")
async def receive_wp_error(request: Request):
    data = await request.json()
    result = await handle_error(data)
    return {"result": result}
print("FastAPI server is running...")