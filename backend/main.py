"""
SEABISCUIT - Institutional Equine Stock Exchange Main FastAPI Microservice
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api_router import router as seabiscuit_router

app = FastAPI(
    title="SEABISCUIT // Institutional Equine Stock Exchange API",
    description="High-performance microservices powering Wall Street Horse Racing Stock Trading Floor & The Racing API Data.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seabiscuit_router)


@app.get("/", tags=["Health Check"])
def root():
    return {
        "status": "online",
        "system": "SEABISCUIT // Institutional Equine Intelligence",
        "version": "2.0.0",
        "docs_url": "/docs"
    }
