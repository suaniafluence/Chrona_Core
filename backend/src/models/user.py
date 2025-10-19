from datetime import datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(nullable=False)
    role: str = Field(default="user", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
