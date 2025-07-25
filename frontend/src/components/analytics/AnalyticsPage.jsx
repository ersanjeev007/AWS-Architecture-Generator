import React, { useState } from 'react';
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
  Flex,
  Select,
  Tab,
  Tabs,
  TabList,
  TabPanel,
  TabPanels,
} from '@chakra-ui/react';
import {
  FaChartLine,
  FaUsers,
  FaCloud,
  FaArrowUp,
  FaArrowDown,
  FaCheckCircle,
  FaRocket,
  FaEye,
  FaDownload,
  FaFilter,
} from 'react-icons/fa';

const AnalyticsPage = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedTab, setSelectedTab] = useState(0);

  // Mock analytics data
  const analyticsData = {
    overview: {
      totalProjects: 47,
      activeUsers: 12,
      totalDeployments: 156,
      successRate: 94.2,
      averageProjectTime: '24 minutes',
      costSavings: 34560,
    },
    usage: {
      dailyActiveUsers: 8,
      weeklyActiveUsers: 12,
      monthlyActiveUsers: 24,
      averageSessionDuration: '45 minutes',
      projectsCreated: 47,
      deploymentsExecuted: 156,
    },
    popular: {
      services: [
        { name: 'EC2', usage: 89, projects: 42 },
        { name: 'RDS', usage: 73, projects: 34 },
        { name: 'S3', usage: 95, projects: 45 },
        { name: 'Lambda', usage: 67, projects: 31 },
        { name: 'CloudFront', usage: 45, projects: 21 },
      ],
      architectures: [
        { name: 'Web Application', count: 18, percentage: 38.3 },
        { name: 'Microservices', count: 14, percentage: 29.8 },
        { name: 'Data Pipeline', count: 8, percentage: 17.0 },
        { name: 'Serverless', count: 7, percentage: 14.9 },
      ],
      regions: [
        { name: 'us-east-1', projects: 28, percentage: 59.6 },
        { name: 'eu-west-1', projects: 12, percentage: 25.5 },
        { name: 'ap-southeast-1', projects: 5, percentage: 10.6 },
        { name: 'us-west-2', projects: 2, percentage: 4.3 },
      ]
    },
    performance: {
      averageLoadTime: '1.2s',
      deploymentSuccess: 94.2,
      userSatisfaction: 4.7,
      systemUptime: 99.9,
    }
  };

  const InfoAlert = () => (
    <Alert status="info" borderRadius="lg" mb={6}>
      <AlertIcon />
      <Box>
        <AlertTitle>Advanced Analytics Dashboard</AlertTitle>
        <AlertDescription>
          Track platform usage, performance metrics, and user engagement with comprehensive analytics.
          Data updates every hour for accurate insights.
        </AlertDescription>
      </Box>
    </Alert>
  );

  const MetricCard = ({ icon, title, value, change, subtitle, color = "blue" }) => (
    <Card>
      <CardBody>
        <VStack spacing={3}>
          <HStack justify="space-between" w="full">
            <Icon as={icon} boxSize={6} color={`${color}.500`} />
            {change && (
              <Badge colorScheme={change > 0 ? 'green' : 'red'}>
                <HStack spacing={1}>
                  <Icon as={change > 0 ? FaArrowUp : FaArrowDown} boxSize={3} />
                  <Text>{Math.abs(change)}%</Text>
                </HStack>
              </Badge>
            )}
          </HStack>
          <VStack spacing={1} w="full">
            <Text fontSize="2xl" fontWeight="bold">{value}</Text>
            <Text fontSize="sm" fontWeight="medium">{title}</Text>
            {subtitle && (
              <Text fontSize="xs" color="gray.500" textAlign="center">{subtitle}</Text>
            )}
          </VStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const PopularServicesChart = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Most Used AWS Services</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {analyticsData.popular.services.map((service, index) => (
            <Box key={index} w="full">
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="medium">{service.name}</Text>
                <HStack>
                  <Text fontSize="sm" color="gray.600">{service.projects} projects</Text>
                  <Badge colorScheme="blue">{service.usage}%</Badge>
                </HStack>
              </HStack>
              <Progress 
                value={service.usage} 
                colorScheme="blue" 
                size="sm" 
                borderRadius="md"
              />
            </Box>
          ))}
        </VStack>
      </CardBody>
    </Card>
  );

  const ArchitectureTypesBreakdown = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Architecture Types</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {analyticsData.popular.architectures.map((arch, index) => (
            <Flex key={index} justify="space-between" align="center" w="full" p={3} borderRadius="md" bg="gray.50">
              <VStack align="start" spacing={0}>
                <Text fontWeight="medium">{arch.name}</Text>
                <Text fontSize="sm" color="gray.600">{arch.count} projects</Text>
              </VStack>
              <VStack align="end" spacing={0}>
                <Text fontSize="lg" fontWeight="bold">{arch.percentage}%</Text>
              </VStack>
            </Flex>
          ))}
        </VStack>
      </CardBody>
    </Card>
  );

  const RegionalDistribution = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Regional Distribution</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {analyticsData.popular.regions.map((region, index) => (
            <Box key={index} w="full">
              <HStack justify="space-between" mb={2}>
                <Text fontWeight="medium">{region.name}</Text>
                <HStack>
                  <Text fontSize="sm" color="gray.600">{region.projects} projects</Text>
                  <Badge variant="outline">{region.percentage}%</Badge>
                </HStack>
              </HStack>
              <Progress 
                value={region.percentage} 
                colorScheme="green" 
                size="sm" 
                borderRadius="md"
              />
            </Box>
          ))}
        </VStack>
      </CardBody>
    </Card>
  );

  const UsageMetrics = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">Platform Usage</Heading>
          <Select size="sm" value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)} w="auto">
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </Select>
        </HStack>
      </CardHeader>
      <CardBody>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
          <VStack spacing={4}>
            <Heading size="sm" color="gray.600">User Activity</Heading>
            <SimpleGrid columns={1} spacing={3} w="full">
              <HStack justify="space-between" p={3} borderRadius="md" bg="blue.50">
                <Text>Daily Active Users</Text>
                <Text fontWeight="bold">{analyticsData.usage.dailyActiveUsers}</Text>
              </HStack>
              <HStack justify="space-between" p={3} borderRadius="md" bg="green.50">
                <Text>Weekly Active Users</Text>
                <Text fontWeight="bold">{analyticsData.usage.weeklyActiveUsers}</Text>
              </HStack>
              <HStack justify="space-between" p={3} borderRadius="md" bg="purple.50">
                <Text>Monthly Active Users</Text>
                <Text fontWeight="bold">{analyticsData.usage.monthlyActiveUsers}</Text>
              </HStack>
            </SimpleGrid>
          </VStack>
          
          <VStack spacing={4}>
            <Heading size="sm" color="gray.600">Platform Activity</Heading>
            <SimpleGrid columns={1} spacing={3} w="full">
              <HStack justify="space-between" p={3} borderRadius="md" bg="orange.50">
                <Text>Projects Created</Text>
                <Text fontWeight="bold">{analyticsData.usage.projectsCreated}</Text>
              </HStack>
              <HStack justify="space-between" p={3} borderRadius="md" bg="teal.50">
                <Text>Deployments Executed</Text>
                <Text fontWeight="bold">{analyticsData.usage.deploymentsExecuted}</Text>
              </HStack>
              <HStack justify="space-between" p={3} borderRadius="md" bg="pink.50">
                <Text>Avg Session Duration</Text>
                <Text fontWeight="bold">{analyticsData.usage.averageSessionDuration}</Text>
              </HStack>
            </SimpleGrid>
          </VStack>
        </SimpleGrid>
      </CardBody>
    </Card>
  );

  const PerformanceMetrics = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Performance Metrics</Heading>
      </CardHeader>
      <CardBody>
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
          <VStack>
            <Text fontSize="2xl" fontWeight="bold" color="blue.500">
              {analyticsData.performance.averageLoadTime}
            </Text>
            <Text fontSize="sm" textAlign="center" color="gray.600">
              Avg Load Time
            </Text>
          </VStack>
          <VStack>
            <Text fontSize="2xl" fontWeight="bold" color="green.500">
              {analyticsData.performance.deploymentSuccess}%
            </Text>
            <Text fontSize="sm" textAlign="center" color="gray.600">
              Deployment Success
            </Text>
          </VStack>
          <VStack>
            <Text fontSize="2xl" fontWeight="bold" color="purple.500">
              {analyticsData.performance.userSatisfaction}/5
            </Text>
            <Text fontSize="sm" textAlign="center" color="gray.600">
              User Satisfaction
            </Text>
          </VStack>
          <VStack>
            <Text fontSize="2xl" fontWeight="bold" color="orange.500">
              {analyticsData.performance.systemUptime}%
            </Text>
            <Text fontSize="sm" textAlign="center" color="gray.600">
              System Uptime
            </Text>
          </VStack>
        </SimpleGrid>
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
              <Heading size="lg">Analytics Dashboard</Heading>
              <Text color="gray.600">
                Monitor platform usage, performance, and user behavior insights
              </Text>
            </VStack>
            <HStack>
              <Button leftIcon={<FaFilter />} size="sm" variant="outline">
                Filter
              </Button>
              <Button leftIcon={<FaDownload />} size="sm" colorScheme="blue">
                Export Report
              </Button>
            </HStack>
          </HStack>
          
          <InfoAlert />
        </Box>

        {/* Key Metrics */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
          <MetricCard
            icon={FaRocket}
            title="Total Projects"
            value={analyticsData.overview.totalProjects}
            change={15.3}
            subtitle="vs last month"
            color="blue"
          />
          <MetricCard
            icon={FaUsers}
            title="Active Users"
            value={analyticsData.overview.activeUsers}
            change={8.7}
            subtitle="this month"
            color="green"
          />
          <MetricCard
            icon={FaCloud}
            title="Deployments"
            value={analyticsData.overview.totalDeployments}
            change={23.1}
            subtitle="successful"
            color="purple"
          />
          <MetricCard
            icon={FaCheckCircle}
            title="Success Rate"
            value={`${analyticsData.overview.successRate}%`}
            change={2.4}
            subtitle="deployment success"
            color="orange"
          />
        </SimpleGrid>

        {/* Tabs Navigation */}
        <Tabs index={selectedTab} onChange={setSelectedTab}>
          <TabList>
            <Tab>Usage Overview</Tab>
            <Tab>Popular Services</Tab>
            <Tab>Performance</Tab>
          </TabList>

          <TabPanels>
            <TabPanel px={0}>
              <VStack spacing={6}>
                <UsageMetrics />
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} w="full">
                  <ArchitectureTypesBreakdown />
                  <RegionalDistribution />
                </SimpleGrid>
              </VStack>
            </TabPanel>

            <TabPanel px={0}>
              <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                <PopularServicesChart />
                <Card>
                  <CardHeader>
                    <Heading size="md">Service Adoption Trends</Heading>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={4}>
                      <Text color="gray.600" textAlign="center">
                        Service adoption trends and usage patterns will be displayed here.
                        This will include historical data, growth rates, and seasonal patterns.
                      </Text>
                      <Button variant="outline" size="sm">
                        View Detailed Trends
                      </Button>
                    </VStack>
                  </CardBody>
                </Card>
              </SimpleGrid>
            </TabPanel>

            <TabPanel px={0}>
              <VStack spacing={6}>
                <PerformanceMetrics />
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6} w="full">
                  <Card>
                    <CardHeader>
                      <Heading size="md">Response Time Trends</Heading>
                    </CardHeader>
                    <CardBody>
                      <VStack spacing={4}>
                        <Text color="gray.600" textAlign="center">
                          Response time analytics and performance trends will be displayed here.
                        </Text>
                        <Button variant="outline" size="sm">
                          View Performance Details
                        </Button>
                      </VStack>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardHeader>
                      <Heading size="md">Error Rate Analysis</Heading>
                    </CardHeader>
                    <CardBody>
                      <VStack spacing={4}>
                        <Text color="gray.600" textAlign="center">
                          Error rate tracking and failure analysis will be displayed here.
                        </Text>
                        <Button variant="outline" size="sm">
                          View Error Logs
                        </Button>
                      </VStack>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Future Features Preview */}
        <Card bg="gradient-to-r" bgGradient="linear(to-r, purple.50, blue.50)">
          <CardBody>
            <VStack spacing={4}>
              <Heading size="md" textAlign="center">Advanced Analytics Features Coming Soon</Heading>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <VStack>
                  <Icon as={FaChartLine} size="2em" color="purple.500" />
                  <Text fontWeight="bold">Predictive Analytics</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    AI-powered usage predictions and trend forecasting
                  </Text>
                </VStack>
                <VStack>
                  <Icon as={FaEye} size="2em" color="blue.500" />
                  <Text fontWeight="bold">Real-time Monitoring</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Live dashboards with real-time metrics and alerts
                  </Text>
                </VStack>
                <VStack>
                  <Icon as={FaDownload} size="2em" color="green.500" />
                  <Text fontWeight="bold">Custom Reports</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Automated reporting with custom metrics and scheduling
                  </Text>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

export default AnalyticsPage;