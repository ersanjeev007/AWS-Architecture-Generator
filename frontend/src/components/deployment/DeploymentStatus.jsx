import React from 'react';
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
  Divider,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
} from '@chakra-ui/react';
import {
  FaCheckCircle,
  FaTimesCircle,
  FaClock,
  FaRocket,
  FaTrash,
} from 'react-icons/fa';
import { SiTerraform, SiAmazonaws } from 'react-icons/si';

const DeploymentStatus = ({ deploymentStatus, awsAccounts }) => {
  if (!deploymentStatus) return null;

  const { is_deployed, current_deployment, deployment_history } = deploymentStatus;

  const formatDateTime = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const formatTimeAgo = (dateString) => {
    if (!dateString) return 'Never';
    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    return `${diffDays} days ago`;
  };

  const getAccountName = (accountId) => {
    const account = awsAccounts.find(acc => acc.id === accountId);
    return account ? account.account_name : 'Unknown Account';
  };

  const getTemplateIcon = (templateType) => {
    return templateType === 'terraform' ? SiTerraform : SiAmazonaws;
  };

  const getTemplateColor = (templateType) => {
    return templateType === 'terraform' ? 'purple' : 'orange';
  };

  return (
    <Card shadow="lg">
      <CardHeader>
        <HStack>
          <Icon 
            as={is_deployed ? FaCheckCircle : FaTimesCircle} 
            color={is_deployed ? "green.500" : "gray.400"} 
            boxSize={5} 
          />
          <Heading size="lg">
            Deployment Status
          </Heading>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* Current Status */}
          <Box>
            <HStack justify="space-between" align="center" mb={4}>
              <VStack align="start" spacing={1}>
                <Text fontSize="sm" color="gray.600" fontWeight="semibold">
                  Current Status
                </Text>
                <HStack>
                  <Badge 
                    colorScheme={is_deployed ? "green" : "gray"} 
                    variant="solid" 
                    px={3} 
                    py={1} 
                    borderRadius="full"
                  >
                    {is_deployed ? "DEPLOYED" : "NOT DEPLOYED"}
                  </Badge>
                  {is_deployed && (
                    <Badge 
                      colorScheme={getTemplateColor(current_deployment.template_type)}
                      variant="outline"
                      px={2} 
                      py={1} 
                      borderRadius="md"
                    >
                      <HStack spacing={1}>
                        <Icon as={getTemplateIcon(current_deployment.template_type)} size={12} />
                        <Text fontSize="xs" textTransform="uppercase">
                          {current_deployment.template_type}
                        </Text>
                      </HStack>
                    </Badge>
                  )}
                </HStack>
              </VStack>
            </HStack>

            {is_deployed && current_deployment && (
              <Box bg="green.50" p={4} borderRadius="md" borderLeft="4px" borderColor="green.400">
                <VStack align="start" spacing={2}>
                  <HStack>
                    <Icon as={FaRocket} color="green.600" size={14} />
                    <Text fontSize="sm" fontWeight="semibold" color="green.800">
                      Active Deployment
                    </Text>
                  </HStack>
                  
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
                    <VStack align="start" spacing={1}>
                      <Text fontSize="xs" color="green.600" fontWeight="semibold">
                        AWS Account
                      </Text>
                      <Text fontSize="sm" color="green.800">
                        {getAccountName(current_deployment.aws_account_id)}
                      </Text>
                    </VStack>
                    
                    {current_deployment.stack_name && (
                      <VStack align="start" spacing={1}>
                        <Text fontSize="xs" color="green.600" fontWeight="semibold">
                          Stack/Resource Name
                        </Text>
                        <Text fontSize="sm" color="green.800" fontFamily="mono">
                          {current_deployment.stack_name}
                        </Text>
                      </VStack>
                    )}
                    
                    <VStack align="start" spacing={1}>
                      <Text fontSize="xs" color="green.600" fontWeight="semibold">
                        Deployed At
                      </Text>
                      <Text fontSize="sm" color="green.800">
                        {formatDateTime(current_deployment.deployed_at)}
                      </Text>
                      <Text fontSize="xs" color="green.600">
                        {formatTimeAgo(current_deployment.deployed_at)}
                      </Text>
                    </VStack>
                    
                    <VStack align="start" spacing={1}>
                      <Text fontSize="xs" color="green.600" fontWeight="semibold">
                        Last Updated
                      </Text>
                      <Text fontSize="sm" color="green.800">
                        {formatDateTime(current_deployment.last_updated)}
                      </Text>
                      <Text fontSize="xs" color="green.600">
                        {formatTimeAgo(current_deployment.last_updated)}
                      </Text>
                    </VStack>
                  </SimpleGrid>
                </VStack>
              </Box>
            )}

            {!is_deployed && (
              <Box bg="gray.50" p={4} borderRadius="md" borderLeft="4px" borderColor="gray.400">
                <HStack>
                  <Icon as={FaClock} color="gray.500" size={14} />
                  <Text fontSize="sm" color="gray.600">
                    No active deployments. Use the "Deploy Infrastructure" button to deploy your architecture.
                  </Text>
                </HStack>
              </Box>
            )}
          </Box>

          <Divider />

          {/* Deployment History Summary */}
          <Box>
            <Text fontSize="sm" color="gray.600" fontWeight="semibold" mb={4}>
              Deployment History
            </Text>
            
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
              <Stat>
                <StatLabel fontSize="xs" color="gray.500">Total Deployments</StatLabel>
                <StatNumber fontSize="lg" color="blue.600">
                  {deployment_history.total_deployments}
                </StatNumber>
              </Stat>
              
              <Stat>
                <StatLabel fontSize="xs" color="gray.500">Terraform</StatLabel>
                <StatNumber fontSize="lg" color="purple.600">
                  {deployment_history.terraform_deployments}
                </StatNumber>
              </Stat>
              
              <Stat>
                <StatLabel fontSize="xs" color="gray.500">CloudFormation</StatLabel>
                <StatNumber fontSize="lg" color="orange.600">
                  {deployment_history.cloudformation_deployments}
                </StatNumber>
              </Stat>
              
              <Stat>
                <StatLabel fontSize="xs" color="gray.500">Destroyed</StatLabel>
                <StatNumber fontSize="lg" color="red.600">
                  {deployment_history.destroyed_deployments}
                </StatNumber>
              </Stat>
            </SimpleGrid>

            {deployment_history.failed_deployments > 0 && (
              <Box mt={4} p={3} bg="red.50" borderRadius="md" borderLeft="4px" borderColor="red.400">
                <HStack>
                  <Icon as={FaTimesCircle} color="red.500" size={14} />
                  <Text fontSize="sm" color="red.800">
                    {deployment_history.failed_deployments} deployment(s) failed. Check deployment logs for details.
                  </Text>
                </HStack>
              </Box>
            )}

            {deployment_history.last_activity && (
              <Text fontSize="xs" color="gray.500" mt={3}>
                Last activity: {formatTimeAgo(deployment_history.last_activity)}
              </Text>
            )}
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default DeploymentStatus;