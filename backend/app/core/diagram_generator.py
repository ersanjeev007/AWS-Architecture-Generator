from typing import Dict, List, Tuple
from app.schemas.questionnaire import QuestionnaireRequest
from app.schemas.architecture import DiagramData, DiagramNode, DiagramEdge
import json

class DiagramGenerator:
    """Generate architecture diagram data for React Flow"""
    
    def __init__(self):
        # Service to icon mapping
        self.service_icons = {
            # Compute
            'EC2': 'EC2',
            'ECS': 'ECS',
            'EKS': 'EKS',
            'Lambda': 'Lambda',
            'Fargate': 'Fargate',
            # Database
            'RDS': 'RDS',
            'DynamoDB': 'DynamoDB',
            'Aurora': 'Aurora',
            'ElastiCache': 'ElastiCache',
            # Storage
            'S3': 'S3',
            'EFS': 'EFS',
            'EBS': 'EBS',
            # Network
            'VPC': 'VPC',
            'ALB': 'ALB',
            'NLB': 'NLB',
            'CloudFront': 'CloudFront',
            'Route53': 'Route53',
            'API Gateway': 'API Gateway',
            # Security
            'WAF': 'WAF',
            'Security Groups': 'Security Groups',
            'NACLs': 'NACLs',
            'IAM': 'IAM',
            'KMS': 'KMS',
            'Secrets Manager': 'Secrets Manager',
            'Certificate Manager': 'Certificate Manager',
            # Monitoring
            'CloudWatch': 'CloudWatch',
            'X-Ray': 'X-Ray',
            'CloudTrail': 'CloudTrail',
        }
    
    def generate_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest) -> DiagramData:
        """Generate a dynamic, project-specific architecture diagram with security components"""
        nodes = []
        edges = []
        
        # Analyze requirements to build appropriate architecture
        arch_type = self._determine_architecture_type(questionnaire)
        security_level = self._determine_security_level(questionnaire)
        
        if arch_type == "web_application":
            return self._generate_web_app_diagram(services, questionnaire, security_level)
        elif arch_type == "api_backend":
            return self._generate_api_diagram(services, questionnaire, security_level)
        elif arch_type == "data_analytics":
            return self._generate_analytics_diagram(services, questionnaire, security_level)
        elif arch_type == "microservices":
            return self._generate_microservices_diagram(services, questionnaire, security_level)
        else:
            return self._generate_generic_diagram(services, questionnaire, security_level)
    
    def _determine_architecture_type(self, questionnaire: QuestionnaireRequest) -> str:
        """Determine the type of architecture based on questionnaire responses"""
        app_type = getattr(questionnaire, 'application_type', '').lower()
        
        if 'web' in app_type or 'frontend' in app_type:
            return "web_application"
        elif 'api' in app_type or 'backend' in app_type:
            return "api_backend"
        elif 'analytics' in app_type or 'data' in app_type or 'ml' in app_type:
            return "data_analytics"
        elif 'microservice' in app_type or 'container' in app_type:
            return "microservices"
        else:
            return "generic"
    
    def _determine_security_level(self, questionnaire: QuestionnaireRequest) -> str:
        """Determine security requirements based on questionnaire"""
        compliance = getattr(questionnaire, 'compliance_requirements', [])
        data_sensitivity = getattr(questionnaire, 'data_sensitivity', '').lower()
        
        if any(req in ['hipaa', 'pci-dss', 'sox'] for req in compliance) or 'high' in data_sensitivity:
            return "high"
        elif 'medium' in data_sensitivity or len(compliance) > 0:
            return "medium"
        else:
            return "basic"
    
    def _generate_web_app_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest, security_level: str) -> DiagramData:
        """Generate web application architecture diagram"""
        nodes = []
        edges = []
        
        # Internet layer
        internet_y = 50
        nodes.append(self._create_node("internet", "Internet", 400, internet_y, "input", "#e3f2fd"))
        
        # Security perimeter
        if security_level in ["medium", "high"]:
            nodes.append(self._create_node("route53", "Route53\n(DNS)", 400, internet_y + 80, "default", "#fff3e0"))
            nodes.append(self._create_node("waf", "🛡️ WAF\n(Web Firewall)", 400, internet_y + 160, "default", "#ffebee"))
            edges.extend([
                self._create_edge("internet", "route53"),
                self._create_edge("route53", "waf")
            ])
            entry_point = "waf"
        else:
            entry_point = "internet"
        
        # CDN layer
        cdn_y = internet_y + 240
        if "cdn" in services:
            nodes.append(self._create_node("cloudfront", f"🌐 {services['cdn']}\n(CDN)", 400, cdn_y, "default", "#e8f5e8"))
            edges.append(self._create_edge(entry_point, "cloudfront"))
            entry_point = "cloudfront"
        
        # Load balancer
        lb_y = cdn_y + 120
        if "load_balancer" in services:
            nodes.append(self._create_node("alb", f"⚖️ {services['load_balancer']}\n(Load Balancer)", 400, lb_y, "default", "#f3e5f5"))
            edges.append(self._create_edge(entry_point, "alb"))
            entry_point = "alb"
        
        # VPC boundary
        vpc_y = lb_y + 120
        nodes.append(self._create_node("vpc", "🏠 VPC\n(Virtual Network)", 400, vpc_y, "default", "#e1f5fe"))
        edges.append(self._create_edge(entry_point, "vpc"))
        
        # Compute layer (multi-AZ if high security)
        compute_y = vpc_y + 120
        if security_level == "high":
            nodes.extend([
                self._create_node("compute_az1", f"🖥️ {services['compute']}\n(AZ-1)", 250, compute_y, "default", "#f9fbe7"),
                self._create_node("compute_az2", f"🖥️ {services['compute']}\n(AZ-2)", 550, compute_y, "default", "#f9fbe7")
            ])
            edges.extend([
                self._create_edge("vpc", "compute_az1"),
                self._create_edge("vpc", "compute_az2")
            ])
            compute_nodes = ["compute_az1", "compute_az2"]
        else:
            nodes.append(self._create_node("compute", f"🖥️ {services['compute']}\n(Compute)", 400, compute_y, "default", "#f9fbe7"))
            edges.append(self._create_edge("vpc", "compute"))
            compute_nodes = ["compute"]
        
        # Security groups
        if security_level in ["medium", "high"]:
            sg_y = compute_y + 80
            nodes.append(self._create_node("security_groups", "🔒 Security Groups\n(Firewall Rules)", 400, sg_y, "default", "#ffebee"))
            for compute_node in compute_nodes:
                edges.append(self._create_edge(compute_node, "security_groups"))
        
        # Database layer
        if "database" in services:
            db_y = compute_y + 180
            if security_level == "high":
                nodes.extend([
                    self._create_node("db_primary", f"🗄️ {services['database']}\n(Primary)", 250, db_y, "default", "#fce4ec"),
                    self._create_node("db_replica", f"🗄️ {services['database']}\n(Replica)", 550, db_y, "default", "#fce4ec")
                ])
                for compute_node in compute_nodes:
                    edges.extend([
                        self._create_edge(compute_node, "db_primary"),
                        self._create_edge("db_primary", "db_replica")
                    ])
            else:
                nodes.append(self._create_node("database", f"🗄️ {services['database']}\n(Database)", 400, db_y, "default", "#fce4ec"))
                for compute_node in compute_nodes:
                    edges.append(self._create_edge(compute_node, "database"))
        
        # Storage layer
        storage_y = compute_y + 80
        storage_icon = self.service_icons.get(services.get('storage', 'S3'), '🪣')
        nodes.append(self._create_node("storage", f"{storage_icon} {services.get('storage', 'S3')}\n(Storage)", 150, storage_y, "default", "#fff8e1"))
        for compute_node in compute_nodes:
            edges.append(self._create_edge(compute_node, "storage"))
        
        # Monitoring and logging (if medium/high security)
        if security_level in ["medium", "high"]:
            monitoring_y = compute_y + 240
            nodes.extend([
                self._create_node("cloudwatch", "📊 CloudWatch\n(Monitoring)", 100, monitoring_y, "default", "#e0f2f1"),
                self._create_node("cloudtrail", "📝 CloudTrail\n(Audit Logs)", 700, monitoring_y, "default", "#e0f2f1")
            ])
            # Connect monitoring to all major components
            for node_id in ["vpc"] + compute_nodes + (["database"] if "database" in services else []):
                edges.extend([
                    self._create_edge(node_id, "cloudwatch"),
                    self._create_edge(node_id, "cloudtrail")
                ])
        
        # Secrets management (if high security)
        if security_level == "high":
            secrets_y = compute_y - 60
            nodes.extend([
                self._create_node("kms", "🔐 KMS\n(Encryption)", 100, secrets_y, "default", "#fef7ff"),
                self._create_node("secrets", "🤐 Secrets Manager\n(Credentials)", 700, secrets_y, "default", "#fef7ff")
            ])
            for compute_node in compute_nodes:
                edges.extend([
                    self._create_edge(compute_node, "kms"),
                    self._create_edge(compute_node, "secrets")
                ])
        
        return DiagramData(nodes=nodes, edges=edges)
    
    def _generate_api_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest, security_level: str) -> DiagramData:
        """Generate API-focused architecture diagram"""
        nodes = []
        edges = []
        
        # API Gateway entry point
        api_y = 100
        nodes.append(self._create_node("internet", "🌐 Internet", 400, api_y, "input", "#e3f2fd"))
        
        # Security layer
        if security_level in ["medium", "high"]:
            nodes.append(self._create_node("waf", "🛡️ WAF\n(API Protection)", 400, api_y + 80, "default", "#ffebee"))
            edges.append(self._create_edge("internet", "waf"))
            entry_point = "waf"
        else:
            entry_point = "internet"
        
        # API Gateway
        nodes.append(self._create_node("api_gateway", "🚪 API Gateway\n(REST/GraphQL)", 400, api_y + 160, "default", "#f3e5f5"))
        edges.append(self._create_edge(entry_point, "api_gateway"))
        
        # Authentication
        if security_level in ["medium", "high"]:
            nodes.append(self._create_node("cognito", "👤 Cognito\n(Auth)", 600, api_y + 160, "default", "#fff3e0"))
            edges.append(self._create_edge("api_gateway", "cognito"))
        
        # Lambda functions (microservices style)
        lambda_y = api_y + 280
        lambda_functions = [
            ("auth_lambda", "⚡ Auth Service", 200, lambda_y),
            ("users_lambda", "⚡ Users Service", 400, lambda_y),
            ("orders_lambda", "⚡ Orders Service", 600, lambda_y)
        ]
        
        for func_id, label, x, y in lambda_functions:
            nodes.append(self._create_node(func_id, label, x, y, "default", "#f9fbe7"))
            edges.append(self._create_edge("api_gateway", func_id))
        
        # Database layer
        if "database" in services:
            db_y = lambda_y + 150
            if services.get('database') == 'DynamoDB':
                nodes.append(self._create_node("dynamodb", "⚡ DynamoDB\n(NoSQL)", 400, db_y, "default", "#fce4ec"))
                for func_id, _, _, _ in lambda_functions:
                    edges.append(self._create_edge(func_id, "dynamodb"))
            else:
                nodes.append(self._create_node("rds", f"🗄️ {services['database']}\n(SQL)", 400, db_y, "default", "#fce4ec"))
                for func_id, _, _, _ in lambda_functions:
                    edges.append(self._create_edge(func_id, "rds"))
        
        # Caching layer
        if security_level in ["medium", "high"] or "cache" in services:
            cache_y = lambda_y + 80
            nodes.append(self._create_node("elasticache", "⚡ ElastiCache\n(Redis/Memcached)", 150, cache_y, "default", "#e8f5e8"))
            for func_id, _, _, _ in lambda_functions:
                edges.append(self._create_edge(func_id, "elasticache"))
        
        return DiagramData(nodes=nodes, edges=edges)
    
    def _generate_analytics_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest, security_level: str) -> DiagramData:
        """Generate data analytics architecture diagram"""
        nodes = []
        edges = []
        
        # Data sources
        sources_y = 100
        nodes.extend([
            self._create_node("data_sources", "📊 Data Sources\n(APIs, DBs, Files)", 200, sources_y, "input", "#e3f2fd"),
            self._create_node("streaming", "🌊 Kinesis\n(Real-time Streams)", 600, sources_y, "input", "#e3f2fd")
        ])
        
        # Data ingestion
        ingestion_y = sources_y + 150
        nodes.append(self._create_node("s3_raw", "🪣 S3 Raw\n(Data Lake)", 400, ingestion_y, "default", "#fff8e1"))
        edges.extend([
            self._create_edge("data_sources", "s3_raw"),
            self._create_edge("streaming", "s3_raw")
        ])
        
        # Processing layer
        processing_y = ingestion_y + 150
        nodes.extend([
            self._create_node("glue", "🔧 Glue\n(ETL Jobs)", 250, processing_y, "default", "#f9fbe7"),
            self._create_node("emr", "⚡ EMR\n(Big Data Processing)", 550, processing_y, "default", "#f9fbe7")
        ])
        edges.extend([
            self._create_edge("s3_raw", "glue"),
            self._create_edge("s3_raw", "emr")
        ])
        
        # Processed storage
        processed_y = processing_y + 150
        nodes.append(self._create_node("s3_processed", "🪣 S3 Processed\n(Analytics Ready)", 400, processed_y, "default", "#e8f5e8"))
        edges.extend([
            self._create_edge("glue", "s3_processed"),
            self._create_edge("emr", "s3_processed")
        ])
        
        # Analytics services
        analytics_y = processed_y + 150
        nodes.extend([
            self._create_node("athena", "🔍 Athena\n(SQL Queries)", 200, analytics_y, "default", "#e1f5fe"),
            self._create_node("redshift", "🗄️ Redshift\n(Data Warehouse)", 400, analytics_y, "default", "#fce4ec"),
            self._create_node("quicksight", "📈 QuickSight\n(BI Dashboards)", 600, analytics_y, "default", "#f3e5f5")
        ])
        edges.extend([
            self._create_edge("s3_processed", "athena"),
            self._create_edge("s3_processed", "redshift"),
            self._create_edge("redshift", "quicksight")
        ])
        
        # Security for analytics
        if security_level in ["medium", "high"]:
            security_y = processing_y - 80
            nodes.extend([
                self._create_node("lake_formation", "🔐 Lake Formation\n(Data Governance)", 400, security_y, "default", "#fef7ff"),
                self._create_node("macie", "🔍 Macie\n(Data Discovery)", 150, security_y, "default", "#ffebee")
            ])
            edges.extend([
                self._create_edge("lake_formation", "s3_raw"),
                self._create_edge("lake_formation", "s3_processed"),
                self._create_edge("macie", "s3_raw")
            ])
        
        return DiagramData(nodes=nodes, edges=edges)
    
    def _generate_microservices_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest, security_level: str) -> DiagramData:
        """Generate containerized microservices architecture"""
        nodes = []
        edges = []
        
        # Load balancer entry
        lb_y = 100
        nodes.append(self._create_node("internet", "🌐 Internet", 400, lb_y, "input", "#e3f2fd"))
        nodes.append(self._create_node("alb", "⚖️ Application LB\n(Layer 7)", 400, lb_y + 100, "default", "#f3e5f5"))
        edges.append(self._create_edge("internet", "alb"))
        
        # EKS/ECS Cluster
        cluster_y = lb_y + 200
        if "EKS" in services.get('compute', ''):
            nodes.append(self._create_node("eks", "☸️ EKS Cluster\n(Kubernetes)", 400, cluster_y, "default", "#e8f5e8"))
            cluster_id = "eks"
        else:
            nodes.append(self._create_node("ecs", "🐳 ECS Cluster\n(Docker)", 400, cluster_y, "default", "#e8f5e8"))
            cluster_id = "ecs"
        
        edges.append(self._create_edge("alb", cluster_id))
        
        # Microservices
        services_y = cluster_y + 150
        microservices = [
            ("user_service", "👤 User Service", 200, services_y),
            ("product_service", "📦 Product Service", 400, services_y),
            ("order_service", "🛒 Order Service", 600, services_y)
        ]
        
        for service_id, label, x, y in microservices:
            nodes.append(self._create_node(service_id, label, x, y, "default", "#f9fbe7"))
            edges.append(self._create_edge(cluster_id, service_id))
        
        # Service mesh (if high security)
        if security_level == "high":
            nodes.append(self._create_node("service_mesh", "🕸️ Service Mesh\n(Istio/App Mesh)", 400, services_y - 80, "default", "#fff3e0"))
            for service_id, _, _, _ in microservices:
                edges.append(self._create_edge("service_mesh", service_id))
        
        # Databases per service
        db_y = services_y + 150
        databases = [
            ("user_db", "🗄️ User DB", 200, db_y),
            ("product_db", "🗄️ Product DB", 400, db_y),
            ("order_db", "🗄️ Order DB", 600, db_y)
        ]
        
        for i, (db_id, label, x, y) in enumerate(databases):
            nodes.append(self._create_node(db_id, label, x, y, "default", "#fce4ec"))
            edges.append(self._create_edge(microservices[i][0], db_id))
        
        return DiagramData(nodes=nodes, edges=edges)
    
    def _generate_generic_diagram(self, services: Dict[str, str], questionnaire: QuestionnaireRequest, security_level: str) -> DiagramData:
        """Generate a basic architecture diagram"""
        return self._generate_web_app_diagram(services, questionnaire, security_level)
    
    def _create_node(self, id: str, label: str, x: int, y: int, type: str = "default", bg_color: str = "#f5f5f5") -> DiagramNode:
        """Create a diagram node with consistent styling"""
        # Remove emojis to avoid encoding issues
        import re
        clean_label = re.sub(r'[^\w\s\-\(\)\/\.\,\:]', '', label)
        
        return DiagramNode(
            id=id,
            type=type,
            data={
                "label": clean_label,
                "style": {
                    "background": bg_color,
                    "border": "2px solid #333",
                    "borderRadius": "8px",
                    "padding": "10px",
                    "fontSize": "12px",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "minWidth": "120px",
                    "minHeight": "60px"
                }
            },
            position={"x": x, "y": y}
        )
    
    def _create_edge(self, source: str, target: str, label: str = "") -> DiagramEdge:
        """Create a diagram edge with consistent styling"""
        return DiagramEdge(
            id=f"{source}-{target}",
            source=source,
            target=target,
            label=label,
            style={
                "stroke": "#333",
                "strokeWidth": 2
            },
            markerEnd={
                "type": "arrowclosed",
                "color": "#333"
            }
        )