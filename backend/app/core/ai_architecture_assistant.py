import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from dataclasses import dataclass
from app.core.ai_ml_optimizer import IntelligentArchitectureOptimizer, AIRecommendation
from app.core.enhanced_security_templates import EnhancedSecurityTemplates
from app.schemas.questionnaire import QuestionnaireRequest

logger = logging.getLogger(__name__)

@dataclass
class ConversationContext:
    project_id: str
    user_intent: str
    architecture_state: Dict[str, Any]
    conversation_history: List[Dict[str, str]]
    recommendations: List[AIRecommendation]

class IntelligentArchitectureAssistant:
    """AI-powered architecture assistant using GPT and ML models"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        self.optimizer = IntelligentArchitectureOptimizer(openai_api_key)
        self.security_templates = EnhancedSecurityTemplates()
        
        # AI assistant personality and knowledge base
        self.system_prompt = """You are an expert AWS Cloud Architect AI Assistant with deep knowledge of:
        - AWS services and architecture patterns
        - Cost optimization strategies
        - Security best practices and compliance
        - Performance optimization
        - AI/ML integration with AWS services
        - Scalability and reliability patterns
        - Modern architecture patterns (microservices, serverless, containers)
        
        Your role is to:
        1. Provide intelligent, actionable architecture recommendations
        2. Explain complex AWS concepts in simple terms
        3. Suggest cost-effective and secure solutions
        4. Help users make informed decisions about their infrastructure
        5. Identify opportunities for AI/ML integration
        
        Always provide specific, practical advice with code examples when relevant.
        Use the latest AWS services and best practices (2025).
        """
        
        # Architecture pattern templates
        self.architecture_patterns = {
            "serverless": {
                "services": ["Lambda", "API Gateway", "DynamoDB", "S3", "CloudFront"],
                "use_cases": ["APIs", "event processing", "real-time data processing"],
                "benefits": ["cost-effective", "auto-scaling", "low maintenance"]
            },
            "microservices": {
                "services": ["ECS", "EKS", "ALB", "RDS", "ElastiCache"],
                "use_cases": ["large applications", "team scaling", "independent deployments"],
                "benefits": ["scalability", "technology diversity", "fault isolation"]
            },
            "data_analytics": {
                "services": ["EMR", "Glue", "Athena", "QuickSight", "Kinesis"],
                "use_cases": ["big data processing", "real-time analytics", "BI dashboards"],
                "benefits": ["scalable data processing", "real-time insights", "cost-effective storage"]
            },
            "ai_ml": {
                "services": ["SageMaker", "Bedrock", "Comprehend", "Rekognition", "Textract"],
                "use_cases": ["machine learning", "AI applications", "intelligent automation"],
                "benefits": ["AI integration", "managed ML services", "rapid innovation"]
            }
        }
    
    async def chat_with_assistant(self, user_message: str, context: ConversationContext) -> Dict[str, Any]:
        """Main chat interface with the AI architecture assistant"""
        
        try:
            # Analyze user intent
            intent = await self._analyze_user_intent(user_message, context)
            
            # Generate contextual response based on intent
            if intent == "architecture_review":
                response = await self._provide_architecture_review(user_message, context)
            elif intent == "cost_optimization":
                response = await self._provide_cost_optimization_advice(user_message, context)
            elif intent == "security_analysis":
                response = await self._provide_security_analysis(user_message, context)
            elif intent == "performance_optimization":
                response = await self._provide_performance_advice(user_message, context)
            elif intent == "ai_ml_integration":
                response = await self._provide_ai_ml_guidance(user_message, context)
            elif intent == "general_question":
                response = await self._provide_general_guidance(user_message, context)
            else:
                response = await self._provide_contextual_response(user_message, context)
            
            # Update conversation history
            context.conversation_history.append({
                "user": user_message,
                "assistant": response["message"],
                "timestamp": datetime.now().isoformat(),
                "intent": intent
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat_with_assistant: {str(e)}")
            return {
                "message": "I apologize, but I encountered an error while processing your request. Please try again or rephrase your question.",
                "suggestions": ["Try asking about specific AWS services", "Ask for architecture recommendations", "Request cost optimization advice"],
                "error": True
            }
    
    async def _analyze_user_intent(self, message: str, context: ConversationContext) -> str:
        """Analyze user intent using AI"""
        
        intent_keywords = {
            "architecture_review": ["architecture", "design", "review", "structure", "pattern"],
            "cost_optimization": ["cost", "price", "budget", "expensive", "savings", "optimize"],
            "security_analysis": ["security", "secure", "vulnerability", "compliance", "encrypt"],
            "performance_optimization": ["performance", "speed", "latency", "slow", "optimize"],
            "ai_ml_integration": ["ai", "ml", "machine learning", "artificial intelligence", "bedrock", "sagemaker"],
            "general_question": ["what", "how", "why", "explain", "help"]
        }
        
        message_lower = message.lower()
        
        # Simple keyword-based intent classification
        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent
        
        return "general_question"
    
    async def _provide_architecture_review(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide architecture review and recommendations"""
        
        # Get AI recommendations
        services = context.architecture_state.get("services", {})
        questionnaire = context.architecture_state.get("questionnaire")
        
        if services:
            ai_recommendations = await self.optimizer.analyze_architecture_with_ai(
                context.architecture_state, questionnaire, services
            )
            
            # Create comprehensive review
            review_summary = self._generate_architecture_summary(context.architecture_state, ai_recommendations)
            
            response = f"""## 🏗️ Architecture Review\n\n{review_summary}\n\n"""
            
            # Add top recommendations
            if ai_recommendations:
                response += "### 🚀 Top AI Recommendations:\n\n"
                for i, rec in enumerate(ai_recommendations[:3], 1):
                    response += f"**{i}. {rec.title}** (Confidence: {rec.confidence_score:.2f})\n"
                    response += f"   {rec.description}\n\n"
            
            suggestions = [
                "Ask about specific service recommendations",
                "Request cost optimization analysis",
                "Inquire about security improvements",
                "Get performance optimization tips"
            ]
            
        else:
            response = """I'd be happy to review your architecture! However, I need more information about your current setup. 

Could you tell me:
- What services are you currently using?
- What's your primary use case?
- Any specific concerns or goals?"""
            
            suggestions = [
                "Describe your current AWS services",
                "Tell me about your application requirements",
                "Ask for architecture pattern recommendations"
            ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "architecture_review",
            "ai_recommendations": ai_recommendations[:5] if 'ai_recommendations' in locals() else []
        }
    
    async def _provide_cost_optimization_advice(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide cost optimization recommendations"""
        
        services = context.architecture_state.get("services", {})
        
        if services:
            # Get cost-specific recommendations
            cost_recommendations = [rec for rec in context.recommendations 
                                 if "cost" in rec.optimization_type.value.lower()]
            
            total_savings = sum([rec.predicted_cost_savings for rec in cost_recommendations 
                               if rec.predicted_cost_savings])
            
            response = f"""## 💰 Cost Optimization Analysis\n\n"""
            
            if total_savings > 0:
                response += f"**Potential Monthly Savings: ${total_savings:.2f}**\n\n"
            
            response += "### 🎯 Key Cost Optimization Opportunities:\n\n"
            
            if cost_recommendations:
                for i, rec in enumerate(cost_recommendations[:3], 1):
                    savings_text = f" (Save ${rec.predicted_cost_savings:.2f}/month)" if rec.predicted_cost_savings else ""
                    response += f"**{i}. {rec.title}**{savings_text}\n"
                    response += f"   {rec.description}\n\n"
            else:
                response += self._generate_generic_cost_advice(services)
            
            suggestions = [
                "How can I implement Reserved Instance savings?",
                "What about Spot Instance opportunities?",
                "Tell me about right-sizing my resources",
                "How can I optimize storage costs?"
            ]
            
        else:
            response = """I can help you optimize your AWS costs! Here are some general strategies:

### 💡 Universal Cost Optimization Tips:
1. **Right-sizing**: Choose appropriate instance sizes
2. **Reserved Instances**: Commit to 1-3 year terms for steady workloads
3. **Spot Instances**: Use for fault-tolerant workloads
4. **Auto Scaling**: Scale resources based on demand
5. **Storage Optimization**: Use appropriate storage classes

What specific services are you using? I can provide targeted advice."""
            
            suggestions = [
                "Tell me about your current AWS spending",
                "What services are consuming the most cost?",
                "Ask about specific cost optimization strategies"
            ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "cost_optimization",
            "cost_savings": total_savings if 'total_savings' in locals() else 0
        }
    
    async def _provide_security_analysis(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide security analysis and recommendations"""
        
        services = context.architecture_state.get("services", {})
        
        if services:
            # Get security-specific recommendations
            security_recommendations = [rec for rec in context.recommendations 
                                     if "security" in rec.optimization_type.value.lower()]
            
            response = """## 🔒 Security Analysis\n\n"""
            
            # Security score (simulated)
            security_score = context.architecture_state.get("security_score", 75)
            response += f"**Current Security Score: {security_score}/100**\n\n"
            
            if security_score < 80:
                response += "⚠️ Your architecture has room for security improvements.\n\n"
            elif security_score >= 90:
                response += "✅ Your architecture follows strong security practices!\n\n"
            else:
                response += "👍 Your architecture has good security foundations.\n\n"
            
            response += "### 🛡️ Security Recommendations:\n\n"
            
            if security_recommendations:
                for i, rec in enumerate(security_recommendations[:3], 1):
                    response += f"**{i}. {rec.title}**\n"
                    response += f"   {rec.description}\n\n"
            else:
                response += self._generate_generic_security_advice(services)
            
            suggestions = [
                "How can I implement Zero Trust architecture?",
                "What about encryption best practices?",
                "Tell me about compliance requirements",
                "How do I improve my security monitoring?"
            ]
            
        else:
            response = """I can help you secure your AWS infrastructure! Here are fundamental security practices:

### 🔐 AWS Security Fundamentals:
1. **IAM Best Practices**: Least privilege access, MFA, regular audits
2. **Network Security**: VPC, Security Groups, NACLs
3. **Encryption**: Data at rest and in transit
4. **Monitoring**: CloudTrail, GuardDuty, Security Hub
5. **Compliance**: Meet regulatory requirements

What's your current architecture? I can provide specific security guidance."""
            
            suggestions = [
                "Tell me about your compliance requirements",
                "What data are you handling?",
                "Ask about specific security services",
                "How do I implement encryption?"
            ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "security_analysis",
            "security_score": security_score if 'security_score' in locals() else 0
        }
    
    async def _provide_performance_advice(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide performance optimization advice"""
        
        services = context.architecture_state.get("services", {})
        
        response = """## ⚡ Performance Optimization\n\n"""
        
        if services:
            # Analyze performance based on services
            performance_tips = self._generate_performance_tips(services)
            response += performance_tips
            
            suggestions = [
                "How can I reduce latency?",
                "What about caching strategies?",
                "Tell me about CDN implementation",
                "How do I optimize database performance?"
            ]
            
        else:
            response += """Here are key performance optimization strategies:

### 🚀 Performance Best Practices:
1. **Caching**: ElastiCache, CloudFront
2. **Database Optimization**: Read replicas, indexing
3. **Content Delivery**: CloudFront CDN
4. **Auto Scaling**: Respond to demand automatically
5. **Instance Selection**: Choose right compute resources

What specific performance challenges are you facing?"""
            
            suggestions = [
                "Tell me about your performance requirements",
                "What's your current response time?",
                "Ask about specific optimization techniques"
            ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "performance_optimization"
        }
    
    async def _provide_ai_ml_guidance(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide AI/ML integration guidance"""
        
        response = """## 🤖 AI/ML Integration Guide\n\n"""
        
        services = context.architecture_state.get("services", {})
        use_case = self._identify_ai_ml_use_case(message, context)
        
        if use_case:
            response += f"Based on your requirements, here's how to integrate AI/ML:\n\n"
            response += self._generate_ai_ml_recommendations(use_case, services)
        else:
            response += """### 🎯 Popular AI/ML Use Cases on AWS:

**1. Generative AI Applications**
- **Amazon Bedrock**: Access foundation models (Claude, Titan, etc.)
- **Use Cases**: Chatbots, content generation, code assistance

**2. Custom Machine Learning**
- **Amazon SageMaker**: Build, train, deploy custom models
- **Use Cases**: Predictive analytics, recommendation engines

**3. AI Services (No ML expertise required)**
- **Amazon Comprehend**: Text analysis and sentiment
- **Amazon Rekognition**: Image and video analysis
- **Amazon Textract**: Document text extraction

**4. Data Analytics & ML**
- **Amazon EMR**: Big data processing with ML
- **AWS Glue**: Data preparation for ML

What specific AI/ML capabilities are you looking to add?"""
        
        suggestions = [
            "I want to add a chatbot to my application",
            "How do I implement predictive analytics?",
            "Tell me about image recognition capabilities",
            "What's the easiest way to add AI features?"
        ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "ai_ml_integration"
        }
    
    async def _provide_general_guidance(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide general AWS architecture guidance"""
        
        # Use OpenAI to generate contextual response if API key is available
        if self.openai_api_key:
            try:
                response = await self._generate_openai_response(message, context)
                suggestions = [
                    "Ask about specific AWS services",
                    "Request architecture recommendations",
                    "Get best practices advice"
                ]
                
                return {
                    "message": response,
                    "suggestions": suggestions,
                    "intent": "general_question"
                }
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
        
        # Fallback response
        response = """I'm here to help you with AWS architecture! I can assist with:

### 🏗️ Architecture Design
- Recommend appropriate AWS services
- Design scalable and secure architectures
- Review existing architectures

### 💰 Cost Optimization  
- Identify cost-saving opportunities
- Right-size your resources
- Implement cost-effective solutions

### 🔒 Security Best Practices
- Implement security controls
- Ensure compliance requirements
- Monitor and detect threats

### ⚡ Performance Optimization
- Improve application performance
- Reduce latency and improve reliability
- Scale effectively

### 🤖 AI/ML Integration
- Add AI capabilities to your applications
- Choose the right AI/ML services
- Implement intelligent automation

What would you like to know about?"""
        
        suggestions = [
            "Help me design a new architecture",
            "Review my current setup",
            "Find cost optimization opportunities",
            "Improve my security posture"
        ]
        
        return {
            "message": response,
            "suggestions": suggestions,
            "intent": "general_question"
        }
    
    async def _provide_contextual_response(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Provide contextual response using conversation history"""
        
        # Analyze conversation history for context
        recent_intents = [msg.get("intent", "") for msg in context.conversation_history[-3:]]
        
        if "cost_optimization" in recent_intents:
            return await self._provide_cost_optimization_advice(message, context)
        elif "security_analysis" in recent_intents:
            return await self._provide_security_analysis(message, context)
        elif "ai_ml_integration" in recent_intents:
            return await self._provide_ai_ml_guidance(message, context)
        else:
            return await self._provide_general_guidance(message, context)
    
    async def _generate_openai_response(self, message: str, context: ConversationContext) -> str:
        """Generate response using OpenAI GPT"""
        
        # Prepare context for OpenAI
        context_info = f"""
        Architecture State: {json.dumps(context.architecture_state, indent=2)}
        Recent Conversation: {json.dumps(context.conversation_history[-3:], indent=2)}
        """
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Context: {context_info}"},
            {"role": "user", "content": message}
        ]
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _generate_architecture_summary(self, architecture_state: Dict[str, Any], 
                                     recommendations: List[AIRecommendation]) -> str:
        """Generate architecture summary"""
        
        services = architecture_state.get("services", {})
        service_count = len(services)
        
        summary = f"""Your architecture currently uses **{service_count} AWS services**. """
        
        if recommendations:
            high_priority = len([r for r in recommendations if r.priority in ["critical", "high"]])
            avg_confidence = sum([r.confidence_score for r in recommendations]) / len(recommendations)
            
            summary += f"""

**AI Analysis Results:**
- {len(recommendations)} optimization opportunities identified
- {high_priority} high-priority recommendations
- Average confidence score: {avg_confidence:.2f}/1.0"""
            
        return summary
    
    def _generate_generic_cost_advice(self, services: Dict[str, str]) -> str:
        """Generate generic cost optimization advice"""
        
        advice = "Based on your services, consider these cost optimizations:\n\n"
        
        if any("ec2" in s.lower() for s in services.values()):
            advice += "- **EC2 Optimization**: Right-size instances, use Reserved Instances for steady workloads\n"
        
        if any("s3" in s.lower() or "storage" in s.lower() for s in services.values()):
            advice += "- **Storage Optimization**: Use appropriate S3 storage classes, implement lifecycle policies\n"
        
        if any("rds" in s.lower() or "database" in s.lower() for s in services.values()):
            advice += "- **Database Optimization**: Use read replicas, consider Aurora Serverless for variable workloads\n"
        
        advice += "- **General**: Implement auto scaling, use CloudWatch for monitoring unused resources\n"
        
        return advice
    
    def _generate_generic_security_advice(self, services: Dict[str, str]) -> str:
        """Generate generic security advice"""
        
        advice = "Essential security measures for your architecture:\n\n"
        advice += "1. **Enable encryption** for all data at rest and in transit\n"
        advice += "2. **Implement least privilege** IAM policies\n"
        advice += "3. **Enable logging** with CloudTrail and VPC Flow Logs\n"
        advice += "4. **Deploy GuardDuty** for threat detection\n"
        advice += "5. **Use Security Hub** for centralized security monitoring\n"
        
        return advice
    
    def _generate_performance_tips(self, services: Dict[str, str]) -> str:
        """Generate performance optimization tips"""
        
        tips = "Performance optimization recommendations:\n\n"
        
        if any("database" in s.lower() or "rds" in s.lower() for s in services.values()):
            tips += "**Database Performance:**\n"
            tips += "- Use read replicas for read-heavy workloads\n"
            tips += "- Implement connection pooling\n"
            tips += "- Consider ElastiCache for caching\n\n"
        
        if any("api" in s.lower() or "gateway" in s.lower() for s in services.values()):
            tips += "**API Performance:**\n"
            tips += "- Enable API Gateway caching\n"
            tips += "- Use CloudFront for global distribution\n"
            tips += "- Implement efficient pagination\n\n"
        
        tips += "**General Performance:**\n"
        tips += "- Use appropriate instance types for your workload\n"
        tips += "- Implement auto scaling for variable demand\n"
        tips += "- Monitor with CloudWatch and set up alerts\n"
        
        return tips
    
    def _identify_ai_ml_use_case(self, message: str, context: ConversationContext) -> Optional[str]:
        """Identify AI/ML use case from message"""
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["chat", "chatbot", "conversation"]):
            return "chatbot"
        elif any(word in message_lower for word in ["predict", "forecast", "analytics"]):
            return "predictive_analytics"
        elif any(word in message_lower for word in ["image", "photo", "visual"]):
            return "image_analysis"
        elif any(word in message_lower for word in ["text", "document", "content"]):
            return "text_analysis"
        elif any(word in message_lower for word in ["recommend", "suggestion"]):
            return "recommendation_engine"
        
        return None
    
    def _generate_ai_ml_recommendations(self, use_case: str, services: Dict[str, str]) -> str:
        """Generate AI/ML service recommendations for specific use case"""
        
        recommendations = {
            "chatbot": """
**🤖 Chatbot Implementation:**
- **Amazon Bedrock**: Use Claude or other foundation models for conversational AI
- **Amazon Lex**: For voice and text chatbots with NLU
- **Lambda + API Gateway**: Backend processing and integration
- **DynamoDB**: Store conversation history and user data

**Implementation Steps:**
1. Set up Amazon Bedrock with appropriate model
2. Create Lambda functions for conversation logic
3. Integrate with your frontend using API Gateway
4. Implement conversation memory with DynamoDB""",

            "predictive_analytics": """
**📊 Predictive Analytics Solution:**
- **Amazon SageMaker**: Build and train custom ML models
- **Amazon Forecast**: Time-series forecasting service
- **Amazon EMR**: For big data processing and feature engineering
- **QuickSight**: Visualize predictions and insights

**Implementation Steps:**
1. Prepare and store data in S3
2. Use SageMaker for model development
3. Deploy model endpoints for real-time predictions
4. Create dashboards in QuickSight""",

            "image_analysis": """
**👁️ Image Analysis Solution:**
- **Amazon Rekognition**: Pre-built image analysis capabilities
- **Amazon Bedrock**: Multi-modal foundation models
- **SageMaker**: Custom computer vision models
- **S3**: Store and organize images

**Implementation Steps:**
1. Store images in S3 with proper organization
2. Use Rekognition for standard image analysis
3. Integrate with Lambda for automated processing
4. Build custom models in SageMaker if needed""",

            "text_analysis": """
**📝 Text Analysis Solution:**
- **Amazon Comprehend**: Sentiment analysis, entity extraction
- **Amazon Textract**: Extract text from documents
- **Amazon Bedrock**: Advanced text understanding and generation
- **OpenSearch**: Search and analyze text data

**Implementation Steps:**
1. Ingest text data into S3
2. Use Comprehend for sentiment and entity analysis
3. Implement search with OpenSearch
4. Create insights dashboards""",

            "recommendation_engine": """
**🎯 Recommendation Engine:**
- **Amazon Personalize**: Managed recommendation service
- **SageMaker**: Build custom recommendation models
- **DynamoDB**: Store user interactions and preferences
- **Kinesis**: Real-time data streaming

**Implementation Steps:**
1. Collect user interaction data
2. Set up Amazon Personalize with your data
3. Train recommendation models
4. Integrate recommendations into your application"""
        }
        
        return recommendations.get(use_case, "I can help you implement AI/ML capabilities. What specific use case are you interested in?")
    
    async def get_smart_suggestions(self, context: ConversationContext) -> List[str]:
        """Generate smart suggestions based on context"""
        
        suggestions = []
        
        # Analyze architecture state for suggestions
        services = context.architecture_state.get("services", {})
        
        if not services:
            suggestions.extend([
                "Help me choose the right AWS services for my project",
                "What's the best architecture pattern for my use case?",
                "Show me cost-effective solutions"
            ])
        else:
            # Service-specific suggestions
            if any("database" in s.lower() for s in services.values()):
                suggestions.append("How can I optimize my database performance?")
            
            if any("s3" in s.lower() or "storage" in s.lower() for s in services.values()):
                suggestions.append("What are the best S3 storage class strategies?")
            
            if len(services) > 5:
                suggestions.append("How can I implement microservices architecture?")
            
            suggestions.extend([
                "Analyze my architecture for cost savings",
                "What AI/ML services can enhance my application?",
                "How can I improve my security posture?"
            ])
        
        # Add context-aware suggestions
        recent_intents = [msg.get("intent", "") for msg in context.conversation_history[-2:]]
        
        if "cost_optimization" not in recent_intents:
            suggestions.append("How can I reduce my AWS costs?")
        
        if "security_analysis" not in recent_intents:
            suggestions.append("What security improvements do you recommend?")
        
        if "ai_ml_integration" not in recent_intents:
            suggestions.append("How can I add AI capabilities to my app?")
        
        return suggestions[:6]  # Return top 6 suggestions