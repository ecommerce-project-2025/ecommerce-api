from datetime import datetime, timezone
from sqlmodel import Relationship, SQLModel, Field
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

# if TYPE_CHECKING:
#     from device.domain.model.robot import Robot

class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(primary_key=True)
    verification_uuid: Optional[str] = Field(nullable=False, sa_column_kwargs={"unique": True, "nullable": False})
    email: str = Field(nullable=False, sa_column_kwargs={"unique": True, "nullable": False})
    username: str = Field(nullable=False, sa_column_kwargs={"unique": True, "nullable": False})
    hashed_password: str = Field(nullable=False)
    # image_url: Optional[str] = Field(nullable=True)
    # full_name: Optional[str] = Field(nullable=True)
    uuid_expires_at: Optional[datetime] = Field(nullable=True)
    email_verified_at: Optional[datetime] = Field(nullable=True)
    created_at: Optional[datetime] = Field(nullable=False, default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(nullable=False, default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": datetime.now(timezone.utc)})
    role: Optional[Role] = Field(nullable=False, default=Role.USER)

    # robots: List["Robot"] = Relationship(back_populates="user")