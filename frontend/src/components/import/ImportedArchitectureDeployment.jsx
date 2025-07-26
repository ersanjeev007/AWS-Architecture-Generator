import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Icon,
  useToast,
  Progress,
  Code,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  List,
  ListItem,
  ListIcon,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Spinner,
} from '@chakra-ui/react';
import {
  FaRocket,
  FaCheckCircle,
  FaExclamationTriangle,
  FaCloud,
  FaServer,
  FaDatabase,
  FaShieldAlt,
  FaDownload,
  FaEye,
  FaPlay,
  FaStop,
  FaSync,
} from 'react-icons/fa';

const ImportedArchitectureDeployment = ({ project, onClose }) => {
  const [deploymentState, setDeploymentState] = useState('ready'); // ready, deploying, deployed, error
  const [deploymentProgress, setDeploymentProgress] = useState(0);
  const [deploymentLogs, setDeploymentLogs] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState('terraform');
  const [deploymentResources, setDeploymentResources] = useState([]);
  const [error, setError] = useState(null);
  
  const toast = useToast();
  const { isOpen: isLogsOpen, onOpen: onLogsOpen, onClose: onLogsClose } = useDisclosure();

  const mockDeploymentSteps = [
    { name: 'Validating template', duration: 2000 },
    { name: 'Initializing provider', duration: 3000 },
    { name: 'Planning infrastructure', duration: 4000 },
    { name: 'Creating VPC and networking', duration: 5000 },
    { name: 'Deploying compute resources', duration: 6000 },
    { name: 'Setting up databases', duration: 4000 },
    { name: 'Configuring security groups', duration: 3000 },
    { name: 'Finalizing deployment', duration: 2000 }
  ];

  const handleStartDeployment = async () => {
    try {
      setDeploymentState('deploying');
      setDeploymentProgress(0);
      setDeploymentLogs([]);
      setError(null);

      // Simulate deployment process
      for (let i = 0; i < mockDeploymentSteps.length; i++) {
        const step = mockDeploymentSteps[i];
        
        // Add log entry
        setDeploymentLogs(prev => [...prev, {
          timestamp: new Date().toISOString(),
          level: 'info',
          message: `Starting: ${step.name}`
        }]);

        // Update progress
        setDeploymentProgress((i / mockDeploymentSteps.length) * 100);

        // Wait for step duration
        await new Promise(resolve => setTimeout(resolve, step.duration));

        // Complete step
        setDeploymentLogs(prev => [...prev, {
          timestamp: new Date().toISOString(),
          level: 'success',
          message: `Completed: ${step.name}`
        }]);

        // Add some resource creation logs
        if (i === 3) { // VPC creation
          setDeploymentResources(prev => [...prev, {
            type: 'VPC',
            name: 'imported-vpc',
            id: 'vpc-12345678',
            status: 'created'
          }]);
        }
        if (i === 4) { // EC2 creation
          setDeploymentResources(prev => [...prev, {
            type: 'EC2 Instance',
            name: 'web-server',
            id: 'i-1234567890abcdef0',
            status: 'created'
          }]);
        }
        if (i === 5) { // RDS creation
          setDeploymentResources(prev => [...prev, {
            type: 'RDS Instance',
            name: 'prod-database',
            id: 'prod-database-imported',
            status: 'created'
          }]);
        }
      }

      setDeploymentProgress(100);
      setDeploymentState('deployed');
      
      toast({
        title: 'Deployment Successful',
        description: 'Your imported infrastructure has been deployed successfully!',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (err) {
      setError(err.message);
      setDeploymentState('error');
      setDeploymentLogs(prev => [...prev, {
        timestamp: new Date().toISOString(),
        level: 'error',
        message: `Deployment failed: ${err.message}`
      }]);
      
      toast({
        title: 'Deployment Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleStopDeployment = () => {
    setDeploymentState('error');
    setDeploymentLogs(prev => [...prev, {
      timestamp: new Date().toISOString(),
      level: 'warning',
      message: 'Deployment stopped by user'
    }]);
    
    toast({
      title: 'Deployment Stopped',
      description: 'Deployment has been cancelled',
      status: 'warning',
      duration: 3000,
      isClosable: true,
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return 'blue';
      case 'deploying': return 'orange';
      case 'deployed': return 'green';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'ready': return FaCloud;
      case 'deploying': return FaSync;
      case 'deployed': return FaCheckCircle;
      case 'error': return FaExclamationTriangle;
      default: return FaCloud;
    }
  };

  const renderDeploymentStatus = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <HStack>
            <Icon as={getStatusIcon(deploymentState)} color={`${getStatusColor(deploymentState)}.500`} />
            <Heading size="md">Deployment Status</Heading>
          </HStack>
          <Badge colorScheme={getStatusColor(deploymentState)} variant="solid">
            {deploymentState.toUpperCase()}
          </Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {deploymentState === 'deploying' && (
            <Box w="full">
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm">Progress</Text>
                <Text fontSize="sm">{Math.round(deploymentProgress)}%</Text>
              </HStack>
              <Progress value={deploymentProgress} colorScheme="blue" />
            </Box>
          )}

          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} w="full">
            <VStack>
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                {deploymentResources.length}
              </Text>
              <Text fontSize="sm" textAlign="center">Resources Created</Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                {selectedTemplate === 'terraform' ? 'Terraform' : 'CloudFormation'}
              </Text>
              <Text fontSize="sm" textAlign="center">Template Type</Text>
            </VStack>
            <VStack>
              <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                {project?.region || 'us-east-1'}
              </Text>
              <Text fontSize="sm" textAlign="center">AWS Region</Text>
            </VStack>
          </SimpleGrid>

          <HStack spacing={4} w="full">
            {deploymentState === 'ready' && (
              <Button
                leftIcon={<FaRocket />}
                colorScheme="green"
                onClick={handleStartDeployment}
                size="lg"
                w="full"
              >
                Deploy Infrastructure
              </Button>
            )}
            
            {deploymentState === 'deploying' && (
              <Button
                leftIcon={<FaStop />}
                colorScheme="red"
                variant="outline"
                onClick={handleStopDeployment}
                size="lg"
                w="full"
              >
                Stop Deployment
              </Button>
            )}
            
            {(deploymentState === 'deployed' || deploymentState === 'error') && (
              <Button
                leftIcon={<FaSync />}
                colorScheme="blue"
                variant="outline"
                onClick={() => {
                  setDeploymentState('ready');
                  setDeploymentProgress(0);
                  setDeploymentResources([]);
                  setDeploymentLogs([]);
                  setError(null);
                }}
                size="lg"
                w="full"
              >
                Deploy Again
              </Button>
            )}

            <Button
              leftIcon={<FaEye />}
              variant="outline"
              onClick={onLogsOpen}
              size="lg"
            >
              View Logs
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const renderResourcesList = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Created Resources</Heading>
      </CardHeader>
      <CardBody>
        {deploymentResources.length === 0 ? (
          <Text color="gray.500" textAlign="center">
            No resources created yet. Start deployment to begin.
          </Text>
        ) : (
          <List spacing={3}>
            {deploymentResources.map((resource, index) => (
              <ListItem key={index}>
                <HStack justify="space-between">
                  <HStack>
                    <ListIcon
                      as={resource.type.includes('VPC') ? FaCloud :
                          resource.type.includes('EC2') ? FaServer :
                          resource.type.includes('RDS') ? FaDatabase : FaShieldAlt}
                      color="green.500"
                    />
                    <VStack align="start" spacing={0}>
                      <Text fontWeight="medium">{resource.name}</Text>
                      <Text fontSize="sm" color="gray.600">{resource.type}</Text>
                    </VStack>
                  </HStack>
                  <VStack align="end" spacing={0}>
                    <Badge colorScheme="green">{resource.status}</Badge>
                    <Text fontSize="xs" color="gray.500">{resource.id}</Text>
                  </VStack>
                </HStack>
              </ListItem>
            ))}
          </List>
        )}
      </CardBody>
    </Card>
  );

  const renderPreDeploymentChecks = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Pre-deployment Checks</Heading>
      </CardHeader>
      <CardBody>
        <List spacing={3}>
          <ListItem>
            <HStack>
              <ListIcon as={FaCheckCircle} color="green.500" />
              <Text>Template validation passed</Text>
            </HStack>
          </ListItem>
          <ListItem>
            <HStack>
              <ListIcon as={FaCheckCircle} color="green.500" />
              <Text>AWS credentials configured</Text>
            </HStack>
          </ListItem>
          <ListItem>
            <HStack>
              <ListIcon as={FaCheckCircle} color="green.500" />
              <Text>Required permissions available</Text>
            </HStack>
          </ListItem>
          <ListItem>
            <HStack>
              <ListIcon as={FaCheckCircle} color="green.500" />
              <Text>Target region accessible</Text>
            </HStack>
          </ListItem>
          <ListItem>
            <HStack>
              <ListIcon as={FaExclamationTriangle} color="orange.500" />
              <Text>Some resources may incur costs</Text>
            </HStack>
          </ListItem>
        </List>
      </CardBody>
    </Card>
  );

  return (
    <VStack spacing={6} w="full">
      <Alert status="info" borderRadius="md">
        <AlertIcon />
        <Box>
          <AlertTitle>Deploy Imported Infrastructure</AlertTitle>
          <AlertDescription>
            Deploy your imported AWS infrastructure using {selectedTemplate}. 
            This will create resources in your AWS account based on the scanned configuration.
          </AlertDescription>
        </Box>
      </Alert>

      <Tabs w="full">
        <TabList>
          <Tab>Deployment</Tab>
          <Tab>Resources</Tab>
          <Tab>Configuration</Tab>
        </TabList>

        <TabPanels>
          <TabPanel px={0}>
            <VStack spacing={6}>
              {renderDeploymentStatus()}
              {deploymentState === 'ready' && renderPreDeploymentChecks()}
            </VStack>
          </TabPanel>

          <TabPanel px={0}>
            {renderResourcesList()}
          </TabPanel>

          <TabPanel px={0}>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
              <Card>
                <CardHeader>
                  <Heading size="md">Template Configuration</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4} align="start">
                    <HStack>
                      <Text fontWeight="medium">Template Type:</Text>
                      <Badge colorScheme="blue">{selectedTemplate}</Badge>
                    </HStack>
                    <HStack>
                      <Text fontWeight="medium">Region:</Text>
                      <Text>{project?.region || 'us-east-1'}</Text>
                    </HStack>
                    <HStack>
                      <Text fontWeight="medium">Resources:</Text>
                      <Text>{project?.discoveredResourceCount || 'N/A'}</Text>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>

              <Card>
                <CardHeader>
                  <Heading size="md">Security Considerations</Heading>
                </CardHeader>
                <CardBody>
                  <List spacing={2}>
                    <ListItem fontSize="sm">
                      <ListIcon as={FaShieldAlt} color="green.500" />
                      Security groups will be recreated with same rules
                    </ListItem>
                    <ListItem fontSize="sm">
                      <ListIcon as={FaShieldAlt} color="green.500" />
                      IAM roles and policies will be applied
                    </ListItem>
                    <ListItem fontSize="sm">
                      <ListIcon as={FaExclamationTriangle} color="orange.500" />
                      Review security configurations before deployment
                    </ListItem>
                  </List>
                </CardBody>
              </Card>
            </SimpleGrid>
          </TabPanel>
        </TabPanels>
      </Tabs>

      {/* Deployment Logs Modal */}
      <Modal isOpen={isLogsOpen} onClose={onLogsClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Deployment Logs</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Box maxH="400px" overflowY="auto">
              {deploymentLogs.length === 0 ? (
                <Text color="gray.500" textAlign="center">No logs available</Text>
              ) : (
                <List spacing={2}>
                  {deploymentLogs.map((log, index) => (
                    <ListItem key={index} fontSize="sm">
                      <HStack spacing={2}>
                        <Badge
                          colorScheme={
                            log.level === 'error' ? 'red' :
                            log.level === 'warning' ? 'orange' :
                            log.level === 'success' ? 'green' : 'blue'
                          }
                          size="sm"
                        >
                          {log.level}
                        </Badge>
                        <Text fontSize="xs" color="gray.500">
                          {new Date(log.timestamp).toLocaleTimeString()}
                        </Text>
                        <Text>{log.message}</Text>
                      </HStack>
                    </ListItem>
                  ))}
                </List>
              )}
            </Box>
          </ModalBody>
          <ModalFooter>
            <Button onClick={onLogsClose}>Close</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default ImportedArchitectureDeployment;