from typing import Dict
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import DiagramData, DiagramNode, DiagramEdge

class DiagramGenerator:
    """Generate architecture diagram data for React Flow"""
    
    def generate_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest) -> DiagramData:
        nodes = []
        edges = []
        x_pos, y_pos = 100, 100
        x_increment, y_increment = 200, 150
        
        # Users node
        nodes.append(DiagramNode(
            id="users",
            type="input",
            data={"label": "Users"},
            position={"x": x_pos, "y": y_pos}
        ))
        
        current_x = x_pos + x_increment
        last_node_id = "users"
        
        # Internet Gateway
        nodes.append(DiagramNode(
            id="igw",
            data={"label": "Internet Gateway"},
            position={"x": current_x, "y": y_pos}
        ))
        edges.append(DiagramEdge(id="users-igw", source=last_node_id, target="igw"))
        last_node_id = "igw"
        current_x += x_increment
        
        # CDN
        if "cdn" in services:
            nodes.append(DiagramNode(
                id="cdn",
                data={"label": f"CloudFront\n({services['cdn']})"},
                position={"x": current_x, "y": y_pos}
            ))
            edges.append(DiagramEdge(id=f"{last_node_id}-cdn", source=last_node_id, target="cdn"))
            last_node_id = "cdn"
            current_x += x_increment
        
        # Load Balancer
        if "load_balancer" in services:
            nodes.append(DiagramNode(
                id="alb",
                data={"label": f"Load Balancer\n({services['load_balancer']})"},
                position={"x": current_x, "y": y_pos}
            ))
            edges.append(DiagramEdge(id=f"{last_node_id}-alb", source=last_node_id, target="alb"))
            last_node_id = "alb"
            current_x += x_increment
        
        # Compute
        nodes.append(DiagramNode(
            id="compute",
            data={"label": f"Compute\n({services['compute']})"},
            position={"x": current_x, "y": y_pos}
        ))
        edges.append(DiagramEdge(id=f"{last_node_id}-compute", source=last_node_id, target="compute"))
        
        # Database
        if "database" in services:
            db_y = y_pos + y_increment
            nodes.append(DiagramNode(
                id="database",
                data={"label": f"Database\n({services['database']})"},
                position={"x": current_x, "y": db_y}
            ))
            edges.append(DiagramEdge(id="compute-database", source="compute", target="database"))
        
        # Storage
        storage_x = current_x - x_increment
        storage_y = y_pos + y_increment
        nodes.append(DiagramNode(
            id="storage",
            data={"label": f"Storage\n({services['storage']})"},
            position={"x": storage_x, "y": storage_y}
        ))
        edges.append(DiagramEdge(id="compute-storage", source="compute", target="storage"))
        
        return DiagramData(nodes=nodes, edges=edges)