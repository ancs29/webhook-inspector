import json

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db import Base, SessionLocal, engine
from model import WebhookTable

Base.metadata.create_all(bind=engine)


app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/receive")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):

    try:
        body_text = (await request.body()).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid UTF-8 data") from exc

    try:
        body_json = json.loads(body_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON data") from exc

    webhook = WebhookTable(
        body=json.dumps(body_json),
        headers=json.dumps(dict(request.headers)),
        query_params=json.dumps(dict(request.query_params)),
    )

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return {"status": "saved", "id": webhook.id}


@app.get("/webhooks")
def get_webhooks(db: Session = Depends(get_db)):
    webhooks = db.query(WebhookTable).all()

    return [
        {
            "id": row.id,
            "body": row.body,
            "headers": row.headers,
            "query_params": row.query_params,
        }
        for row in webhooks
    ]


@app.get("/webhooks/{webhook_id}")
def get_webhook(webhook_id: int, db: Session = Depends(get_db)):
    webhook = db.query(WebhookTable).filter(WebhookTable.id == webhook_id).first()

    if not webhook:
        return {"error": "Not found"}

    return {
        "id": webhook.id,
        "body": webhook.body,
        "headers": json.loads(webhook.headers),
        "query_params": json.loads(webhook.query_params),
    }


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
