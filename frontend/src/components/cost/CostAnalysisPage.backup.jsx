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
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Badge,
  Button,
  Progress,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Icon,
  useColorModeValue,
  Spinner,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import {
  FaDollarSign,
  FaChartLine,
  FaServer,
  FaDatabase,
  FaCloud,
  FaShieldAlt,
  FaExclamationTriangle,
  FaBolt,
  FaRocket,
  FaSync,
  FaDownload,
  FaTrendingUp,
  FaTrendingDown,
} from 'react-icons/fa';
import costAnalysisService from '../../services/costAnalysisService';

const CostAnalysisPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [costData, setCostData] = useState(null);
  const [optimizationData, setOptimizationData] = useState(null);
  const [trendsData, setTrendsData] = useState(null);
  const [error, setError] = useState(null);
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const toast = useToast();

  // Load cost data on component mount
  useEffect(() => {
    loadCostData();
    loadRealTimeData();
  }, [selectedPeriod]);

  const loadCostData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get current project data from localStorage or context
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      
      if (currentProject.id) {
        // Load optimization recommendations
        const optimizations = await costAnalysisService.getCostOptimizationRecommendations(currentProject.id);
        setOptimizationData(optimizations);
        
        // Load cost trends
        const trends = await costAnalysisService.getCostTrends(currentProject.id, 12);
        setTrendsData(trends);
      }
      
      // Load real-time cost data
      const realTimeData = await costAnalysisService.getRealTimeCostData(currentProject.id || 'demo');
      setCostData(realTimeData);
      
    } catch (error) {
      console.error('Error loading cost data:', error);
      setError('Failed to load cost data. Using demo data.');
      
      // Fallback to mock data
      setCostData({
        current_month_spend: 2847.65,
        daily_spend: 94.92,
        projected_month_end: 3200.00,
        cost_alerts: [],
        top_services: [
          { service: 'EC2', cost: 1245.80, percentage: 43.7 },
          { service: 'RDS', cost: 678.90, percentage: 23.8 },
          { service: 'S3', cost: 234.50, percentage: 8.2 }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const loadRealTimeData = async () => {
    try {
      const realTimeData = await costAnalysisService.getRealTimeCostData();
      setCostData(prevData => ({
        ...prevData,
        ...realTimeData
      }));
    } catch (error) {
      console.error('Error loading real-time data:', error);
    }
  };

  const handleRefreshData = async () => {
    toast({
      title: 'Refreshing cost data...',
      status: 'info',
      duration: 2000,
    });
    await loadCostData();
    toast({
      title: 'Cost data updated',
      status: 'success',
      duration: 2000,
    });
  };

  const handleApplyOptimization = async (recommendationType) => {
    try {
      setLoading(true);
      const currentProject = JSON.parse(localStorage.getItem('currentProject') || '{}');
      
      await costAnalysisService.applyCostOptimization(
        currentProject.id || 'demo', 
        recommendationType, 
        {}
      );
      
      toast({
        title: 'Optimization Applied',
        description: `${recommendationType} optimization has been scheduled`,
        status: 'success',
        duration: 3000,
      });
      
      // Refresh data
      await loadCostData();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to apply optimization',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading && !costData) {
    return (
      <Container maxW="7xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Loading cost analysis data...</Text>
        </VStack>
      </Container>
    );
  }

  const LoadingAlert = () => (
    <Alert status="info" borderRadius="lg" mb={6}>
      <AlertIcon />
      <Box>
        <AlertTitle>Real-time Cost Analysis</AlertTitle>
        <AlertDescription>
          {error ? error : 'Live cost data integrated with AWS pricing. Data updates every 24 hours for accuracy.'}
        </AlertDescription>
      </Box>
    </Alert>
  );

  const StatCard = ({ icon, title, value, change, helpText, color = "blue" }) => (
    <Card>
      <CardBody>
        <HStack justify="space-between">
          <VStack align="start" spacing={1}>
            <HStack>
              <Icon as={icon} color={`${color}.500`} />
              <Text fontSize="sm" color="gray.600" fontWeight="medium">
                {title}
              </Text>
            </HStack>
            <Text fontSize="2xl" fontWeight="bold">
              {value}
            </Text>
            {change && (
              <HStack>
                <StatArrow type={change > 0 ? 'increase' : 'decrease'} />
                <Text fontSize="sm" color={change > 0 ? 'red.500' : 'green.500'}>
                  {Math.abs(change)}%
                </Text>
              </HStack>
            )}
            {helpText && (
              <Text fontSize="xs" color="gray.500">
                {helpText}
              </Text>
            )}
          </VStack>
        </HStack>
      </CardBody>
    </Card>
  );

  const ServiceBreakdown = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Service Cost Breakdown</Heading>
          <Button leftIcon={<FaSync />} size="sm" variant="outline" onClick={handleRefreshData}>
            Refresh
          </Button>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {costData?.top_services?.map((service, index) => (
            <Box key={index} w="full">
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="medium">{service.service}</Text>
                <HStack>
                  <Text fontWeight="bold">{costAnalysisService.formatCost(service.cost)}</Text>
                  <Badge colorScheme="blue">
                    {service.percentage.toFixed(1)}%
                  </Badge>
                </HStack>
              </HStack>
              <Progress 
                value={service.percentage} 
                colorScheme="blue" 
                size="sm" 
                borderRadius="md"
              />
              <Text fontSize="xs" color="gray.500" mt={1}>
                {service.percentage.toFixed(1)}% of total cost
              </Text>
            </Box>
          )) || [
            <Box key="loading" w="full" textAlign="center">
              <Text color="gray.500">Loading service breakdown...</Text>
            </Box>
          ]}
        </VStack>
      </CardBody>
    </Card>
  );

  const CostRecommendations = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Cost Optimization Recommendations</Heading>
          <Badge colorScheme="green" fontSize="sm">
            Potential Savings: {optimizationData ? costAnalysisService.formatCost(optimizationData.total_potential_savings) : '$--'}
          </Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {optimizationData?.optimization_recommendations?.map((rec, index) => (
            <Box key={index} w="full" p={4} borderRadius="lg" border="1px" borderColor={borderColor}>
              <HStack justify="space-between" mb={2}>
                <VStack align="start" spacing={1}>
                  <HStack>
                    <Text fontWeight="bold">{rec.category}</Text>
                    <Badge colorScheme="orange">
                      medium priority
                    </Badge>
                  </HStack>
                  <Text fontSize="sm" color="gray.600">{rec.recommendation}</Text>
                  <Text fontSize="sm">{rec.implementation}</Text>
                </VStack>
                <VStack align="end">
                  <Text fontSize="lg" fontWeight="bold" color="green.500">
                    {rec.potential_savings}
                  </Text>
                  <Text fontSize="xs" color="gray.500">potential savings</Text>
                </VStack>
              </HStack>
              <Button 
                size="sm" 
                colorScheme="blue" 
                variant="outline" 
                mt={2}
                onClick={() => handleApplyOptimization(rec.category)}
                isLoading={loading}
              >
                Apply Recommendation
              </Button>
            </Box>
          )) || [
            <Box key="loading" w="full" textAlign="center">
              <Text color="gray.500">Loading optimization recommendations...</Text>
            </Box>
          ]}
        </VStack>
      </CardBody>
    </Card>
  );

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg">Cost Analysis Dashboard</Heading>
              <Text color="gray.600">
                Monitor and optimize your AWS infrastructure costs
              </Text>
            </VStack>
            <HStack>
              <Button leftIcon={<FaSync />} size="sm" variant="outline" onClick={handleRefreshData} isLoading={loading}>
                Refresh
              </Button>
              <Button leftIcon={<FaDownload />} size="sm" colorScheme="blue">
                Export Report
              </Button>
            </HStack>
          </HStack>
          
          <LoadingAlert />
        </Box>

        {/* Key Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <StatCard
            icon={FaDollarSign}
            title="Current Month Spend"
            value={costData ? costAnalysisService.formatCost(costData.current_month_spend) : '$--'}
            change={trendsData ? ((costData.current_month_spend - trendsData.cost_trends[trendsData.cost_trends.length-2]?.actual_cost) / trendsData.cost_trends[trendsData.cost_trends.length-2]?.actual_cost * 100) : null}
            helpText="compared to last month"
            color="blue"
          />
          <StatCard
            icon={FaChartLine}
            title="Projected Month End"
            value={costData ? costAnalysisService.formatCost(costData.projected_month_end) : '$--'}
            helpText="based on current usage"
            color="orange"
          />
          <StatCard
            icon={FaBolt}
            title="Daily Spend"
            value={costData ? costAnalysisService.formatCost(costData.daily_spend) : '$--'}
            helpText="today's estimated cost"
            color="green"
          />
          <StatCard
            icon={FaRocket}
            title="Cost Efficiency Score"
            value={optimizationData ? `${Math.round(costAnalysisService.getCostEfficiencyScore(optimizationData.current_monthly_cost, optimizationData.current_monthly_cost * 0.8))}/100` : '--/100'}
            helpText="room for improvement"
            color="purple"
          />
        </SimpleGrid>

        {/* Tabs for different views */}
        <Tabs index={activeTab} onChange={setActiveTab}>
          <TabList>
            <Tab>Overview</Tab>
            <Tab>Trends</Tab>
            <Tab>Optimizations</Tab>
            <Tab>Detailed Analysis</Tab>
          </TabList>

          <TabPanels>
            <TabPanel px={0}>
              {/* Charts and Breakdowns */}
              <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                <ServiceBreakdown />
                <CostRecommendations />
              </SimpleGrid>
            </TabPanel>

            <TabPanel px={0}>
              {/* Cost Trends */}
              <VStack spacing={6}>
                <CostTrendsChart />
                <CostAnomaliesCard />
              </VStack>
            </TabPanel>

            <TabPanel px={0}>
              {/* Optimization Details */}
              <OptimizationDetailsCard />
            </TabPanel>

            <TabPanel px={0}>
              {/* Detailed Cost Table */}
              <DetailedCostTable />
            </TabPanel>
          </TabPanels>
        </Tabs>


      </VStack>
    </Container>
  );
};

export default CostAnalysisPage;