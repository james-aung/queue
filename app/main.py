from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, entries, queues
from app.db.base import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Virtual Queue API",
    description="API for virtual queuing system with SMS notifications",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(queues.router, prefix="/api/queues", tags=["queues"])
app.include_router(entries.router, prefix="/api/entries", tags=["entries"])


@app.get("/")
def root():
    return {"message": "Virtual Queue API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
