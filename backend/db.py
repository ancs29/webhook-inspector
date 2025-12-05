from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./webhooks.db"

engine = create_engine(
    DATABASE_URL,
    echo=True,  # optional: prints SQL statements
    future=True,  # enables 2.x style usage
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()
