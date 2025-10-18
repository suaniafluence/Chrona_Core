from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

