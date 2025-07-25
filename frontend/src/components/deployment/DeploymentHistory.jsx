import React, { useState } from 'react';
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  VStack,
  HStack,
  Heading,
  Text,
  Badge,
  Icon,
  Button,
  Collapse,
  Code,
  Divider,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  SimpleGrid,
} from '@chakra-ui/react';
import {
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaRocket,
  FaTrash,
  FaEye,
  FaChevronDown,
  FaChevronUp,
} from 'react-icons/fa';
import { SiTerraform, SiAmazonaws } from 'react-icons/si';

const DeploymentHistory = ({ deployments, awsAccounts }) => {
  const [showAll, setShowAll] = useState(false);
  const [expandedOutput, setExpandedOutput] = useState({});

  if (!deployments || deployments.length === 0) {
    return (
      <Card shadow="lg">
        <CardHeader>
          <HStack>
            <Icon as={FaClock} color="gray.400" boxSize={5} />
            <Heading size="lg">Deployment History</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <Box textAlign="center" py={8}>
            <Icon as={FaClock} boxSize={12} color="gray.300" mb={4} />
            <Text color="gray.500">No deployment history available</Text>
          </Box>
        </CardBody>
      </Card>
    );
  }

  const displayedDeployments = showAll ? deployments : deployments.slice(0, 5);

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const getAccountName = (accountId) => {
    const account = awsAccounts.find(acc => acc.id === accountId);
    return account ? account.account_name : 'Unknown Account';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success': return FaCheckCircle;
      case 'failed': return FaTimesCircle;
      case 'destroyed': return FaTrash;
      case 'running': return FaClock;
      default: return FaClock;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'green';
      case 'failed': return 'red';
      case 'destroyed': return 'orange';
      case 'running': return 'blue';
      default: return 'gray';
    }
  };

  const getTemplateIcon = (templateType) => {
    return templateType === 'terraform' ? SiTerraform : SiAmazonaws;
  };

  const getTemplateColor = (templateType) => {
    return templateType === 'terraform' ? 'purple' : 'orange';
  };

  const toggleOutput = (deploymentId) => {
    setExpandedOutput(prev => ({
      ...prev,
      [deploymentId]: !prev[deploymentId]
    }));
  };

  const getOperationType = (deployment) => {
    // Check if this is a destroy operation based on status or other indicators
    if (deployment.status === 'destroyed') return 'DESTROY';
    
    // If dry_run is true, it's a validation
    if (deployment.dry_run) return 'DRY RUN';
    
    // Otherwise it's a deployment
    return 'DEPLOY';
  };

  return (
    <Card shadow="lg">
      <CardHeader>
        <HStack justify="space-between">
          <HStack>
            <Icon as={FaClock} color="blue.500" boxSize={5} />
            <Heading size="lg">Deployment History</Heading>
            <Badge colorScheme="blue" variant="subtle">
              {deployments.length} operations
            </Badge>
          </HStack>
          {deployments.length > 5 && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowAll(!showAll)}
              rightIcon={showAll ? <FaChevronUp /> : <FaChevronDown />}
            >
              {showAll ? 'Show Less' : `Show All (${deployments.length})`}
            </Button>
          )}
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={4} align="stretch">
          {displayedDeployments.map((deployment, index) => (
            <Card key={deployment.id} variant="outline" size="sm">
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {/* Header Row */}
                  <HStack justify="space-between" align="start">
                    <HStack spacing={3}>
                      <Icon 
                        as={getStatusIcon(deployment.status)} 
                        color={`${getStatusColor(deployment.status)}.500`} 
                        boxSize={4} 
                      />
                      <VStack align="start" spacing={1}>
                        <HStack>
                          <Badge 
                            colorScheme={getStatusColor(deployment.status)}
                            variant="solid"
                            size="sm"
                          >
                            {getOperationType(deployment)}
                          </Badge>
                          <Badge 
                            colorScheme={getTemplateColor(deployment.template_type)}
                            variant="outline"
                            size="sm"
                          >
                            <HStack spacing={1}>
                              <Icon as={getTemplateIcon(deployment.template_type)} size={10} />
                              <Text fontSize="xs" textTransform="uppercase">
                                {deployment.template_type}
                              </Text>
                            </HStack>
                          </Badge>
                        </HStack>
                        <Text fontSize="sm" fontWeight="semibold" color="gray.800">
                          {deployment.status === 'destroyed' ? 'Infrastructure Destroyed' :
                           deployment.dry_run ? 'Validation Run' : 'Infrastructure Deployed'}
                        </Text>
                      </VStack>
                    </HStack>
                    
                    <VStack align="end" spacing={1}>
                      <Text fontSize="xs" color="gray.500">
                        {formatDateTime(deployment.created_at)}
                      </Text>
                      {deployment.updated_at !== deployment.created_at && (
                        <Text fontSize="xs" color="gray.400">
                          Updated: {formatDateTime(deployment.updated_at)}
                        </Text>
                      )}
                    </VStack>
                  </HStack>

                  {/* Details Grid */}
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <VStack align="start" spacing={1}>
                      <Text fontSize="xs" color="gray.500" fontWeight="semibold">
                        AWS Account
                      </Text>
                      <Text fontSize="sm">
                        {getAccountName(deployment.aws_account_id)}
                      </Text>
                    </VStack>
                    
                    {deployment.stack_name && (
                      <VStack align="start" spacing={1}>
                        <Text fontSize="xs" color="gray.500" fontWeight="semibold">
                          Stack/Resource Name
                        </Text>
                        <Text fontSize="sm" fontFamily="mono" bg="gray.100" px={2} py={1} borderRadius="md">
                          {deployment.stack_name}
                        </Text>
                      </VStack>
                    )}
                  </SimpleGrid>

                  {/* Output/Error Section */}
                  {(deployment.output || deployment.error) && (
                    <>
                      <Divider />
                      <VStack align="stretch" spacing={2}>
                        <Button
                          size="sm"
                          variant="ghost"
                          leftIcon={<FaEye />}
                          onClick={() => toggleOutput(deployment.id)}
                          alignSelf="start"
                        >
                          {expandedOutput[deployment.id] ? 'Hide' : 'Show'} {deployment.error ? 'Error' : 'Output'}
                        </Button>
                        
                        <Collapse in={expandedOutput[deployment.id]}>
                          <Box 
                            bg={deployment.error ? "red.50" : "gray.50"} 
                            p={3} 
                            borderRadius="md"
                            borderLeft="4px"
                            borderColor={deployment.error ? "red.400" : "blue.400"}
                          >
                            <Text fontSize="xs" color="gray.500" fontWeight="semibold" mb={2}>
                              {deployment.error ? 'Error Details:' : 'Output:'}
                            </Text>
                            <Code 
                              fontSize="xs" 
                              whiteSpace="pre-wrap" 
                              bg="transparent"
                              color={deployment.error ? "red.800" : "gray.800"}
                              maxH="200px"
                              overflowY="auto"
                            >
                              {deployment.error || deployment.output}
                            </Code>
                          </Box>
                        </Collapse>
                      </VStack>
                    </>
                  )}
                </VStack>
              </CardBody>
            </Card>
          ))}
          
          {deployments.length === 0 && (
            <Box textAlign="center" py={8}>
              <Icon as={FaClock} boxSize={12} color="gray.300" mb={4} />
              <Text color="gray.500">No deployment history available</Text>
            </Box>
          )}
        </VStack>
      </CardBody>
    </Card>
  );
};

export default DeploymentHistory;