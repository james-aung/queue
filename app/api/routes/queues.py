from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_db
from app.models.queue import Queue, QueueEntry, QueueStatus, queue_admins
from app.models.user import User
from app.schemas.queue import (
    Queue as QueueSchema,
)
from app.schemas.queue import (
    QueueCreate,
    QueueUpdate,
)

router = APIRouter()


@router.post("/", response_model=QueueSchema)
def create_queue(
    queue: QueueCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new queue. The current user becomes the admin."""
    # Check if queue name already exists
    existing = db.query(Queue).filter(Queue.name == queue.name).first()
    if existing:
        raise HTTPException(
            status_code=400, detail="Queue with this name already exists"
        )

    db_queue = Queue(
        name=queue.name,
        business_name=queue.business_name,
        description=queue.description,
        address=queue.address,
        estimated_wait_minutes=queue.estimated_wait_minutes,
    )
    db.add(db_queue)
    db.flush()  # Get the ID without committing

    # Make the creator an admin
    db.execute(
        queue_admins.insert().values(user_id=current_user.id, queue_id=db_queue.id)
    )

    db.commit()
    db.refresh(db_queue)

    # Add computed fields
    result = QueueSchema.model_validate(db_queue)
    result.current_size = 0
    result.admin_ids = [current_user.id]

    return result


@router.get("/", response_model=list[QueueSchema])
def list_queues(
    skip: int = 0,
    limit: int = 100,
    status: Optional[QueueStatus] = None,
    db: Session = Depends(get_db),
):
    """List all active queues."""
    query = db.query(Queue)

    if status:
        query = query.filter(Queue.status == status)
    else:
        # Default to showing only active queues
        query = query.filter(Queue.status == QueueStatus.ACTIVE)

    queues = query.offset(skip).limit(limit).all()

    result = []
    for queue in queues:
        queue_data = QueueSchema.model_validate(queue)
        # Add current size
        queue_data.current_size = (
            db.query(QueueEntry)
            .filter(
                QueueEntry.queue_id == queue.id,
                QueueEntry.status.in_(["waiting", "called"]),
            )
            .count()
        )
        # Add admin IDs
        queue_data.admin_ids = [admin.id for admin in queue.admins]
        result.append(queue_data)

    return result


@router.get("/{queue_id}", response_model=QueueSchema)
def get_queue(queue_id: int, db: Session = Depends(get_db)):
    """Get a specific queue by ID."""
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    result = QueueSchema.model_validate(queue)
    result.current_size = (
        db.query(QueueEntry)
        .filter(
            QueueEntry.queue_id == queue.id,
            QueueEntry.status.in_(["waiting", "called"]),
        )
        .count()
    )
    result.admin_ids = [admin.id for admin in queue.admins]

    return result


@router.patch("/{queue_id}", response_model=QueueSchema)
def update_queue(
    queue_id: int,
    queue_update: QueueUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a queue. Only admins can update."""
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    # Check if user is admin
    if current_user not in queue.admins:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this queue"
        )

    # Update fields
    update_data = queue_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(queue, field, value)

    db.commit()
    db.refresh(queue)

    result = QueueSchema.model_validate(queue)
    result.current_size = (
        db.query(QueueEntry)
        .filter(
            QueueEntry.queue_id == queue.id,
            QueueEntry.status.in_(["waiting", "called"]),
        )
        .count()
    )
    result.admin_ids = [admin.id for admin in queue.admins]

    return result


@router.delete("/{queue_id}", status_code=204)
def delete_queue(
    queue_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a queue. Only admins can delete."""
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    # Check if user is admin
    if current_user not in queue.admins:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this queue"
        )

    db.delete(queue)
    db.commit()


@router.post("/{queue_id}/admins/{user_id}", response_model=dict)
def add_admin(
    queue_id: int,
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add an admin to a queue. Only existing admins can add new admins."""
    queue = db.query(Queue).filter(Queue.id == queue_id).first()
    if not queue:
        raise HTTPException(status_code=404, detail="Queue not found")

    # Check if current user is admin
    if current_user not in queue.admins:
        raise HTTPException(
            status_code=403, detail="Not authorized to manage admins for this queue"
        )

    # Check if user exists
    new_admin = db.query(User).filter(User.id == user_id).first()
    if not new_admin:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already admin
    if new_admin in queue.admins:
        raise HTTPException(
            status_code=400, detail="User is already an admin of this queue"
        )

    # Add admin
    db.execute(queue_admins.insert().values(user_id=user_id, queue_id=queue_id))
    db.commit()

    return {"message": "Admin added successfully"}
