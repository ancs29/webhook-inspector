"""
This module contains all FastAPI backend routes for receiving, fetching and displaying webhooks.

Contains three API routes to receive webhooks, get all webhooks, and get a specific webhook by ID.
Contains two HTML routes to display Jinja2 templates containing the home page and a page with the
details of a specific webhook.
Contains a global exception handler to catch unexpected errors and return a JSON error response.
Creates a database session to connect routes to the Postgres database.

Attributes:
    app: FastAPI application instance
    templates: Jinja2Templates instance for rendering HTML templates

Module can be ran with Uvicorn (uvicorn backend.main:app --reload)
"""

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
    """Function used by backend routes to connect to Postgres database.

    This function creates a database session  and closes it after the request is completed.

    Returns:
        db: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ----------- API ROUTES ----------- #
@app.post("/api/webhooks")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    """This route receives incoming webhooks and stores them in the database.

    This route receives POST requests containing JSON webhook data.
    It attempts to convert the data into a UTF-8 string and then parse it as JSON, raising
    exceptions if either fails.
    The webhook body, headers, and query parameters are then stored in the Postgres database.

    Args:
        request: FastAPI Request object representing the incoming HTTP request
        db: SQLAlchemy database session

    Returns:
        JSONResponse: Response containing the status code and the ID of the saved webhook

    Raises:
        HTTPException: Code 400 if the body is not valid UTF-8 or not valid JSON.

    Webhooks can be sent in the terminal with a curl command, they can be sent from GitHub,
    or from another application.
    """
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

    return JSONResponse(status_code=201, content={"status": "saved", "id": webhook.id})


@app.get("/api/webhooks")
def get_webhooks(db: Session = Depends(get_db)):
    """This route returns the list of all received webhooks: their body, headers, and query
    parameters.

    Generates a session of the Postgres database and queries all rows in the webhooks table.
    Each row is converted into a dictionary containing its fields and added to a list.

    Args:
        db: SQLAlchemy database session

    Returns:
        JSONResponse: List of dictionaries representing each webhook and status code 200
    """

    webhooks = db.query(WebhookTable).all()

    content = [
        {
            "id": row.id,
            "body": row.body,
            "headers": row.headers,
            "query_params": row.query_params,
        }
        for row in webhooks
    ]

    return JSONResponse(status_code=200, content=content)


@app.get("/api/webhooks/{webhook_id}")
def get_webhook(webhook_id: int, db: Session = Depends(get_db)):
    """This route returns the details of a specific webhook by its ID.

    It queries the Postgres database for a webhook with the given ID.
    If found, it returns a dictionary containing the webhook's body, headers, and query parameters.
    If the webhook with the given ID does not exist, it returns an error message.

    Args:
        webhook_id: number representing a webhook in the database
        db: SQLAlchemy database session

    Returns:
        JSONResponse: Response containing the webhook data or an error response, with the
        appropriate status code
    """
    webhook = db.query(WebhookTable).filter(WebhookTable.id == webhook_id).first()

    if not webhook:
        return JSONResponse(status_code=404, content={"detail": "Webhook not found"})

    content = {
        "id": webhook.id,
        "body": webhook.body,
        "headers": json.loads(webhook.headers),
        "query_params": json.loads(webhook.query_params),
    }

    return JSONResponse(status_code=200, content=content)


# ----------- HTML ROUTES ----------- #
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Renders the home page displaying all received webhooks and the URL to send webhooks to.

    Returns an HTML page rendered from the "index.html" Jinja2 template.
    The page displays a list of all webhooks stored in the database and a URL to which webhooks
    can be sent.
    All webhooks can be clicked on to view their details, and there is a button to refresh the list.

    Args:
        request: FastAPI Request object representing the incoming HTTP request
        db: SQLAlchemy database session

    Returns:
        TemplateResponse: HTML page rendered from the "index.html" template, with status code 200
    """
    webhooks = db.query(WebhookTable).all()

    webhook_url = f"{request.url.scheme}://{request.url.netloc}/api/webhooks"

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "webhooks": webhooks, "webhook_url": webhook_url},
        status_code=200,
    )


@app.get("/{webhook_id}", response_class=HTMLResponse)
async def webhook_detail(
    webhook_id: int, request: Request, db: Session = Depends(get_db)
):
    """This route returns a web page displaying the details of a specific webhook.

    The page shows the webhook's body, headers, and query parameters in a pretty-printed JSON
    format with indentation for readability.
    It queries the Postgres database for the webhook and raises an HTTPException if not found.
    It formats the content for display and renders the "webhook.html" Jinja2 template.

    Args:
        webhook_id: number representing a webhook in the database
        request: FastAPI Request object representing the incoming HTTP request
        db: SQLAlchemy database session

    Returns:
        TemplateResponse: HTML page rendered from the "webhook.html" template, with status code 200

    Raises:
        HTTPException: Raised with status code 404 if the webhook is not found
    """
    webhook = db.query(WebhookTable).filter(WebhookTable.id == webhook_id).first()

    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

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
        status_code=200,
    )


# ----------- GLOBAL EXCEPTION HANDLER ----------- #
@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, _exc: Exception):
    """This is a global exception handler that catches unhandled exceptions in the application.

    This handler is triggered whenever an unexpected error occurs in any route.
    It returns a JSON response with a 500 status code and a generic error message.

    Args:
        _request: FastAPI Request object representing the incoming HTTP request that caused the
        exception
        _exc: The exception that was raised and not handled elsewhere

    Returns:
        JSONResponse: JSON response with a 500 status code and a generic error message
    """
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
