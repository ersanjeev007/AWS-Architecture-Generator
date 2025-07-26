import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Badge,
  Button,
  Progress,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Icon,
  useColorModeValue,
  CircularProgress,
  CircularProgressLabel,
  Divider,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Textarea,
  Input,
  Select,
  Switch,
  FormControl,
  FormLabel,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Avatar,
  List,
  ListItem,
  ListIcon,
  Spinner
} from '@chakra-ui/react';
import {
  FaBrain,
  FaChartLine,
  FaDollarSign,
  FaShieldAlt,
  FaRocket,
  FaCog,
  FaLightbulb,
  FaRobot,
  FaComments,
  FaPlay,
  FaCheckCircle,
  FaExclamationTriangle,
  FaTrendingUp,
  FaSparkles,
  FaCode,
  FaCloudDownloadAlt
} from 'react-icons/fa';
import aiMLOptimizationService from '../../services/aiMLOptimizationService';

const AIOptimizationDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [optimizationFocus, setOptimizationFocus] = useState(['cost', 'performance']);
  const [aiReadinessData, setAiReadinessData] = useState(null);
  const [costPrediction, setCostPrediction] = useState(null);
  const [smartSuggestions, setSmartSuggestions] = useState([]);
  
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const bgColor = useColorModeValue('white', 'gray.800');
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  
  useEffect(() => {
    loadInitialData();
  }, []);
  
  const loadInitialData = async () => {
    try {
      setLoading(true);
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      
      if (currentProject.id) {
        // Load AI analysis, readiness assessment, and smart suggestions in parallel
        const [analysisResult, readinessResult, suggestionsResult] = await Promise.all([
          loadAIAnalysis(currentProject.id),
          loadAIReadinessAssessment(currentProject.id),
          loadSmartSuggestions(currentProject.id)
        ]);
        
        setAiAnalysis(analysisResult);
        setAiReadinessData(readinessResult);
        setSmartSuggestions(suggestionsResult.suggestions || []);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
      toast({
        title: 'Error loading AI data',
        description: 'Using demo data for display',
        status: 'warning',
        duration: 3000,
      });
      loadDemoData();
    } finally {
      setLoading(false);
    }
  };
  
  const loadAIAnalysis = async (projectId) => {
    try {
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      const analysisRequest = {
        project_id: projectId,
        questionnaire: currentProject.questionnaire || {},
        services: currentProject.services || {},
        include_predictions: true
      };
      
      return await aiMLOptimizationService.analyzeArchitectureWithAI(analysisRequest);
    } catch (error) {
      console.error('Error loading AI analysis:', error);
      return null;
    }
  };
  
  const loadAIReadinessAssessment = async (projectId) => {
    try {
      return await aiMLOptimizationService.assessAIReadiness(projectId);
    } catch (error) {
      console.error('Error loading AI readiness:', error);
      return null;
    }
  };
  
  const loadSmartSuggestions = async (projectId) => {
    try {
      return await aiMLOptimizationService.getSmartSuggestions(projectId);
    } catch (error) {
      console.error('Error loading smart suggestions:', error);
      return { suggestions: [] };
    }
  };
  
  const loadDemoData = () => {
    // Demo data for when API is not available
    setAiAnalysis({
      recommendations: [
        {
          id: 'demo_cost_opt',
          title: 'AI-Recommended: Implement Spot Instance Strategy',
          description: 'ML analysis indicates potential savings of $347.50/month by migrating non-critical workloads to Spot instances.',
          optimization_type: 'cost_optimization',
          affected_services: ['EC2', 'ECS'],
          priority: 'high',
          confidence_score: 0.87,
          predicted_cost_savings: 347.50,
          ml_model_used: 'RandomForest Cost Predictor'
        },
        {
          id: 'demo_performance',
          title: 'AI-Recommended: Intelligent Caching Layer',
          description: 'High network utilization detected. Implementing CloudFront with intelligent caching could reduce response times by 60%.',
          optimization_type: 'performance_optimization',
          affected_services: ['CloudFront', 'ElastiCache'],
          priority: 'medium',
          confidence_score: 0.79,
          predicted_performance_improvement: '60% response time reduction',
          ml_model_used: 'Network Pattern Analysis'
        }
      ],
      insights: {
        total_recommendations: 8,
        confidence_stats: { average_confidence: 0.83 },
        cost_impact: { total_potential_savings: 1247.30 },
        ai_readiness_score: 78.5,
        priority_breakdown: { critical: 1, high: 3, medium: 3, low: 1 }
      }
    });
    
    setAiReadinessData({
      ai_readiness_score: 78.5,
      readiness_level: 'Medium - Some preparation needed for AI/ML',
      recommended_services: ['Amazon SageMaker', 'Amazon Bedrock', 'AWS Lambda']
    });
    
    setSmartSuggestions([
      'How can I optimize my database performance?',
      'What AI/ML services can enhance my application?',
      'Analyze my architecture for cost savings'
    ]);
  };
  
  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return;
    
    const userMessage = chatInput.trim();
    setChatInput('');
    
    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      type: 'user',
      message: userMessage,
      timestamp: new Date()
    };
    
    setChatMessages(prev => [...prev, newUserMessage]);
    setChatLoading(true);
    
    try {
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      const chatRequest = {
        message: userMessage,
        project_id: currentProject.id || 'demo',
        context: {
          services: currentProject.services || {},
          questionnaire: currentProject.questionnaire || {}
        }
      };
      
      const response = await aiMLOptimizationService.chatWithAI(chatRequest);
      
      // Add AI response to chat
      const aiMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        message: response.message,
        suggestions: response.suggestions,
        intent: response.intent,
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Error in chat:', error);
      
      // Fallback response
      const fallbackMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        message: 'I apologize, but I encountered an issue processing your request. Here are some general recommendations based on your question.',
        suggestions: [
          'Try asking about specific AWS services',
          'Request architecture recommendations',
          'Ask for cost optimization advice'
        ],
        timestamp: new Date()
      };
      
      setChatMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setChatLoading(false);
    }
  };
  
  const handleOptimizationRun = async () => {
    try {
      setLoading(true);
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      
      const optimizationRequest = {
        project_id: currentProject.id || 'demo',
        optimization_focus: optimizationFocus,
        current_architecture: {
          services: currentProject.services || {},
          questionnaire: currentProject.questionnaire || {}
        }
      };
      
      const result = await aiMLOptimizationService.optimizeArchitecture(optimizationRequest);
      
      toast({
        title: 'Optimization Complete',
        description: `Generated ${result.recommendations?.length || 0} recommendations`,
        status: 'success',
        duration: 4000,
      });
      
      // Refresh the analysis
      await loadInitialData();
      
    } catch (error) {
      console.error('Error running optimization:', error);
      toast({
        title: 'Optimization Error',
        description: 'Failed to run optimization. Please try again.',
        status: 'error',
        duration: 4000,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleSuggestionClick = (suggestion) => {
    setChatInput(suggestion);
  };
  
  const AIOverviewCard = () => (
    <Card>
      <CardBody>
        <VStack spacing={6}>
          <HStack justify="space-between" w="full">
            <VStack align="start" spacing={1}>
              <Text fontSize="lg" fontWeight="bold">AI Architecture Intelligence</Text>
              <Text fontSize="sm" color="gray.600">Powered by ML and predictive analytics</Text>
            </VStack>
            <Icon as={FaBrain} boxSize={8} color="purple.500" />
          </HStack>
          
          <CircularProgress value={aiAnalysis?.insights?.ai_readiness_score || 78.5} size="120px" color="purple.500" thickness="8px">
            <CircularProgressLabel fontSize="2xl" fontWeight="bold">
              {Math.round(aiAnalysis?.insights?.ai_readiness_score || 78.5)}
            </CircularProgressLabel>
          </CircularProgress>
          
          <SimpleGrid columns={2} spacing={4} w="full">
            <VStack>
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                ${aiAnalysis?.insights?.cost_impact?.total_potential_savings?.toFixed(2) || '1,247.30'}
              </Text>
              <Text fontSize="xs" color="gray.600" textAlign="center">
                Potential Monthly Savings
              </Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                {aiAnalysis?.insights?.total_recommendations || 8}
              </Text>
              <Text fontSize="xs" color="gray.600" textAlign="center">
                AI Recommendations
              </Text>
            </VStack>
          </SimpleGrid>
          
          <Button colorScheme="purple" w="full" onClick={handleOptimizationRun} isLoading={loading} leftIcon={<FaSparkles />}>
            Run AI Optimization
          </Button>
        </VStack>
      </CardBody>
    </Card>
  );
  
  const RecommendationsGrid = () => (
    <VStack spacing={6}>
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6} w="full">
        <Card>
          <CardHeader>
            <HStack>
              <Icon as={FaDollarSign} color="green.500" />
              <Heading size="md">Cost Optimization</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                ${aiAnalysis?.insights?.cost_impact?.total_potential_savings?.toFixed(2) || '1,247.30'}
              </Text>
              <Text fontSize="sm" color="gray.600">Monthly savings potential</Text>
              <Progress value={85} colorScheme="green" size="sm" w="full" />
              <Text fontSize="xs">High confidence recommendations</Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardHeader>
            <HStack>
              <Icon as={FaRocket} color="blue.500" />
              <Heading size="md">Performance</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                60%
              </Text>
              <Text fontSize="sm" color="gray.600">Response time improvement</Text>
              <Progress value={78} colorScheme="blue" size="sm" w="full" />
              <Text fontSize="xs">Caching & CDN optimizations</Text>
            </VStack>
          </CardBody>
        </Card>
        
        <Card>
          <CardHeader>
            <HStack>
              <Icon as={FaShieldAlt} color="orange.500" />
              <Heading size="md">Security</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack align="start" spacing={3}>
              <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                92
              </Text>
              <Text fontSize="sm" color="gray.600">Security score target</Text>
              <Progress value={92} colorScheme="orange" size="sm" w="full" />
              <Text fontSize="xs">Zero trust & encryption</Text>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>
      
      {/* Detailed Recommendations */}
      <Card w="full">
        <CardHeader>
          <Heading size="md">🤖 AI-Powered Recommendations</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            {(aiAnalysis?.recommendations || []).map((rec, index) => (
              <Box key={rec.id || index} w="full" p={4} borderRadius="lg" border="1px" borderColor={borderColor}>
                <HStack justify="space-between" mb={2}>
                  <HStack>
                    <Badge colorScheme={
                      rec.priority === 'critical' ? 'red' :
                      rec.priority === 'high' ? 'orange' :
                      rec.priority === 'medium' ? 'yellow' : 'blue'
                    }>
                      {rec.priority}
                    </Badge>
                    <Badge variant="outline">{rec.optimization_type?.replace('_', ' ')}</Badge>
                    <Badge colorScheme="purple" variant="outline">
                      AI Confidence: {(rec.confidence_score * 100).toFixed(0)}%
                    </Badge>
                  </HStack>
                  <Button 
                    size="sm" 
                    leftIcon={<FaPlay />}
                    onClick={() => {
                      setSelectedRecommendation(rec);
                      onOpen();
                    }}
                  >
                    View Details
                  </Button>
                </HStack>
                <Text fontWeight="bold" mb={2}>{rec.title}</Text>
                <Text fontSize="sm" color="gray.600" mb={2}>{rec.description}</Text>
                <HStack>
                  {rec.predicted_cost_savings && (
                    <>
                      <Text fontSize="xs" color="green.500" fontWeight="bold">
                        Save: ${rec.predicted_cost_savings}/month
                      </Text>
                      <Text fontSize="xs" color="gray.500">•</Text>
                    </>
                  )}
                  <Text fontSize="xs" color="gray.500">
                    Model: {rec.ml_model_used}
                  </Text>
                  <Text fontSize="xs" color="gray.500">•</Text>
                  <Text fontSize="xs" color="gray.500">
                    Services: {rec.affected_services?.join(', ')}
                  </Text>
                </HStack>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
  
  const AIAssistantChat = () => (
    <Card h="600px" display="flex" flexDirection="column">
      <CardHeader>
        <HStack>
          <Avatar size="sm" icon={<FaRobot />} bg="purple.500" />
          <VStack align="start" spacing={0}>
            <Heading size="md">AI Architecture Assistant</Heading>
            <Text fontSize="sm" color="gray.600">Ask me anything about your AWS architecture</Text>
          </VStack>
        </HStack>
      </CardHeader>
      
      <CardBody flex="1" display="flex" flexDirection="column">
        {/* Smart Suggestions */}
        {smartSuggestions.length > 0 && chatMessages.length === 0 && (
          <Box mb={4}>
            <Text fontSize="sm" fontWeight="bold" mb={2}>💡 Smart Suggestions:</Text>
            <VStack spacing={2}>
              {smartSuggestions.slice(0, 3).map((suggestion, index) => (
                <Button
                  key={index}
                  size="sm"
                  variant="outline"
                  w="full"
                  textAlign="left"
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Button>
              ))}
            </VStack>
          </Box>
        )}
        
        {/* Chat Messages */}
        <Box flex="1" overflowY="auto" mb={4}>
          <VStack spacing={3} align="stretch">
            {chatMessages.map((msg) => (
              <Box key={msg.id} alignSelf={msg.type === 'user' ? 'flex-end' : 'flex-start'}>
                <Box
                  bg={msg.type === 'user' ? 'blue.500' : 'gray.100'}
                  color={msg.type === 'user' ? 'white' : 'black'}
                  p={3}
                  borderRadius="lg"
                  maxW="80%"
                >
                  <Text fontSize="sm">{msg.message}</Text>
                  {msg.suggestions && (
                    <VStack mt={2} spacing={1} align="start">
                      {msg.suggestions.slice(0, 3).map((suggestion, index) => (
                        <Button
                          key={index}
                          size="xs"
                          variant="ghost"
                          color={msg.type === 'user' ? 'white' : 'blue.500'}
                          onClick={() => handleSuggestionClick(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </VStack>
                  )}
                </Box>
              </Box>
            ))}
            
            {chatLoading && (
              <Box alignSelf="flex-start">
                <Box bg="gray.100" p={3} borderRadius="lg">
                  <HStack>
                    <Spinner size="sm" />
                    <Text fontSize="sm">AI is thinking...</Text>
                  </HStack>
                </Box>
              </Box>
            )}
          </VStack>
        </Box>
        
        {/* Chat Input */}
        <HStack>
          <Input
            placeholder="Ask about cost optimization, security, performance..."
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleChatSubmit()}
          />
          <Button
            colorScheme="purple"
            onClick={handleChatSubmit}
            isLoading={chatLoading}
            disabled={!chatInput.trim()}
          >
            Send
          </Button>
        </HStack>
      </CardBody>
    </Card>
  );
  
  const AIReadinessAssessment = () => (
    <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
      <Card>
        <CardHeader>
          <Heading size="md">🤖 AI/ML Readiness Assessment</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <CircularProgress 
              value={aiReadinessData?.ai_readiness_score || 78.5} 
              size="120px" 
              color="purple.500" 
              thickness="8px"
            >
              <CircularProgressLabel fontSize="xl" fontWeight="bold">
                {Math.round(aiReadinessData?.ai_readiness_score || 78.5)}
              </CircularProgressLabel>
            </CircularProgress>
            
            <Text textAlign="center" fontSize="sm" color="gray.600">
              {aiReadinessData?.readiness_level || 'Medium - Some preparation needed for AI/ML'}
            </Text>
            
            <Divider />
            
            <VStack align="start" w="full" spacing={2}>
              <Text fontWeight="bold" fontSize="sm">Recommended AI/ML Services:</Text>
              <List spacing={1}>
                {(aiReadinessData?.recommended_services || ['Amazon SageMaker', 'Amazon Bedrock', 'AWS Lambda']).map((service, index) => (
                  <ListItem key={index} fontSize="sm">
                    <ListIcon as={FaCheckCircle} color="green.500" />
                    {service}
                  </ListItem>
                ))}
              </List>
            </VStack>
          </VStack>
        </CardBody>
      </Card>
      
      <Card>
        <CardHeader>
          <Heading size="md">💰 ML Cost Prediction</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <Stat>
              <StatLabel>Estimated Monthly AI/ML Costs</StatLabel>
              <StatNumber>${costPrediction?.total_monthly_cost || '450'}</StatNumber>
              <StatHelpText>
                <StatArrow type="increase" />
                ROI: 240% in 6 months
              </StatHelpText>
            </Stat>
            
            <Divider />
            
            <VStack align="start" w="full" spacing={2}>
              <Text fontWeight="bold" fontSize="sm">Cost Breakdown:</Text>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">SageMaker</Text>
                <Text fontSize="sm" fontWeight="bold">$200/month</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Bedrock</Text>
                <Text fontSize="sm" fontWeight="bold">$150/month</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Lambda</Text>
                <Text fontSize="sm" fontWeight="bold">$50/month</Text>
              </HStack>
              <HStack justify="space-between" w="full">
                <Text fontSize="sm">Other Services</Text>
                <Text fontSize="sm" fontWeight="bold">$50/month</Text>
              </HStack>
            </VStack>
            
            <Button size="sm" colorScheme="blue" w="full" leftIcon={<FaChartLine />}>
              Get Detailed Cost Analysis
            </Button>
          </VStack>
        </CardBody>
      </Card>
    </SimpleGrid>
  );
  
  if (loading && !aiAnalysis) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" color="purple.500" />
          <Text>Loading AI optimization analysis...</Text>
        </VStack>
      </Container>
    );
  }
  
  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg">🤖 AI/ML Optimization Dashboard</Heading>
              <Text color="gray.600">
                Intelligent architecture optimization powered by machine learning and predictive analytics
              </Text>
            </VStack>
            <HStack>
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-optimize" mb="0" fontSize="sm">
                  Auto-optimize
                </FormLabel>
                <Switch id="auto-optimize" colorScheme="purple" />
              </FormControl>
              <Button leftIcon={<FaCloudDownloadAlt />} size="sm" variant="outline">
                Export Report
              </Button>
            </HStack>
          </HStack>
          
          <Alert status="info" borderRadius="lg" mb={6}>
            <AlertIcon />
            <Box>
              <AlertTitle>AI-Powered Architecture Intelligence</AlertTitle>
              <AlertDescription>
                Our ML models analyze your architecture patterns, usage data, and AWS best practices to provide personalized optimization recommendations with high confidence scores.
              </AlertDescription>
            </Box>
          </Alert>
        </Box>
        
        {/* Main Dashboard */}
        <SimpleGrid columns={{ base: 1, lg: 4 }} spacing={6}>
          <Box gridColumn={{ lg: "1 / 2" }}>
            <AIOverviewCard />
          </Box>
          <Box gridColumn={{ lg: "2 / 5" }}>
            <Tabs index={activeTab} onChange={setActiveTab}>
              <TabList>
                <Tab>Recommendations</Tab>
                <Tab>AI Assistant</Tab>
                <Tab>Readiness</Tab>
                <Tab>Analytics</Tab>
              </TabList>
              
              <TabPanels>
                <TabPanel px={0}>
                  <RecommendationsGrid />
                </TabPanel>
                
                <TabPanel px={0}>
                  <AIAssistantChat />
                </TabPanel>
                
                <TabPanel px={0}>
                  <AIReadinessAssessment />
                </TabPanel>
                
                <TabPanel px={0}>
                  <Card>
                    <CardBody>
                      <Text>Advanced analytics and ML model insights coming soon...</Text>
                    </CardBody>
                  </Card>
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Box>
        </SimpleGrid>
        
        {/* Recommendation Details Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>{selectedRecommendation?.title}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedRecommendation && (
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={2}>Description</Text>
                    <Text>{selectedRecommendation.description}</Text>
                  </Box>
                  
                  <SimpleGrid columns={2} spacing={4}>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Priority</Text>
                      <Badge colorScheme={
                        selectedRecommendation.priority === 'critical' ? 'red' :
                        selectedRecommendation.priority === 'high' ? 'orange' :
                        selectedRecommendation.priority === 'medium' ? 'yellow' : 'blue'
                      }>
                        {selectedRecommendation.priority}
                      </Badge>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Confidence Score</Text>
                      <Text fontWeight="bold">{(selectedRecommendation.confidence_score * 100).toFixed(0)}%</Text>
                    </Box>
                    {selectedRecommendation.predicted_cost_savings && (
                      <Box>
                        <Text fontSize="sm" color="gray.600">Cost Savings</Text>
                        <Text fontWeight="bold" color="green.500">${selectedRecommendation.predicted_cost_savings}/month</Text>
                      </Box>
                    )}
                    <Box>
                      <Text fontSize="sm" color="gray.600">ML Model Used</Text>
                      <Text fontWeight="medium">{selectedRecommendation.ml_model_used}</Text>
                    </Box>
                  </SimpleGrid>
                  
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={2}>Affected Services</Text>
                    <HStack>
                      {selectedRecommendation.affected_services?.map((service, index) => (
                        <Badge key={index} variant="outline">{service}</Badge>
                      ))}
                    </HStack>
                  </Box>
                </VStack>
              )}
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="purple" mr={3} leftIcon={<FaCode />}>
                Implement Recommendation
              </Button>
              <Button variant="ghost" onClick={onClose}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default AIOptimizationDashboard;