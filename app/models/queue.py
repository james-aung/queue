from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class QueueStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"


class EntryStatus(str, enum.Enum):
    WAITING = "waiting"
    CALLED = "called"
    SERVED = "served"
    CANCELLED = "cancelled"


# Junction table for many-to-many relationship between Users and Queues
queue_admins = Table(
    "queue_admins",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("queue_id", Integer, ForeignKey("queues.id"), primary_key=True),
)


class Queue(Base):
    __tablename__ = "queues"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    business_name = Column(String, nullable=False)
    description = Column(String)
    address = Column(String)
    status = Column(Enum(QueueStatus), default=QueueStatus.ACTIVE)
    estimated_wait_minutes = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Many-to-many relationship with admin users
    admins: Mapped[list[User]] = relationship(
        "User", secondary=queue_admins, back_populates="managed_queues"
    )
    entries: Mapped[list[QueueEntry]] = relationship(
        "QueueEntry", back_populates="queue", cascade="all, delete-orphan"
    )


class QueueEntry(Base):
    __tablename__ = "queue_entries"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True)
    queue_id = Column(Integer, ForeignKey("queues.id"), nullable=False)
    customer_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    party_size = Column(Integer, default=1)
    position = Column(Integer, nullable=False)
    status = Column(Enum(EntryStatus), default=EntryStatus.WAITING)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    called_at = Column(DateTime(timezone=True), nullable=True)
    served_at = Column(DateTime(timezone=True), nullable=True)

    queue: Mapped[Queue] = relationship("Queue", back_populates="entries")
