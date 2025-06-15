import logging
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import ArchitectureResponse
from app.services.architecture_service import ArchitectureService
from app.core.architecture_generator import ArchitectureGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

# Dependency injection
def get_architecture_service() -> ArchitectureService:
    return ArchitectureService()

def get_architecture_generator() -> ArchitectureGenerator:
    return ArchitectureGenerator()

@router.post("/generate", response_model=ArchitectureResponse)
async def generate_architecture(
    questionnaire: QuestionnaireRequest,
    architecture_service: ArchitectureService = Depends(get_architecture_service),
    generator: ArchitectureGenerator = Depends(get_architecture_generator)
):
    """Generate AWS architecture based on questionnaire responses"""
    try:
        architecture = await architecture_service.generate_architecture(questionnaire, generator)
        return architecture
    except Exception as e:
        logger.exception("Error generating architecture")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate architecture: {str(e)}"
        )

@router.get("/{architecture_id}", response_model=ArchitectureResponse)
async def get_architecture(
    architecture_id: str,
    architecture_service: ArchitectureService = Depends(get_architecture_service)
):
    """Retrieve a previously generated architecture by ID"""
    try:
        architecture = await architecture_service.get_architecture(architecture_id)
        if not architecture:
            raise HTTPException(status_code=404, detail="Architecture not found")
        return architecture
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve architecture: {str(e)}"
        )

@router.get("/", response_model=list)
async def list_architectures(
    architecture_service: ArchitectureService = Depends(get_architecture_service)
):
    """List all architecture IDs"""
    try:
        architecture_ids = await architecture_service.list_architectures()
        return architecture_ids
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list architectures: {str(e)}"
        )