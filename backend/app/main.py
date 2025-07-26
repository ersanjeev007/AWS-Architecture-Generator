from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import architecture, health, projects, aws_accounts, auth, architecture_modification, infrastructure_import, ai_ml_optimization, dynamic_security, dynamic_cost, production_infrastructure
from app.api.v1.endpoints import cost_analysis, security_recommendations
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
    application.include_router(
        aws_accounts.router,
        prefix=f"{settings.API_V1_STR}/aws-accounts",
        tags=["aws-accounts"]
    )
    application.include_router(
        cost_analysis.router,
        prefix=f"{settings.API_V1_STR}/cost-analysis",
        tags=["cost-analysis"]
    )
    application.include_router(
        security_recommendations.router,
        prefix=f"{settings.API_V1_STR}/security",
        tags=["security-recommendations"]
    )
    application.include_router(
        auth.router,
        prefix=f"{settings.API_V1_STR}/auth",
        tags=["authentication"]
    )
    application.include_router(
        architecture_modification.router,
        prefix=f"{settings.API_V1_STR}/architecture",
        tags=["architecture-modification"]
    )
    application.include_router(
        infrastructure_import.router,
        prefix=f"{settings.API_V1_STR}",
        tags=["infrastructure-import"]
    )
    application.include_router(
        ai_ml_optimization.router,
        prefix=f"{settings.API_V1_STR}",
        tags=["ai-ml-optimization"]
    )
    application.include_router(
        dynamic_security.router,
        prefix=f"{settings.API_V1_STR}/dynamic-security",
        tags=["dynamic-security"]
    )
    application.include_router(
        dynamic_cost.router,
        prefix=f"{settings.API_V1_STR}/dynamic-cost",
        tags=["dynamic-cost"]
    )
    application.include_router(
        production_infrastructure.router,
        prefix=f"{settings.API_V1_STR}/production-infrastructure",
        tags=["production-infrastructure"]
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