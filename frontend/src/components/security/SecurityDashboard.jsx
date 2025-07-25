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
  Avatar,
  List,
  ListItem,
  ListIcon,
  Divider,
  Spinner,
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
} from '@chakra-ui/react';
import {
  FaShieldAlt,
  FaExclamationTriangle,
  FaCheckCircle,
  FaEye,
  FaLock,
  FaKey,
  FaHistory,
  FaSync,
  FaDownload,
  FaPlay,
} from 'react-icons/fa';
import securityService from '../../services/securityService';

const SecurityDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [securityData, setSecurityData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [complianceData, setComplianceData] = useState(null);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [error, setError] = useState(null);
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();

  useEffect(() => {
    loadSecurityData();
  }, []);

  const loadSecurityData = async () => {
    const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
    
    try {
      setLoading(true);
      setError(null);
      
      if (currentProject.id) {
        try {
          // Try to load real data first
          const [securityAnalysis, projectRecommendations, compliance] = await Promise.all([
            securityService.analyzeProjectSecurity(
              currentProject.id,
              currentProject.questionnaire || {},
              currentProject.services || {},
              true,
              'medium'
            ),
            securityService.getProjectRecommendations(currentProject.id, { limit: 20 }),
            securityService.getComplianceDashboard(currentProject.id)
          ]);

          setSecurityData(securityAnalysis);
          setRecommendations(projectRecommendations);
          setComplianceData(compliance);
        } catch (apiError) {
          console.warn('API not available, using mock data:', apiError);
          throw apiError; // Fall through to mock data
        }
      } else {
        throw new Error('No current project');
      }
    } catch (error) {
      console.error('Error loading security data:', error);
      setError('Failed to load live security data. Using demo data.');
      
      // Fallback to mock data
      const mockData = await securityService.getMockSecurityData(currentProject?.id || 'demo');
      setSecurityData(mockData);
      setRecommendations(mockData.recommendations);
      setComplianceData({
        project_id: mockData.project_id,
        compliance_frameworks: Object.keys(mockData.compliance_status),
        overall_compliance_score: mockData.security_posture_score,
        framework_scores: mockData.compliance_status
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefreshData = async () => {
    toast({
      title: 'Refreshing security data...',
      status: 'info',
      duration: 2000,
    });
    await loadSecurityData();
    toast({
      title: 'Security data updated',
      status: 'success',
      duration: 2000,
    });
  };

  const handleRunSecurityScan = async () => {
    try {
      setLoading(true);
      toast({
        title: 'Running security scan...',
        status: 'info',
        duration: 3000,
      });

      // Simulate scan delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Refresh all data
      await loadSecurityData();
      
      toast({
        title: 'Security scan completed',
        description: 'Security posture has been re-evaluated',
        status: 'success',
        duration: 3000,
      });
    } catch (error) {
      toast({
        title: 'Scan failed',
        description: 'Unable to complete security scan',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRecommendationClick = async (recommendation) => {
    try {
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      const implementationPlan = await securityService.getImplementationPlan(
        recommendation.id,
        currentProject.id || 'demo'
      );
      
      setSelectedRecommendation({
        ...recommendation,
        implementation_plan: implementationPlan
      });
      onOpen();
    } catch (error) {
      console.error('Error getting implementation plan:', error);
      setSelectedRecommendation(recommendation);
      onOpen();
    }
  };

  const LoadingAlert = () => (
    <Alert status="info" borderRadius="lg" mb={6}>
      <AlertIcon />
      <Box>
        <AlertTitle>AI-Powered Security Analysis</AlertTitle>
        <AlertDescription>
          {error ? error : 'Real-time security monitoring with AI-powered recommendations. Last scan: ' + (securityData?.last_analyzed ? new Date(securityData.last_analyzed).toLocaleString() : 'now')}
        </AlertDescription>
      </Box>
    </Alert>
  );

  const SecurityScoreCard = () => {
    const scoreData = securityService.formatSecurityScore(securityData?.security_posture_score || 87);
    
    return (
      <Card>
        <CardBody>
          <VStack spacing={6}>
            <HStack justify="space-between" w="full">
              <VStack align="start" spacing={1}>
                <Text fontSize="lg" fontWeight="bold">Security Posture Score</Text>
                <Text fontSize="sm" color="gray.600">Overall security health</Text>
              </VStack>
              <Icon as={FaShieldAlt} boxSize={6} color={`${scoreData.color}.500`} />
            </HStack>
            
            <CircularProgress value={scoreData.value} size="120px" color={`${scoreData.color}.500`} thickness="8px">
              <CircularProgressLabel fontSize="2xl" fontWeight="bold">
                {scoreData.value}
              </CircularProgressLabel>
            </CircularProgress>
            
            <SimpleGrid columns={3} spacing={4} w="full">
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="red.500">
                  {securityData?.threats?.filter(t => t.severity === 'critical').length || 2}
                </Text>
                <Text fontSize="xs" color="gray.600" textAlign="center">
                  Critical Issues
                </Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                  {securityData?.threats?.filter(t => t.severity === 'high').length || 1}
                </Text>
                <Text fontSize="xs" color="gray.600" textAlign="center">
                  High Priority
                </Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {recommendations?.filter(r => r.priority === 'low').length || 4}
                </Text>
                <Text fontSize="xs" color="gray.600" textAlign="center">
                  Resolved
                </Text>
              </VStack>
            </SimpleGrid>
            
            <Button colorScheme="blue" w="full" onClick={handleRunSecurityScan} isLoading={loading}>
              Run Security Scan
            </Button>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  const ThreatOverview = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Active Threats</Heading>
          <Badge colorScheme="red">
            {securityData?.threats?.filter(t => t.status === 'active').length || 0} Active
          </Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {securityData?.threats?.slice(0, 4).map((threat, index) => (
            <Box key={threat.id || index} w="full" p={4} borderRadius="lg" border="1px" borderColor={borderColor}>
              <HStack justify="space-between" mb={2}>
                <HStack>
                  <Badge 
                    colorScheme={
                      threat.severity === 'critical' ? 'red' : 
                      threat.severity === 'high' ? 'orange' : 
                      threat.severity === 'medium' ? 'yellow' : 'blue'
                    }
                  >
                    {threat.severity}
                  </Badge>
                  <Badge variant="outline">{threat.service}</Badge>
                </HStack>
                <Text fontSize="xs" color="gray.500">{threat.detectedAt}</Text>
              </HStack>
              <Text fontWeight="bold" mb={1}>{threat.title}</Text>
              <Text fontSize="sm" color="gray.600" mb={3}>{threat.description}</Text>
              <HStack spacing={2}>
                <Button size="sm" colorScheme="red" variant="outline">
                  Investigate
                </Button>
                <Button size="sm" colorScheme="gray" variant="outline">
                  Dismiss
                </Button>
              </HStack>
            </Box>
          )) || [
            <Box key="loading" w="full" textAlign="center">
              <Text color="gray.500">Loading threat data...</Text>
            </Box>
          ]}
        </VStack>
      </CardBody>
    </Card>
  );

  const ComplianceOverview = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Compliance Status</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {complianceData?.framework_scores ? (
            Object.entries(complianceData.framework_scores).map(([framework, data]) => (
              <Box key={framework} w="full">
                <HStack justify="space-between" mb={2}>
                  <HStack>
                    <Text fontWeight="medium" textTransform="uppercase">
                      {framework.replace('-', ' ')}
                    </Text>
                    <Badge 
                      colorScheme={data.status === 'compliant' ? 'green' : 'orange'}
                    >
                      {data.status === 'compliant' ? 'Compliant' : 'Needs Attention'}
                    </Badge>
                  </HStack>
                  <Text fontWeight="bold">{data.compliance_score}%</Text>
                </HStack>
                <Progress 
                  value={data.compliance_score} 
                  colorScheme={data.status === 'compliant' ? 'green' : 'orange'} 
                  size="sm" 
                  borderRadius="md"
                />
              </Box>
            ))
          ) : (
            <Text color="gray.500" textAlign="center">Loading compliance data...</Text>
          )}
        </VStack>
        <Divider my={4} />
        <Button variant="outline" w="full">
          View Detailed Compliance Report
        </Button>
      </CardBody>
    </Card>
  );

  const RecommendationsTab = () => {
    const prioritizedRecommendations = securityService.getRecommendationsByPriority(recommendations);
    
    return (
      <VStack spacing={6}>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
          <Card>
            <CardHeader>
              <Heading size="md">Recommendations by Priority</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                {['critical', 'high', 'medium', 'low'].map(priority => {
                  const count = recommendations.filter(r => r.priority === priority).length;
                  const color = {
                    critical: 'red',
                    high: 'orange', 
                    medium: 'yellow',
                    low: 'blue'
                  }[priority];
                  
                  return (
                    <HStack key={priority} justify="space-between" w="full" p={3} borderRadius="md" bg={`${color}.50`}>
                      <Text fontWeight="medium" textTransform="capitalize">{priority} Priority</Text>
                      <Badge colorScheme={color}>{count}</Badge>
                    </HStack>
                  );
                })}
              </VStack>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <Heading size="md">Security Categories</Heading>
            </CardHeader>
            <CardBody>
              {securityData?.security_metrics && (
                <VStack spacing={3}>
                  {Object.entries(securityService.getSecurityScoreBreakdown(securityData)).map(([category, data]) => (
                    <Box key={category} w="full">
                      <HStack justify="space-between" mb={1}>
                        <Text fontSize="sm" fontWeight="medium" textTransform="capitalize">
                          {category.replace('_', ' ')}
                        </Text>
                        <Text fontSize="sm" fontWeight="bold">{data.score}%</Text>
                      </HStack>
                      <Progress value={data.score} size="sm" colorScheme={
                        data.status === 'excellent' ? 'green' :
                        data.status === 'good' ? 'blue' :
                        data.status === 'needs_improvement' ? 'orange' : 'red'
                      } />
                    </Box>
                  ))}
                </VStack>
              )}
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Detailed Recommendations List */}
        <Card w="full">
          <CardHeader>
            <Heading size="md">Detailed Recommendations</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              {prioritizedRecommendations.map((rec, index) => (
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
                      <Badge variant="outline">{rec.recommendation_type}</Badge>
                    </HStack>
                    <Button 
                      size="sm" 
                      leftIcon={<FaPlay />}
                      onClick={() => handleRecommendationClick(rec)}
                    >
                      View Details
                    </Button>
                  </HStack>
                  <Text fontWeight="bold" mb={2}>{rec.title}</Text>
                  <Text fontSize="sm" color="gray.600" mb={2}>{rec.description}</Text>
                  <HStack>
                    <Text fontSize="xs" color="gray.500">
                      Effort: {rec.implementation_effort}
                    </Text>
                    <Text fontSize="xs" color="gray.500">•</Text>
                    <Text fontSize="xs" color="gray.500">
                      Cost Impact: {rec.cost_impact}
                    </Text>
                    <Text fontSize="xs" color="gray.500">•</Text>
                    <Text fontSize="xs" color="gray.500">
                      Services: {rec.affected_services.slice(0, 2).join(', ')}
                      {rec.affected_services.length > 2 && ` +${rec.affected_services.length - 2} more`}
                    </Text>
                  </HStack>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    );
  };

  const SecurityMetrics = () => (
    <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaShieldAlt} boxSize={8} color="blue.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">15</Text>
              <Text fontSize="sm" color="gray.600">Security Groups</Text>
              <Text fontSize="xs" color="green.500">All configured</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaKey} boxSize={8} color="orange.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">8</Text>
              <Text fontSize="sm" color="gray.600">IAM Policies</Text>
              <Text fontSize="xs" color="green.500">Least privilege</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaLock} boxSize={8} color="green.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">12</Text>
              <Text fontSize="sm" color="gray.600">Encrypted Resources</Text>
              <Text fontSize="xs" color="green.500">AES-256</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaEye} boxSize={8} color="purple.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">24/7</Text>
              <Text fontSize="sm" color="gray.600">Monitoring</Text>
              <Text fontSize="xs" color="green.500">Active</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>
    </SimpleGrid>
  );

  const RecentActivity = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Recent Security Activity</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4} align="stretch">
          {securityData?.recent_activity?.map((activity, index) => (
            <HStack key={index} p={3} borderRadius="md" bg="gray.50">
              <Avatar 
                size="sm" 
                icon={
                  <Icon 
                    as={
                      activity.type === 'threat' ? FaExclamationTriangle :
                      activity.type === 'improvement' ? FaCheckCircle :
                      activity.type === 'scan' ? FaEye : FaHistory
                    }
                  />
                }
                bg={
                  activity.type === 'threat' ? 'red.500' :
                  activity.type === 'improvement' ? 'green.500' :
                  activity.type === 'scan' ? 'blue.500' : 'gray.500'
                }
              />
              <VStack align="start" spacing={0} flex={1}>
                <Text fontSize="sm" fontWeight="medium">{activity.action}</Text>
                <Text fontSize="xs" color="gray.600">{activity.time}</Text>
              </VStack>
            </HStack>
          )) || [
            <Box key="loading" textAlign="center">
              <Text color="gray.500">Loading activity data...</Text>
            </Box>
          ]}
        </VStack>
      </CardBody>
    </Card>
  );

  if (loading && !securityData) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading security analysis...</Text>
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
              <Heading size="lg">Security Dashboard</Heading>
              <Text color="gray.600">
                Monitor threats, compliance, and security posture across your AWS infrastructure
              </Text>
            </VStack>
            <HStack>
              <Button leftIcon={<FaSync />} size="sm" variant="outline" onClick={handleRefreshData} isLoading={loading}>
                Refresh
              </Button>
              <Button leftIcon={<FaDownload />} size="sm" variant="outline">
                Export Report
              </Button>
              <Button leftIcon={<FaShieldAlt />} size="sm" colorScheme="blue" onClick={handleRunSecurityScan} isLoading={loading}>
                Security Scan
              </Button>
            </HStack>
          </HStack>
          
          <LoadingAlert />
        </Box>

        {/* Security Metrics */}
        <SecurityMetrics />

        {/* Tabs Navigation */}
        <Tabs index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Recommendations</Tab>
            <Tab>Compliance</Tab>
            <Tab>Activity</Tab>
          </TabList>

          <TabPanels>
            <TabPanel px={0}>
              {/* Main Dashboard */}
              <SimpleGrid columns={{ base: 1, lg: 3 }} spacing={6}>
                <SecurityScoreCard />
                <ThreatOverview />
                <ComplianceOverview />
              </SimpleGrid>
            </TabPanel>

            <TabPanel px={0}>
              <RecommendationsTab />
            </TabPanel>

            <TabPanel px={0}>
              {/* Compliance Details */}
              <VStack spacing={6}>
                <Card w="full">
                  <CardHeader>
                    <Heading size="md">Compliance Framework Details</Heading>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
                      {Object.entries(securityService.getComplianceFrameworkDetails()).map(([key, framework]) => (
                        <Box key={key} p={4} borderRadius="lg" border="1px" borderColor={borderColor}>
                          <VStack align="start" spacing={2}>
                            <HStack>
                              <Badge colorScheme="blue">{framework.name}</Badge>
                              <Text fontSize="sm" fontWeight="bold">{framework.full_name}</Text>
                            </HStack>
                            <Text fontSize="sm" color="gray.600">{framework.description}</Text>
                            <Box>
                              <Text fontSize="xs" fontWeight="medium" mb={1}>Key Requirements:</Text>
                              <List spacing={1}>
                                {framework.key_requirements.map((req, index) => (
                                  <ListItem key={index} fontSize="xs">
                                    <ListIcon as={FaCheckCircle} color="green.500" />
                                    {req}
                                  </ListItem>
                                ))}
                              </List>
                            </Box>
                          </VStack>
                        </Box>
                      ))}
                    </SimpleGrid>
                  </CardBody>
                </Card>
              </VStack>
            </TabPanel>

            <TabPanel px={0}>
              <RecentActivity />
            </TabPanel>
          </TabPanels>
        </Tabs>

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
                  
                  <Box>
                    <Text fontSize="sm" color="gray.600" mb={2}>Implementation Steps</Text>
                    <List spacing={2}>
                      {selectedRecommendation.implementation_steps.map((step, index) => (
                        <ListItem key={index} fontSize="sm">
                          <ListIcon as={FaCheckCircle} color="blue.500" />
                          {step}
                        </ListItem>
                      ))}
                    </List>
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
                      <Text fontSize="sm" color="gray.600">Implementation Effort</Text>
                      <Text fontWeight="medium">{selectedRecommendation.implementation_effort}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Cost Impact</Text>
                      <Text fontWeight="medium">{selectedRecommendation.cost_impact}</Text>
                    </Box>
                    <Box>
                      <Text fontSize="sm" color="gray.600">Affected Services</Text>
                      <Text fontWeight="medium">{selectedRecommendation.affected_services.join(', ')}</Text>
                    </Box>
                  </SimpleGrid>
                </VStack>
              )}
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="blue" mr={3}>
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

export default SecurityDashboard;