from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_db
from app.models.queue import EntryStatus, Queue, QueueEntry, QueueStatus
from app.models.user import User
from app.schemas.queue import (
    QueueEntry as QueueEntrySchema,
)
from app.schemas.queue import (
    QueueEntryCreate,
)
from app.services.sms import sms_service

router = APIRouter()


@router.post("/join", response_model=QueueEntrySchema)
def join_queue(
    entry: QueueEntryCreate,
    db: Session = Depends(get_db),
):
    """Join a queue as a customer. No authentication required."""
    # Check if queue exists and is active
    queue = db.query(Queue).filter(Queue.id == entry.queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    if queue.status != QueueStatus.ACTIVE:
        raise HTTPException(
            status_code=400, detail="Queue is not accepting new entries"
        )

    # Get the next position
    last_entry = (
        db.query(QueueEntry)
        .filter(QueueEntry.queue_id == entry.queue_id)
        .order_by(QueueEntry.position.desc())
        .first()
    )
    next_position = (last_entry.position + 1) if last_entry else 1

    # Create entry
    db_entry = QueueEntry(
        queue_id=entry.queue_id,
        customer_name=entry.customer_name,
        phone_number=entry.phone_number,
        party_size=entry.party_size,
        position=next_position,
        status=EntryStatus.WAITING,
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Calculate estimated wait time
    entries_ahead = (
        db.query(QueueEntry)
        .filter(
            QueueEntry.queue_id == entry.queue_id,
            QueueEntry.position < db_entry.position,
            QueueEntry.status.in_([EntryStatus.WAITING, EntryStatus.CALLED]),
        )
        .count()
    )

    result = QueueEntrySchema.model_validate(db_entry)
    result.estimated_wait_minutes = entries_ahead * queue.estimated_wait_minutes

    # Send SMS notification
    sms_service.send_queue_joined_notification(
        phone_number=entry.phone_number,
        queue_name=queue.business_name,
        position=db_entry.position,
        estimated_wait_minutes=result.estimated_wait_minutes,
    )

    return result


@router.get("/queue/{queue_id}", response_model=list[QueueEntrySchema])
def list_queue_entries(
    queue_id: int,
    status: Optional[EntryStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List entries in a queue."""
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    query = db.query(QueueEntry).filter(QueueEntry.queue_id == queue_id)

    if status:
        query = query.filter(QueueEntry.status == status)
    else:
        # Default to showing waiting and called entries
        query = query.filter(
            QueueEntry.status.in_([EntryStatus.WAITING, EntryStatus.CALLED])
        )

    entries = query.order_by(QueueEntry.position).offset(skip).limit(limit).all()

    result = []
    for i, entry in enumerate(entries):
        entry_data = QueueEntrySchema.model_validate(entry)
        # Calculate estimated wait based on position in active queue
        if entry.status in [EntryStatus.WAITING, EntryStatus.CALLED]:
            entry_data.estimated_wait_minutes = i * queue.estimated_wait_minutes
        else:
            entry_data.estimated_wait_minutes = 0
        result.append(entry_data)

    return result


@router.get("/{entry_id}", response_model=QueueEntrySchema)
def get_entry(entry_id: int, db: Session = Depends(get_db)):
    """Get a specific queue entry."""
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Calculate position in active queue
    if entry.status in [EntryStatus.WAITING, EntryStatus.CALLED]:
        entries_ahead = (
            db.query(QueueEntry)
            .filter(
                QueueEntry.queue_id == entry.queue_id,
                QueueEntry.position < entry.position,
                QueueEntry.status.in_([EntryStatus.WAITING, EntryStatus.CALLED]),
            )
            .count()
        )
        estimated_wait = entries_ahead * entry.queue.estimated_wait_minutes
    else:
        estimated_wait = 0

    result = QueueEntrySchema.model_validate(entry)
    result.estimated_wait_minutes = estimated_wait

    return result


@router.patch("/{entry_id}/call", response_model=QueueEntrySchema)
def call_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Call a customer to the front. Only queue admins can call."""
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Check if user is admin of this queue
    if current_user not in entry.queue.admins:
        raise HTTPException(
            status_code=403, detail="Not authorized to manage this queue"
        )

    if entry.status != EntryStatus.WAITING:
        raise HTTPException(status_code=400, detail=f"Entry is already {entry.status}")

    # Update status
    entry.status = EntryStatus.CALLED
    entry.called_at = func.now()

    db.commit()
    db.refresh(entry)

    result = QueueEntrySchema.model_validate(entry)
    result.estimated_wait_minutes = 0

    # Send SMS notification
    sms_service.send_customer_called_notification(
        phone_number=entry.phone_number, queue_name=entry.queue.business_name
    )

    return result


@router.patch("/{entry_id}/serve", response_model=QueueEntrySchema)
def serve_entry(
    entry_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Mark a customer as served. Only queue admins can mark as served."""
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    # Check if user is admin of this queue
    if current_user not in entry.queue.admins:
        raise HTTPException(
            status_code=403, detail="Not authorized to manage this queue"
        )

    if entry.status == EntryStatus.SERVED:
        raise HTTPException(status_code=400, detail="Entry is already served")

    # Update status
    entry.status = EntryStatus.SERVED
    entry.served_at = func.now()

    db.commit()
    db.refresh(entry)

    result = QueueEntrySchema.model_validate(entry)
    result.estimated_wait_minutes = 0

    return result


@router.patch("/{entry_id}/cancel", response_model=QueueEntrySchema)
def cancel_entry(
    entry_id: int,
    db: Session = Depends(get_db),
):
    """Cancel a queue entry. Can be done by anyone with the entry ID."""
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if entry.status in [EntryStatus.SERVED, EntryStatus.CANCELLED]:
        raise HTTPException(status_code=400, detail=f"Entry is already {entry.status}")

    # Update status
    entry.status = EntryStatus.CANCELLED

    db.commit()
    db.refresh(entry)

    result = QueueEntrySchema.model_validate(entry)
    result.estimated_wait_minutes = 0

    return result
