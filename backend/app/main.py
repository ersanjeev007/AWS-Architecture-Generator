from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import architecture, health, projects  # Add projects import
from app.database import create_tables

def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Generate custom AWS architectures with Infrastructure as Code",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Create database tables on startup
    create_tables()

    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    application.include_router(
        architecture.router, 
        prefix=f"{settings.API_V1_STR}/architecture",
        tags=["architecture"]
    )
    application.include_router(
        projects.router,  # Add projects router
        prefix=f"{settings.API_V1_STR}/projects",
        tags=["projects"]
    )
    application.include_router(
        health.router, 
        prefix=f"{settings.API_V1_STR}/health",
        tags=["health"]
    )

    return application

app = create_application()

@app.get("/")
async def root():
    return {
        "message": "AWS Architecture Generator API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )