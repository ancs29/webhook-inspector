from fastapi import FastAPI, Request

app = FastAPI()

webhooks = []


@app.post("/receive")
async def receive_webhook(request: Request):
    body = await request.body()

    event = {
        "body": body.decode(),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
    }

    webhooks.append(event)
    return {"status": "ok"}


@app.get("/webhooks")
def get_events():
    return webhooks
