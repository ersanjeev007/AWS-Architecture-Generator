from fastapi import APIRouter
from datetime import datetime
from app.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes deployments"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "api": "ok",
            "memory": "ok"
        }
    }

@router.get("/live")
async def liveness_check():
    """Liveness check endpoint for Kubernetes deployments"""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }