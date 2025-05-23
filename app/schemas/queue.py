from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.queue import EntryStatus, QueueStatus


class QueueBase(BaseModel):
    name: str
    business_name: str
    description: Optional[str] = None
    address: Optional[str] = None
    estimated_wait_minutes: int = 5


class QueueCreate(QueueBase):
    pass


class QueueUpdate(BaseModel):
    name: Optional[str] = None
    business_name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    status: Optional[QueueStatus] = None
    estimated_wait_minutes: Optional[int] = None


class QueueInDB(QueueBase):
    id: int
    status: QueueStatus
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class Queue(QueueInDB):
    current_size: Optional[int] = 0
    admin_ids: Optional[list[int]] = []


class QueueEntryBase(BaseModel):
    customer_name: str
    phone_number: str
    party_size: int = 1


class QueueEntryCreate(QueueEntryBase):
    queue_id: int


class QueueEntryUpdate(BaseModel):
    status: Optional[EntryStatus] = None


class QueueEntryInDB(QueueEntryBase):
    id: int
    queue_id: int
    position: int
    status: EntryStatus
    joined_at: datetime
    called_at: Optional[datetime]
    served_at: Optional[datetime]

    model_config = {"from_attributes": True}


class QueueEntry(QueueEntryInDB):
    estimated_wait_minutes: Optional[int] = None
