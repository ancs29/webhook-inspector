import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

webhooks = []


@app.post("/receive")
async def receive_webhook(request: Request):

    try:
        body_text = (await request.body()).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid UTF-8 data") from exc

    try:
        body_json = json.loads(body_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from exc

    webhook = {
        "body": body_json,
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
    }

    webhooks.append(webhook)
    return {"status": "ok"}


@app.get("/webhooks")
def get_webhooks():
    return webhooks


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Understand and check global exception handler function
# Figure out how to format try and except blocks in receive function and all functions
