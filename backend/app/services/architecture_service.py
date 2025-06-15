from typing import Dict, List, Optional
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import ArchitectureResponse
from app.core.architecture_generator import ArchitectureGenerator

class ArchitectureService:
    """Service layer for architecture operations"""
    
    def __init__(self):
        self.architectures_storage: Dict[str, ArchitectureResponse] = {}
        self.generator = ArchitectureGenerator()
    
    async def generate_architecture(
        self, 
        questionnaire: QuestionnaireRequest, 
        generator: Optional[ArchitectureGenerator] = None
    ) -> ArchitectureResponse:
        """Generate a new architecture from questionnaire"""
        
        # Use provided generator or default one
        arch_generator = generator or self.generator
        
        # Generate the architecture
        architecture = arch_generator.generate(questionnaire)
        
        # Store in memory (replace with database in production)
        self.architectures_storage[architecture.id] = architecture
        
        return architecture
    
    async def get_architecture(self, architecture_id: str) -> Optional[ArchitectureResponse]:
        """Retrieve an architecture by ID"""
        return self.architectures_storage.get(architecture_id)
    
    async def list_architectures(self) -> List[str]:
        """List all architecture IDs"""
        return list(self.architectures_storage.keys())
    
    async def delete_architecture(self, architecture_id: str) -> bool:
        """Delete an architecture by ID"""
        if architecture_id in self.architectures_storage:
            del self.architectures_storage[architecture_id]
            return True
        return False