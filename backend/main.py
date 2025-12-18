import json

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine
from .model import WebhookTable

Base.metadata.create_all(bind=engine)


app = FastAPI()

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------- API ROUTES ----------- #


@app.post("/api/receive")
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


@app.get("/api/webhooks")
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


@app.get("/api/webhooks/{webhook_id}")
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


# ----------- HTML ROUTES ----------- #
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Query all webhooks from database
    webhooks = db.query(WebhookTable).all()

    webhook_url = f"{request.url.scheme}://{request.url.netloc}/api/receive"

    # Pass webhooks to template
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "webhooks": webhooks, "webhook_url": webhook_url},
    )


@app.get("/{webhook_id}", response_class=HTMLResponse)
async def webhook_detail(
    webhook_id: int, request: Request, db: Session = Depends(get_db)
):
    webhook = db.query(WebhookTable).filter(WebhookTable.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    # Pretty-print JSON with indentation
    body_formatted = json.dumps(json.loads(webhook.body), indent=2)
    headers_formatted = json.dumps(json.loads(webhook.headers), indent=2)
    query_params_formatted = json.dumps(json.loads(webhook.query_params), indent=2)

    return templates.TemplateResponse(
        "webhook.html",
        {
            "request": request,
            "webhook": webhook,
            "body_formatted": body_formatted,
            "headers_formatted": headers_formatted,
            "query_params_formatted": query_params_formatted,
        },
    )


# ----------- GLOBAL EXCEPTION HANDLER ----------- #
@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
