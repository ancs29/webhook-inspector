"""
This module defines the SQLAlchemy ORM model for storing incoming webhook requests.

Attributes:
    WebhookTable: SQLAlchemy ORM model

Separated from db.py to separate general database configuration from specific table models.
"""

from sqlalchemy import Column, Integer, Text

from .db import Base


class WebhookTable(Base):
    """
    SQLAlchemy ORM model representing the webhooks database

    Each row stores a request with its body, headers, and query parameters, along with an id.
    All dicts are serialized to JSON strings before storage in Text columns.

    Attributes:
        id: Primary key
        body: JSON data
        headers: JSON headers
        query_params: query parameters
    """

    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text)
    headers = Column(Text)
    query_params = Column(Text)
