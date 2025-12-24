"""This module sets up and configures the database connection for the application.

This module configures SQLAlchemy to connect to a PostgreSQL database. It creates a
connection engine, a session factory for database interactions, and a base class to map Python
classes to database tables.

Attributes:
    DATABASE_URL: Connection string for PostgreSQL database. Looks for a DATABASE_URL
    environment variable, uses local host as a backup.
    engine: SQLAlchemy engine that manages connections to the Postgres database.
    SessionLocal: Object that produces sessions, allowing interaction with the database.
    Base: Declarative base class that allows mapping between Python classes and database tables.

Separated from model.py to separate general database configuration from specific table models.
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/webhooks_inspector")

engine = create_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()
