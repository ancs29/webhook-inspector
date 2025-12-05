from sqlalchemy import Column, Integer, Text

from .db import Base


class WebhookTable(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text)
    headers = Column(Text)
    query_params = Column(Text)
