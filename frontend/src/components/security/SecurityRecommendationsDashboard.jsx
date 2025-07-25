import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  SimpleGrid,
  Badge,
  Select,
  FormControl,
  FormLabel,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useToast,
  Progress,
  Icon,
  Tooltip,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  List,
  ListItem,
  ListIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Code,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Textarea,
  Input,
} from '@chakra-ui/react';
import {
  FaShieldAlt,
  FaExclamationTriangle,
  FaBolt,
  FaCheckCircle,
  FaInfoCircle,
  FaCogs,
  FaSync,
  FaEye,
  FaPlay,
  FaDownload,
  FaRobot,
  FaGraduationCap,
  FaAward,
  FaBug,
  FaSearch,
  FaFilter,
} from 'react-icons/fa';

const SecurityRecommendationsDashboard = ({ project, questionnaire, services }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [securityAnalysis, setSecurityAnalysis] = useState(null);
  const [awsSecurityUpdates, setAwsSecurityUpdates] = useState([]);
  const [complianceDashboard, setComplianceDashboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [implementationPlan, setImplementationPlan] = useState(null);
  const [filterPriority, setFilterPriority] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [openaiApiKey, setOpenaiApiKey] = useState('');
  const [bulkAnalysisProjects, setBulkAnalysisProjects] = useState([]);
  const { 
    isOpen: isRecommendationModalOpen, 
    onOpen: onRecommendationModalOpen, 
    onClose: onRecommendationModalClose 
  } = useDisclosure();
  const { 
    isOpen: isImplementationModalOpen, 
    onOpen: onImplementationModalOpen, 
    onClose: onImplementationModalClose 
  } = useDisclosure();
  const toast = useToast();

  const recommendationTypes = [
    { value: 'all', label: 'All Types' },
    { value: 'new_feature', label: 'New Features' },
    { value: 'vulnerability_fix', label: 'Vulnerability Fixes' },
    { value: 'compliance_update', label: 'Compliance Updates' },
    { value: 'best_practice', label: 'Best Practices' },
    { value: 'cost_optimization', label: 'Cost Optimization' },
  ];

  const priorities = [
    { value: 'all', label: 'All Priorities' },
    { value: 'critical', label: 'Critical' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  useEffect(() => {
    if (project?.id && questionnaire && services) {
      analyzeProjectSecurity();
      fetchAwsSecurityUpdates();
      fetchComplianceDashboard();
    }
  }, [project, questionnaire, services]);

  const analyzeProjectSecurity = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/v1/security/analyze-project', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: project.id,
          questionnaire,
          services,
          include_ai_recommendations: !!openaiApiKey,
          security_level: questionnaire.security_level || 'medium',
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze project security');
      }

      const analysis = await response.json();
      setSecurityAnalysis(analysis);
      setRecommendations(analysis.recommendations || []);

    } catch (error) {
      console.error('Error analyzing project security:', error);
      toast({
        title: 'Security Analysis Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchRecommendations = async () => {
    try {
      const params = new URLSearchParams();
      if (filterPriority !== 'all') params.append('priority_filter', filterPriority);
      if (filterType !== 'all') params.append('recommendation_type', filterType);
      params.append('limit', '20');

      const response = await fetch(`/api/v1/security/recommendations/${project.id}?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch recommendations');
      }

      const recs = await response.json();
      setRecommendations(recs);

    } catch (error) {
      console.error('Error fetching recommendations:', error);
      toast({
        title: 'Failed to Load Recommendations',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const fetchAwsSecurityUpdates = async () => {
    try {
      const response = await fetch('/api/v1/security/aws-security-updates');
      
      if (response.ok) {
        const updates = await response.json();
        setAwsSecurityUpdates(updates.aws_security_updates || []);
      }
    } catch (error) {
      console.error('Error fetching AWS security updates:', error);
    }
  };

  const fetchComplianceDashboard = async () => {
    try {
      const response = await fetch(`/api/v1/security/compliance-dashboard/${project.id}`);
      
      if (response.ok) {
        const dashboard = await response.json();
        setComplianceDashboard(dashboard);
      }
    } catch (error) {
      console.error('Error fetching compliance dashboard:', error);
    }
  };

  const getImplementationPlan = async (recommendation) => {
    try {
      setLoading(true);
      
      const response = await fetch(`/api/v1/security/recommendation-implementation-plan/${recommendation.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: project.id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get implementation plan');
      }

      const plan = await response.json();
      setImplementationPlan(plan);
      setSelectedRecommendation(recommendation);
      onImplementationModalOpen();

    } catch (error) {
      console.error('Error getting implementation plan:', error);
      toast({
        title: 'Failed to Load Implementation Plan',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationIcon = (type) => {
    const iconMap = {
      'new_feature': FaBolt,
      'vulnerability_fix': FaBug,
      'compliance_update': FaAward,
      'best_practice': FaGraduationCap,
      'cost_optimization': FaCogs,
    };
    return iconMap[type] || FaInfoCircle;
  };

  const getRecommendationColor = (type) => {
    const colorMap = {
      'new_feature': 'blue',
      'vulnerability_fix': 'red',
      'compliance_update': 'purple',
      'best_practice': 'green',
      'cost_optimization': 'orange',
    };
    return colorMap[type] || 'gray';
  };

  const getPriorityColor = (priority) => {
    const colorMap = {
      'critical': 'red',
      'high': 'orange',
      'medium': 'yellow',
      'low': 'blue',
    };
    return colorMap[priority] || 'gray';
  };

  const getSecurityScoreColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'yellow';
    return 'red';
  };

  const filteredRecommendations = recommendations.filter(rec => {
    const priorityMatch = filterPriority === 'all' || rec.priority === filterPriority;
    const typeMatch = filterType === 'all' || rec.recommendation_type === filterType;
    return priorityMatch && typeMatch;
  });

  if (loading && !securityAnalysis) {
    return (
      <Box textAlign="center" py={10}>
        <VStack spacing={4}>
          <Spinner size="lg" color="blue.500" />
          <Text>Analyzing security posture with AI recommendations...</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Security Dashboard Header */}
      <Card shadow="lg">
        <CardHeader>
          <HStack justify="space-between" align="center">
            <HStack>
              <Icon as={FaShieldAlt} color="blue.500" boxSize={6} />
              <Heading size="lg">AI Security Recommendations</Heading>
            </HStack>
            <HStack spacing={3}>
              <Button
                leftIcon={<FaRobot />}
                colorScheme="purple"
                variant="outline"
                onClick={analyzeProjectSecurity}
                isLoading={loading}
                size="sm"
              >
                Re-analyze with AI
              </Button>
              <Button
                leftIcon={<FaSync />}
                colorScheme="blue"
                onClick={fetchRecommendations}
                isLoading={loading}
                size="sm"
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <FormControl>
              <FormLabel>OpenAI API Key (Optional)</FormLabel>
              <Input
                type="password"
                placeholder="sk-..."
                value={openaiApiKey}
                onChange={(e) => setOpenaiApiKey(e.target.value)}
                size="sm"
              />
              <Text fontSize="xs" color="gray.600" mt={1}>
                Required for AI-powered recommendations. Key is not stored.
              </Text>
            </FormControl>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Security Analysis Overview */}
      {securityAnalysis && (
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
          <Card shadow="md">
            <CardBody>
              <VStack spacing={3}>
                <Icon as={FaShieldAlt} boxSize={8} color={getSecurityScoreColor(securityAnalysis.security_posture_score)} />
                <VStack spacing={1}>
                  <Text fontSize="2xl" fontWeight="bold" color={`${getSecurityScoreColor(securityAnalysis.security_posture_score)}.500`}>
                    {securityAnalysis.security_posture_score}/100
                  </Text>
                  <Text fontSize="sm" color="gray.600">Security Score</Text>
                </VStack>
                <Progress
                  value={securityAnalysis.security_posture_score}
                  colorScheme={getSecurityScoreColor(securityAnalysis.security_posture_score)}
                  w="full"
                  size="lg"
                />
              </VStack>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <VStack spacing={3}>
                <Icon as={FaExclamationTriangle} boxSize={8} color="red.500" />
                <VStack spacing={1}>
                  <Text fontSize="2xl" fontWeight="bold" color="red.500">
                    {securityAnalysis.vulnerabilities_count}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Vulnerabilities</Text>
                </VStack>
              </VStack>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <VStack spacing={3}>
                <Icon as={FaCheckCircle} boxSize={8} color="blue.500" />
                <VStack spacing={1}>
                  <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                    {recommendations.length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Recommendations</Text>
                </VStack>
              </VStack>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <VStack spacing={3}>
                <Icon as={FaAward} boxSize={8} color="purple.500" />
                <VStack spacing={1}>
                  <Text fontSize="lg" fontWeight="bold" color="purple.500">
                    {Object.keys(securityAnalysis.compliance_status || {}).length}
                  </Text>
                  <Text fontSize="sm" color="gray.600">Compliance Frameworks</Text>
                </VStack>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>
      )}

      {/* Compliance Status */}
      {complianceDashboard && (
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaAward} color="purple.500" />
              <Heading size="md">Compliance Dashboard</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Alert status="info">
                <AlertIcon />
                <AlertDescription>
                  Overall compliance score: <strong>{complianceDashboard.overall_compliance_score}/100</strong>
                </AlertDescription>
              </Alert>

              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} w="full">
                {complianceDashboard.compliance_frameworks.map((framework) => (
                  <Box
                    key={framework}
                    p={4}
                    borderRadius="md"
                    border="1px"
                    borderColor="gray.200"
                    bg="gray.50"
                  >
                    <VStack align="start" spacing={2}>
                      <HStack justify="space-between" w="full">
                        <Text fontWeight="semibold" textTransform="uppercase">
                          {framework}
                        </Text>
                        <Badge colorScheme="purple">{framework}</Badge>
                      </HStack>
                      
                      {complianceDashboard.framework_scores[framework] && (
                        <>
                          <Text color="purple.600" fontWeight="bold" fontSize="lg">
                            {complianceDashboard.framework_scores[framework]}/100
                          </Text>
                          <Progress
                            value={complianceDashboard.framework_scores[framework]}
                            colorScheme={complianceDashboard.framework_scores[framework] >= 70 ? 'green' : 'red'}
                            w="full"
                            size="sm"
                          />
                        </>
                      )}
                    </VStack>
                  </Box>
                ))}
              </SimpleGrid>

              {complianceDashboard.critical_gaps.length > 0 && (
                <Alert status="warning">
                  <AlertIcon />
                  <VStack align="start" spacing={2}>
                    <Text fontWeight="semibold">Critical Compliance Gaps:</Text>
                    {complianceDashboard.critical_gaps.map((gap, index) => (
                      <Text key={index} fontSize="sm">
                        • {gap.framework}: {gap.gap} (Score: {gap.score}/100)
                      </Text>
                    ))}
                  </VStack>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Filters */}
      <Card shadow="md">
        <CardBody>
          <HStack spacing={4}>
            <FormControl maxW="200px">
              <FormLabel size="sm">Priority Filter</FormLabel>
              <Select
                size="sm"
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
              >
                {priorities.map((priority) => (
                  <option key={priority.value} value={priority.value}>
                    {priority.label}
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl maxW="200px">
              <FormLabel size="sm">Type Filter</FormLabel>
              <Select
                size="sm"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                {recommendationTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </Select>
            </FormControl>

            <Button
              leftIcon={<FaFilter />}
              colorScheme="blue"
              variant="outline"
              onClick={fetchRecommendations}
              size="sm"
              mt={6}
            >
              Apply Filters
            </Button>
          </HStack>
        </CardBody>
      </Card>

      {/* Recommendations List */}
      <Card shadow="lg">
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Security Recommendations</Heading>
            <Badge colorScheme="blue" variant="subtle" px={3} py={1}>
              {filteredRecommendations.length} recommendations
            </Badge>
          </HStack>
        </CardHeader>
        <CardBody>
          {filteredRecommendations.length > 0 ? (
            <Accordion allowMultiple>
              {filteredRecommendations.map((recommendation) => (
                <AccordionItem key={recommendation.id}>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <HStack>
                        <Icon
                          as={getRecommendationIcon(recommendation.recommendation_type)}
                          color={`${getRecommendationColor(recommendation.recommendation_type)}.500`}
                        />
                        <Text fontWeight="semibold">{recommendation.title}</Text>
                        <Badge
                          colorScheme={getPriorityColor(recommendation.priority)}
                          variant="solid"
                        >
                          {recommendation.priority}
                        </Badge>
                        <Badge
                          colorScheme={getRecommendationColor(recommendation.recommendation_type)}
                          variant="outline"
                        >
                          {recommendation.recommendation_type.replace('_', ' ')}
                        </Badge>
                      </HStack>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={4}>
                      <Text fontSize="sm" color="gray.700">
                        {recommendation.description}
                      </Text>
                      
                      <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
                        <Box>
                          <Text fontWeight="semibold" fontSize="sm" mb={2}>
                            Affected Services:
                          </Text>
                          <HStack wrap="wrap" spacing={2}>
                            {recommendation.affected_services.map((service, index) => (
                              <Badge key={index} variant="outline" colorScheme="orange">
                                {service}
                              </Badge>
                            ))}
                          </HStack>
                        </Box>

                        <Box>
                          <Text fontWeight="semibold" fontSize="sm" mb={2}>
                            Implementation Details:
                          </Text>
                          <VStack align="start" spacing={1} fontSize="sm">
                            <HStack>
                              <Text>Effort:</Text>
                              <Badge variant="outline">{recommendation.implementation_effort}</Badge>
                            </HStack>
                            <HStack>
                              <Text>Cost Impact:</Text>
                              <Badge variant="outline">{recommendation.cost_impact}</Badge>
                            </HStack>
                          </VStack>
                        </Box>
                      </SimpleGrid>

                      {recommendation.compliance_frameworks.length > 0 && (
                        <Box>
                          <Text fontWeight="semibold" fontSize="sm" mb={2}>
                            Compliance Frameworks:
                          </Text>
                          <HStack wrap="wrap" spacing={2}>
                            {recommendation.compliance_frameworks.map((framework, index) => (
                              <Badge key={index} colorScheme="purple" variant="subtle">
                                {framework}
                              </Badge>
                            ))}
                          </HStack>
                        </Box>
                      )}

                      <Box>
                        <Text fontWeight="semibold" fontSize="sm" mb={2}>
                          Implementation Steps:
                        </Text>
                        <List spacing={1} fontSize="sm">
                          {recommendation.implementation_steps.map((step, index) => (
                            <ListItem key={index}>
                              <ListIcon as={FaCheckCircle} color="green.500" />
                              {step}
                            </ListItem>
                          ))}
                        </List>
                      </Box>

                      <HStack spacing={3}>
                        <Button
                          size="sm"
                          colorScheme="blue"
                          leftIcon={<FaEye />}
                          onClick={() => getImplementationPlan(recommendation)}
                        >
                          Implementation Plan
                        </Button>
                        
                        {recommendation.aws_documentation_url && (
                          <Button
                            size="sm"
                            variant="outline"
                            leftIcon={<FaSearch />}
                            as="a"
                            href={recommendation.aws_documentation_url}
                            target="_blank"
                          >
                            AWS Docs
                          </Button>
                        )}
                      </HStack>
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>
          ) : (
            <Box textAlign="center" py={10}>
              <VStack spacing={4}>
                <Icon as={FaShieldAlt} boxSize={12} color="gray.300" />
                <Text color="gray.500">No recommendations match your current filters</Text>
                <Button
                  colorScheme="blue"
                  variant="outline"
                  onClick={() => {
                    setFilterPriority('all');
                    setFilterType('all');
                    fetchRecommendations();
                  }}
                >
                  Clear Filters
                </Button>
              </VStack>
            </Box>
          )}
        </CardBody>
      </Card>

      {/* AWS Security Updates */}
      {awsSecurityUpdates.length > 0 && (
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaBolt} color="orange.500" />
              <Heading size="md">Latest AWS Security Updates</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              {awsSecurityUpdates.slice(0, 3).map((update, index) => (
                <Box
                  key={index}
                  p={4}
                  borderRadius="md"
                  border="1px"
                  borderColor="orange.200"
                  bg="orange.50"
                  w="full"
                >
                  <VStack align="start" spacing={2}>
                    <HStack justify="space-between" w="full">
                      <Text fontWeight="semibold" color="orange.800">
                        {update.title}
                      </Text>
                      <Badge colorScheme="orange">{update.date}</Badge>
                    </HStack>
                    <Text fontSize="sm" color="orange.700">
                      {update.description}
                    </Text>
                    <Text fontSize="sm" color="orange.600" fontWeight="semibold">
                      Impact: {update.impact}
                    </Text>
                    {update.services && (
                      <HStack wrap="wrap" spacing={2}>
                        {update.services.map((service, serviceIndex) => (
                          <Badge key={serviceIndex} variant="outline" colorScheme="orange">
                            {service}
                          </Badge>
                        ))}
                      </HStack>
                    )}
                  </VStack>
                </Box>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Implementation Plan Modal */}
      <Modal 
        isOpen={isImplementationModalOpen} 
        onClose={onImplementationModalClose} 
        size="4xl"
      >
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            Implementation Plan: {selectedRecommendation?.title}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {implementationPlan && (
              <Tabs>
                <TabList>
                  <Tab>Overview</Tab>
                  <Tab>Prerequisites</Tab>
                  <Tab>Testing</Tab>
                  <Tab>Rollback</Tab>
                  {selectedRecommendation?.terraform_snippet && <Tab>Terraform</Tab>}
                  {selectedRecommendation?.cloudformation_snippet && <Tab>CloudFormation</Tab>}
                </TabList>

                <TabPanels>
                  <TabPanel>
                    <VStack align="start" spacing={4}>
                      <SimpleGrid columns={2} spacing={4} w="full">
                        <Box>
                          <Text fontWeight="semibold">Timeline:</Text>
                          <Text>{implementationPlan.implementation_timeline}</Text>
                        </Box>
                        <Box>
                          <Text fontWeight="semibold">Estimated Cost:</Text>
                          <Text>{implementationPlan.estimated_cost}</Text>
                        </Box>
                      </SimpleGrid>
                      
                      <Box>
                        <Text fontWeight="semibold" mb={2}>Success Metrics:</Text>
                        <List spacing={1}>
                          {implementationPlan.success_metrics.map((metric, index) => (
                            <ListItem key={index}>
                              <ListIcon as={FaCheckCircle} color="green.500" />
                              {metric}
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    </VStack>
                  </TabPanel>

                  <TabPanel>
                    <List spacing={2}>
                      {implementationPlan.prerequisites.map((prereq, index) => (
                        <ListItem key={index}>
                          <ListIcon as={FaInfoCircle} color="blue.500" />
                          {prereq}
                        </ListItem>
                      ))}
                    </List>
                  </TabPanel>

                  <TabPanel>
                    <List spacing={2}>
                      {implementationPlan.testing_plan.map((test, index) => (
                        <ListItem key={index}>
                          <ListIcon as={FaCheckCircle} color="green.500" />
                          {test}
                        </ListItem>
                      ))}
                    </List>
                  </TabPanel>

                  <TabPanel>
                    <List spacing={2}>
                      {implementationPlan.rollback_plan.map((step, index) => (
                        <ListItem key={index}>
                          <ListIcon as={FaExclamationTriangle} color="orange.500" />
                          {step}
                        </ListItem>
                      ))}
                    </List>
                  </TabPanel>

                  {selectedRecommendation?.terraform_snippet && (
                    <TabPanel>
                      <Code
                        p={4}
                        borderRadius="md"
                        w="full"
                        overflow="auto"
                        fontSize="sm"
                        whiteSpace="pre"
                      >
                        {selectedRecommendation.terraform_snippet}
                      </Code>
                    </TabPanel>
                  )}

                  {selectedRecommendation?.cloudformation_snippet && (
                    <TabPanel>
                      <Code
                        p={4}
                        borderRadius="md"
                        w="full"
                        overflow="auto"
                        fontSize="sm"
                        whiteSpace="pre"
                      >
                        {selectedRecommendation.cloudformation_snippet}
                      </Code>
                    </TabPanel>
                  )}
                </TabPanels>
              </Tabs>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onImplementationModalClose}>
              Close
            </Button>
            <Button colorScheme="blue" leftIcon={<FaPlay />}>
              Start Implementation
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default SecurityRecommendationsDashboard;