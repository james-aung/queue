#!/usr/bin/env python3
"""
Script to create dummy data for testing the queue management system.
"""

from datetime import datetime, timedelta

from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.queue import EntryStatus, Queue, QueueEntry, QueueStatus
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_dummy_data():
    """Create dummy data for testing."""
    # Create synchronous engine and session
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as session:
        # Clear existing data
        session.query(QueueEntry).delete()
        session.query(Queue).delete()
        session.query(User).delete()
        session.commit()

        # Create shopkeeper users
        shopkeepers = [
            User(
                email="pizza@shop.com",
                username="pizzashop",
                hashed_password=pwd_context.hash("password123"),
                phone_number="+1234567890",
            ),
            User(
                email="coffee@cafe.com",
                username="coffeecafe",
                hashed_password=pwd_context.hash("password123"),
                phone_number="+1234567891",
            ),
            User(
                email="barber@shop.com",
                username="barbershop",
                hashed_password=pwd_context.hash("password123"),
                phone_number="+1234567892",
            ),
        ]

        for shopkeeper in shopkeepers:
            session.add(shopkeeper)

        session.commit()

        # Refresh to get IDs
        for shopkeeper in shopkeepers:
            session.refresh(shopkeeper)

        # Create queues
        queues = [
            Queue(
                name="pizza-orders",
                business_name="Tony's Pizza Palace",
                description="Fresh pizza made to order",
                address="123 Main St, Downtown",
                status=QueueStatus.ACTIVE,
                estimated_wait_minutes=15,
            ),
            Queue(
                name="coffee-queue",
                business_name="Bean There Coffee",
                description="Artisanal coffee and pastries",
                address="456 Oak Ave, Midtown",
                status=QueueStatus.ACTIVE,
                estimated_wait_minutes=8,
            ),
            Queue(
                name="haircuts",
                business_name="Classic Cuts Barbershop",
                description="Traditional barbershop services",
                address="789 Pine St, Uptown",
                status=QueueStatus.PAUSED,
                estimated_wait_minutes=25,
            ),
        ]

        for queue in queues:
            session.add(queue)

        session.commit()

        # Refresh to get IDs
        for queue in queues:
            session.refresh(queue)

        # Assign admins to queues
        queues[0].admins.append(shopkeepers[0])  # Pizza shop
        queues[1].admins.append(shopkeepers[1])  # Coffee cafe
        queues[2].admins.append(shopkeepers[2])  # Barber shop

        session.commit()

        # Create queue entries
        now = datetime.now()

        # Pizza queue entries
        pizza_entries = [
            QueueEntry(
                queue_id=queues[0].id,
                customer_name="John Smith",
                phone_number="+1555000001",
                party_size=2,
                position=1,
                status=EntryStatus.CALLED,
                joined_at=now - timedelta(minutes=10),
                called_at=now - timedelta(minutes=2),
            ),
            QueueEntry(
                queue_id=queues[0].id,
                customer_name="Sarah Johnson",
                phone_number="+1555000002",
                party_size=1,
                position=2,
                status=EntryStatus.WAITING,
                joined_at=now - timedelta(minutes=5),
            ),
            QueueEntry(
                queue_id=queues[0].id,
                customer_name="Mike Wilson",
                phone_number="+1555000003",
                party_size=4,
                position=3,
                status=EntryStatus.WAITING,
                joined_at=now - timedelta(minutes=3),
            ),
        ]

        # Coffee queue entries
        coffee_entries = [
            QueueEntry(
                queue_id=queues[1].id,
                customer_name="Emma Davis",
                phone_number="+1555000004",
                party_size=1,
                position=1,
                status=EntryStatus.WAITING,
                joined_at=now - timedelta(minutes=8),
            ),
            QueueEntry(
                queue_id=queues[1].id,
                customer_name="David Brown",
                phone_number="+1555000005",
                party_size=2,
                position=2,
                status=EntryStatus.WAITING,
                joined_at=now - timedelta(minutes=4),
            ),
        ]

        # Barber queue entries (paused queue with some entries)
        barber_entries = [
            QueueEntry(
                queue_id=queues[2].id,
                customer_name="Robert Taylor",
                phone_number="+1555000006",
                party_size=1,
                position=1,
                status=EntryStatus.WAITING,
                joined_at=now - timedelta(minutes=30),
            ),
        ]

        all_entries = pizza_entries + coffee_entries + barber_entries
        for entry in all_entries:
            session.add(entry)

        session.commit()

        print("✅ Dummy data created successfully!")
        print("\n📊 Summary:")
        print(f"👥 Created {len(shopkeepers)} shopkeepers")
        print(f"🏪 Created {len(queues)} queues")
        print(f"📝 Created {len(all_entries)} queue entries")

        print("\n🔐 Login credentials:")
        for i, shopkeeper in enumerate(shopkeepers):
            queue_name = queues[i].business_name
            print(f"  {queue_name}: {shopkeeper.email} / password123")

    engine.dispose()


if __name__ == "__main__":
    create_dummy_data()
