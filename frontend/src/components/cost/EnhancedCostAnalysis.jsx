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
  Switch,
  FormControl,
  FormLabel,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useToast,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
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
} from '@chakra-ui/react';
import {
  FaDollarSign,
  FaChartLine,
  FaLightbulb,
  FaGlobe,
  FaSync,
  FaDownload,
  FaCheckCircle,
  FaExclamationTriangle,
  FaInfoCircle,
} from 'react-icons/fa';

const EnhancedCostAnalysis = ({ project, questionnaire, services, onCostUpdate }) => {
  const [costData, setCostData] = useState(null);
  const [optimizations, setOptimizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('us-east-1');
  const [securityLevel, setSecurityLevel] = useState('medium');
  const [regionalComparison, setRegionalComparison] = useState(null);
  const [showOptimizations, setShowOptimizations] = useState(true);
  const [costTrends, setCostTrends] = useState(null);
  const toast = useToast();

  const awsRegions = [
    { value: 'us-east-1', label: 'US East (N. Virginia)' },
    { value: 'us-west-2', label: 'US West (Oregon)' },
    { value: 'eu-west-1', label: 'Europe (Ireland)' },
    { value: 'ap-southeast-1', label: 'Asia Pacific (Singapore)' },
    { value: 'ap-northeast-1', label: 'Asia Pacific (Tokyo)' },
  ];

  useEffect(() => {
    if (questionnaire && services) {
      fetchEnhancedCostEstimate();
    }
  }, [questionnaire, services, selectedRegion, securityLevel]);

  const fetchEnhancedCostEstimate = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/v1/cost-analysis/enhanced-estimate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questionnaire,
          services,
          region: selectedRegion,
          security_level: securityLevel,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to fetch enhanced cost estimate');
      }

      const data = await response.json();
      setCostData(data);
      setOptimizations(data.optimizations || []);
      
      if (onCostUpdate) {
        onCostUpdate(data);
      }

      // Fetch cost trends if project exists
      if (project?.id) {
        await fetchCostTrends(project.id);
      }

    } catch (error) {
      console.error('Error fetching enhanced cost estimate:', error);
      toast({
        title: 'Cost Analysis Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchCostTrends = async (projectId) => {
    try {
      const response = await fetch(`/api/v1/cost-analysis/cost-trends/${projectId}`);
      if (response.ok) {
        const trends = await response.json();
        setCostTrends(trends);
      }
    } catch (error) {
      console.error('Error fetching cost trends:', error);
    }
  };

  const compareRegionalCosts = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/v1/cost-analysis/compare-regions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questionnaire,
          services,
          security_level: securityLevel,
          regions: ['us-east-1', 'us-west-2', 'eu-west-1'],
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to compare regional costs');
      }

      const comparison = await response.json();
      setRegionalComparison(comparison);

    } catch (error) {
      console.error('Error comparing regional costs:', error);
      toast({
        title: 'Regional Comparison Failed',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const getOptimizationIcon = (category) => {
    const iconMap = {
      'Reserved Instances': FaCheckCircle,
      'Spot Instances': FaExclamationTriangle,
      'Right Sizing': FaInfoCircle,
      'Storage Optimization': FaLightbulb,
    };
    return iconMap[category] || FaLightbulb;
  };

  const getOptimizationColor = (priority) => {
    const colorMap = {
      'High': 'red',
      'Medium': 'orange',
      'Low': 'blue',
    };
    return colorMap[priority] || 'gray';
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  if (loading && !costData) {
    return (
      <Box textAlign="center" py={10}>
        <VStack spacing={4}>
          <Spinner size="lg" color="blue.500" />
          <Text>Analyzing costs with real-time AWS pricing...</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      {/* Cost Analysis Header */}
      <Card shadow="lg">
        <CardHeader>
          <HStack justify="space-between" align="center">
            <HStack>
              <Icon as={FaDollarSign} color="green.500" boxSize={6} />
              <Heading size="lg">Enhanced Cost Analysis</Heading>
            </HStack>
            <HStack spacing={3}>
              <Button
                leftIcon={<FaGlobe />}
                colorScheme="blue"
                variant="outline"
                onClick={compareRegionalCosts}
                isLoading={loading}
                size="sm"
              >
                Compare Regions
              </Button>
              <Button
                leftIcon={<FaSync />}
                colorScheme="green"
                onClick={fetchEnhancedCostEstimate}
                isLoading={loading}
                size="sm"
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <FormControl>
              <FormLabel>Region</FormLabel>
              <Select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
              >
                {awsRegions.map((region) => (
                  <option key={region.value} value={region.value}>
                    {region.label}
                  </option>
                ))}
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel>Security Level</FormLabel>
              <Select
                value={securityLevel}
                onChange={(e) => setSecurityLevel(e.target.value)}
              >
                <option value="basic">Basic</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </Select>
            </FormControl>

            <FormControl>
              <HStack justify="space-between">
                <FormLabel mb={0}>Show Optimizations</FormLabel>
                <Switch
                  colorScheme="green"
                  isChecked={showOptimizations}
                  onChange={(e) => setShowOptimizations(e.target.checked)}
                />
              </HStack>
            </FormControl>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Cost Summary */}
      {costData && (
        <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
          <Card shadow="md">
            <CardBody>
              <Stat>
                <StatLabel>Monthly Estimate</StatLabel>
                <StatNumber color="green.600">
                  {formatCurrency(costData.total_monthly_cost)}
                </StatNumber>
                <StatHelpText>
                  <HStack>
                    <Text>{costData.estimated_cost}</Text>
                    <Badge colorScheme="blue" size="sm">
                      {costData.currency}
                    </Badge>
                  </HStack>
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <Stat>
                <StatLabel>Pricing Confidence</StatLabel>
                <StatNumber>{costData.pricing_confidence}%</StatNumber>
                <Progress
                  value={costData.pricing_confidence}
                  colorScheme={costData.pricing_confidence > 80 ? 'green' : 'orange'}
                  size="sm"
                  mt={2}
                />
              </Stat>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <Stat>
                <StatLabel>Region</StatLabel>
                <StatNumber fontSize="lg">{selectedRegion}</StatNumber>
                <StatHelpText>
                  {awsRegions.find(r => r.value === selectedRegion)?.label}
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card shadow="md">
            <CardBody>
              <Stat>
                <StatLabel>Last Updated</StatLabel>
                <StatNumber fontSize="sm">{costData.last_updated}</StatNumber>
                <StatHelpText>
                  <Badge 
                    colorScheme={costData.includes_free_tier ? 'green' : 'gray'}
                    size="sm"
                  >
                    {costData.includes_free_tier ? 'Includes Free Tier' : 'No Free Tier'}
                  </Badge>
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>
      )}

      {/* Cost Breakdown */}
      {costData?.cost_breakdown && (
        <Card shadow="lg">
          <CardHeader>
            <Heading size="md">Service Cost Breakdown</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {costData.cost_breakdown.map((item, index) => (
                <Box
                  key={index}
                  p={4}
                  borderRadius="md"
                  border="1px"
                  borderColor="gray.200"
                  bg="gray.50"
                >
                  <VStack align="start" spacing={2}>
                    <HStack justify="space-between" w="full">
                      <Text fontWeight="semibold" fontSize="sm">
                        {item.service}
                      </Text>
                      <Badge colorScheme="orange">AWS</Badge>
                    </HStack>
                    <Text color="green.600" fontWeight="bold" fontSize="lg">
                      {item.estimated_monthly_cost}
                    </Text>
                    <Text fontSize="xs" color="gray.600">
                      {item.description}
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>
      )}

      {/* Cost Trends - Simplified Table View */}
      {costTrends && (
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaChartLine} color="blue.500" />
              <Heading size="md">Cost Trends (Last 6 Months)</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 2, md: 6 }} spacing={4}>
              {costTrends.cost_trends.slice(-6).map((trend, index) => (
                <Box key={index} p={4} bg="gray.50" borderRadius="md" textAlign="center">
                  <Text fontSize="sm" color="gray.600" mb={1}>{trend.month}</Text>
                  <Text fontWeight="bold" color="green.600" fontSize="lg">
                    {formatCurrency(trend.actual_cost)}
                  </Text>
                  <Text fontSize="xs" color="blue.600">
                    Proj: {formatCurrency(trend.projected_cost)}
                  </Text>
                </Box>
              ))}
            </SimpleGrid>
            
            {costTrends.trend_analysis && (
              <Alert status="info" mt={4}>
                <AlertIcon />
                <AlertDescription>
                  <Text fontSize="sm">
                    <strong>Trend Analysis:</strong> {costTrends.trend_analysis.direction} 
                    {' '}({costTrends.trend_analysis.percentage_change}% change). 
                    Average monthly cost: {formatCurrency(costTrends.trend_analysis.average_monthly_cost)}
                  </Text>
                </AlertDescription>
              </Alert>
            )}
          </CardBody>
        </Card>
      )}

      {/* Cost Optimizations */}
      {showOptimizations && optimizations.length > 0 && (
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaLightbulb} color="yellow.500" />
              <Heading size="md">Cost Optimization Recommendations</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <Accordion allowMultiple>
              {optimizations.map((optimization, index) => (
                <AccordionItem key={index}>
                  <AccordionButton>
                    <Box flex="1" textAlign="left">
                      <HStack>
                        <Icon
                          as={getOptimizationIcon(optimization.category)}
                          color={`${getOptimizationColor(optimization.priority)}.500`}
                        />
                        <Text fontWeight="semibold">{optimization.category}</Text>
                        <Badge
                          colorScheme={getOptimizationColor(optimization.priority)}
                          variant="subtle"
                        >
                          {optimization.priority} Priority
                        </Badge>
                        {optimization.potential_savings && (
                          <Badge colorScheme="green" ml={2}>
                            Save {optimization.potential_savings}
                          </Badge>
                        )}
                      </HStack>
                    </Box>
                    <AccordionIcon />
                  </AccordionButton>
                  <AccordionPanel pb={4}>
                    <VStack align="start" spacing={3}>
                      <Text fontSize="sm" color="gray.700">
                        {optimization.description}
                      </Text>
                      
                      {optimization.implementation_steps && (
                        <Box>
                          <Text fontWeight="semibold" fontSize="sm" mb={2}>
                            Implementation Steps:
                          </Text>
                          <List spacing={1} fontSize="sm">
                            {optimization.implementation_steps.map((step, stepIndex) => (
                              <ListItem key={stepIndex}>
                                <ListIcon as={FaCheckCircle} color="green.500" />
                                {step}
                              </ListItem>
                            ))}
                          </List>
                        </Box>
                      )}
                      
                      {optimization.estimated_effort && (
                        <HStack>
                          <Text fontSize="sm" fontWeight="semibold">
                            Effort:
                          </Text>
                          <Badge variant="outline">
                            {optimization.estimated_effort}
                          </Badge>
                        </HStack>
                      )}
                    </VStack>
                  </AccordionPanel>
                </AccordionItem>
              ))}
            </Accordion>
          </CardBody>
        </Card>
      )}

      {/* Regional Comparison */}
      {regionalComparison && (
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaGlobe} color="blue.500" />
              <Heading size="md">Regional Cost Comparison</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <Alert status="success">
                <AlertIcon />
                <AlertDescription>
                  Cheapest region: <strong>{regionalComparison.cheapest_region}</strong>
                  {regionalComparison.cost_variance && (
                    <Text fontSize="sm" mt={1}>
                      Cost variance across regions: {regionalComparison.cost_variance.toFixed(1)}%
                    </Text>
                  )}
                </AlertDescription>
              </Alert>

              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} w="full">
                {Object.entries(regionalComparison.regional_comparison).map(([region, data]) => (
                  <Box
                    key={region}
                    p={4}
                    borderRadius="md"
                    border="2px"
                    borderColor={region === regionalComparison.cheapest_region ? 'green.200' : 'gray.200'}
                    bg={region === regionalComparison.cheapest_region ? 'green.50' : 'white'}
                  >
                    <VStack align="start" spacing={2}>
                      <HStack justify="space-between" w="full">
                        <Text fontWeight="semibold">
                          {awsRegions.find(r => r.value === region)?.label || region}
                        </Text>
                        {region === regionalComparison.cheapest_region && (
                          <Badge colorScheme="green">Cheapest</Badge>
                        )}
                      </HStack>
                      
                      {data.error ? (
                        <Text color="red.500" fontSize="sm">{data.error}</Text>
                      ) : (
                        <>
                          <Text color="green.600" fontWeight="bold" fontSize="lg">
                            {formatCurrency(data.total_monthly_cost)}
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {data.cost_range}
                          </Text>
                        </>
                      )}
                    </VStack>
                  </Box>
                ))}
              </SimpleGrid>

              {regionalComparison.recommendations && (
                <Box w="full">
                  <Text fontWeight="semibold" mb={2}>Recommendations:</Text>
                  <List spacing={1}>
                    {regionalComparison.recommendations.map((rec, index) => (
                      <ListItem key={index} fontSize="sm">
                        <ListIcon as={FaInfoCircle} color="blue.500" />
                        {rec}
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </VStack>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
};

export default EnhancedCostAnalysis;