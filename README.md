# Virtual Queue System

A virtual queuing system with SMS notifications, built with FastAPI and React.

## Features

- 🎫 Virtual queue management
- 📱 SMS notifications when it's your turn
- 👤 User authentication for queue administrators
- 🔐 JWT-based authentication
- 📊 Real-time queue status
- 🎯 RESTful API
- 🧪 Mock SMS provider for development (Twilio-ready for production)

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic
- **Authentication**: JWT with OAuth2
- **Database**: SQLite (dev), PostgreSQL (prod)
- **SMS**: Twilio
- **Package Management**: UV
- **Linting/Formatting**: Ruff
- **Type Checking**: mypy

## Getting Started

### Prerequisites

- Python 3.9+
- UV package manager

### Installation

1. Clone the repository:
```bash
git clone <repo-url>
cd queue
```

2. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Install dependencies:
```bash
uv sync --dev
```

4. Copy environment variables:
```bash
cp .env.example .env
```

5. Edit `.env` with your configuration

### SMS Configuration

By default, the app uses a mock SMS provider in development that logs messages to the console. To use Twilio in production:

1. Set `ENVIRONMENT=production` in `.env`
2. Add your Twilio credentials:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`

The mock provider is perfect for testing without incurring SMS costs.

### Running the Server

```bash
python run.py
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/token` - Login and get JWT token

### Queues
- `GET /api/queues` - List all active queues
- `POST /api/queues` - Create a new queue (auth required)
- `GET /api/queues/{id}` - Get queue details
- `PATCH /api/queues/{id}` - Update queue (admin only)
- `DELETE /api/queues/{id}` - Delete queue (admin only)

### Queue Entries
- `POST /api/entries/join` - Join a queue (no auth required)
- `GET /api/entries/queue/{queue_id}` - List entries in a queue
- `GET /api/entries/{id}` - Get entry status
- `PATCH /api/entries/{id}/call` - Call customer (admin only)
- `PATCH /api/entries/{id}/serve` - Mark as served (admin only)
- `PATCH /api/entries/{id}/cancel` - Cancel entry

## Database Schema

### User
Represents both customers and queue administrators.
- `id`: Primary key
- `email`: Unique email address
- `username`: Unique username for login
- `password`: Hashed password
- `phone_number`: Optional phone number
- `is_active`: Account status
- `managed_queues`: Many-to-many relationship with queues they can manage

### Queue
Represents a business's virtual queue.
- `id`: Primary key
- `name`: Unique queue identifier (e.g., "joes-pizza-main")
- `business_name`: Display name of the business
- `description`: Optional description
- `address`: Optional business address
- `status`: ACTIVE, PAUSED, or CLOSED
- `estimated_wait_minutes`: Average wait time per customer
- `admins`: Users who can manage this queue
- `entries`: Customers currently in the queue

### QueueEntry
Represents a customer's position in a queue.
- `id`: Primary key
- `queue_id`: Foreign key to Queue
- `customer_name`: Name of the customer
- `phone_number`: Phone for SMS notifications
- `party_size`: Number of people in the party
- `position`: Order in the queue
- `status`: WAITING, CALLED, SERVED, or CANCELLED
- `joined_at`: When they joined the queue
- `called_at`: When they were called
- `served_at`: When they were served

### Relationships
- **User ↔ Queue**: Many-to-many through `queue_admins` table
- **Queue → QueueEntry**: One-to-many (a queue has many entries)

## Development

### Running Tests
```bash
pytest
```

### Linting and Formatting
```bash
ruff check .
ruff format .
```

### Type Checking
```bash
mypy app/
```