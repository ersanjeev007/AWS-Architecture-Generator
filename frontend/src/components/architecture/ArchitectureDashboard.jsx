import React, { useEffect, useState } from 'react';
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
  Divider,
  Icon,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Select,
  Switch,
  useDisclosure,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { useParams, Link } from 'react-router-dom';
import { ReactFlow, Controls, Background } from 'reactflow';
import 'reactflow/dist/style.css';
import {
  FaDownload,
  FaCloud,
  FaShieldAlt,
  FaDollarSign,
  FaHome,
  FaFileCode,
  FaSave,
  FaSync,
  FaRocket,
  FaPlay,
  FaTrash,
  FaExclamationTriangle,
  FaChartLine,
  FaRobot,
  FaEye,
  FaCogs,
} from 'react-icons/fa';
import { SiTerraform, SiAmazonaws } from 'react-icons/si';
import { projectService } from '../../services/projectService';
import { awsAccountService } from '../../services/awsAccountService';
import DeploymentStatus from '../deployment/DeploymentStatus';
import DeploymentHistory from '../deployment/DeploymentHistory';
import EnhancedCostAnalysis from '../cost/EnhancedCostAnalysis';
import SecurityRecommendationsDashboard from '../security/SecurityRecommendationsDashboard';

const ArchitectureDashboard = () => {
  const { id } = useParams();
  const toast = useToast();
  const { 
    isOpen: isDeployModalOpen, 
    onOpen: onDeployModalOpen, 
    onClose: onDeployModalClose 
  } = useDisclosure();
  const { 
    isOpen: isDestroyModalOpen, 
    onOpen: onDestroyModalOpen, 
    onClose: onDestroyModalClose 
  } = useDisclosure();
  
  const [currentArchitecture, setCurrentArchitecture] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [regenerating, setRegenerating] = useState(false);
  const [awsAccounts, setAwsAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState('');
  const [selectedTemplateType, setSelectedTemplateType] = useState('terraform');
  const [deploying, setDeploying] = useState(false);
  const [isDryRun, setIsDryRun] = useState(true);
  const [deployments, setDeployments] = useState([]);
  const [selectedDeployment, setSelectedDeployment] = useState('');
  const [destroying, setDestroying] = useState(false);
  const [isDestroyDryRun, setIsDestroyDryRun] = useState(true);
  const [forceDestroy, setForceDestroy] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState(null);

  useEffect(() => {
    if (!id) {
      setError('No project ID provided');
      setLoading(false);
      return;
    }

    loadArchitecture();
    loadAWSAccounts();
    loadDeployments();
    loadDeploymentStatus();
  }, [id]);

  const loadArchitecture = async () => {
    try {
      setLoading(true);
      setError(null);

      const project = await projectService.getProject(id);

      if (!project) {
        throw new Error('Project not found');
      }

      if (project.architecture_data) {
        const architectureData = {
          id: project.id,
          project_name: project.project_name,
          services: project.architecture_data.services || {},
          security_features: project.architecture_data.security_features || [],
          estimated_cost: project.architecture_data.estimated_cost || 'N/A',
          cost_breakdown: project.architecture_data.cost_breakdown || [],
          diagram_data: project.architecture_data.diagram_data || { nodes: [], edges: [] },
          terraform_template: project.architecture_data.terraform_template || '',
          cloudformation_template: project.architecture_data.cloudformation_template || '',
          recommendations: project.architecture_data.recommendations || []
        };

        setCurrentArchitecture(architectureData);
      } else {
        throw new Error('No architecture data found in this project');
      }

    } catch (err) {
      console.error('Error loading architecture:', err);
      setError(err.message || 'Failed to load architecture');
    } finally {
      setLoading(false);
    }
  };

  const loadAWSAccounts = async () => {
    try {
      const accounts = await awsAccountService.listAccounts();
      setAwsAccounts(accounts);
      if (accounts.length > 0) {
        setSelectedAccount(accounts[0].id);
      }
    } catch (err) {
      console.error('Error loading AWS accounts:', err);
    }
  };

  const loadDeployments = async () => {
    try {
      const projectDeployments = await awsAccountService.listProjectDeployments(id);
      setDeployments(projectDeployments);
      
      // Find the most recent successful deployment for destroy
      const successfulDeployments = projectDeployments.filter(
        d => d.status === 'success' && !d.dry_run
      );
      if (successfulDeployments.length > 0) {
        setSelectedDeployment(successfulDeployments[0].id);
      }
    } catch (err) {
      console.error('Error loading deployments:', err);
    }
  };

  const loadDeploymentStatus = async () => {
    try {
      const status = await awsAccountService.getProjectDeploymentStatus(id);
      setDeploymentStatus(status);
    } catch (err) {
      console.error('Error loading deployment status:', err);
    }
  };

  const handleDeployInfrastructure = async () => {
    if (!selectedAccount) {
      toast({
        title: 'No AWS Account Selected',
        description: 'Please select an AWS account for deployment',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setDeploying(true);
      
      const deploymentRequest = {
        project_id: id,
        aws_account_id: selectedAccount,
        template_type: selectedTemplateType,
        dry_run: isDryRun
      };

      const result = await awsAccountService.deployInfrastructure(deploymentRequest);
      
      toast({
        title: isDryRun ? 'Dry Run Complete' : 'Deployment Started',
        description: result.message,
        status: result.status === 'success' ? 'success' : 'error',
        duration: isDryRun ? 5000 : 10000,
        isClosable: true,
      });

      if (result.output) {
        console.log('Deployment output:', result.output);
      }

      onDeployModalClose();
      
      // Reload deployments and status after successful deployment
      await loadDeployments();
      await loadDeploymentStatus();
      
    } catch (err) {
      toast({
        title: 'Deployment Failed',
        description: err.message,
        status: 'error',
        duration: 10000,
        isClosable: true,
      });
    } finally {
      setDeploying(false);
    }
  };

  const handleDestroyInfrastructure = async () => {
    if (!selectedDeployment) {
      toast({
        title: 'No Deployment Selected',
        description: 'Please select a deployment to destroy',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    const deployment = deployments.find(d => d.id === selectedDeployment);
    if (!deployment) {
      toast({
        title: 'Invalid Deployment',
        description: 'Selected deployment not found',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setDestroying(true);
      
      const destroyRequest = {
        deployment_id: selectedDeployment,
        aws_account_id: deployment.aws_account_id,
        template_type: deployment.template_type,
        dry_run: isDestroyDryRun,
        force_destroy: forceDestroy
      };

      const result = await awsAccountService.destroyInfrastructure(destroyRequest);
      
      toast({
        title: isDestroyDryRun ? 'Destroy Dry Run Complete' : 'Infrastructure Destroyed',
        description: result.message,
        status: result.status === 'success' ? 'success' : 'error',
        duration: isDestroyDryRun ? 5000 : 10000,
        isClosable: true,
      });

      if (result.output) {
        console.log('Destroy output:', result.output);
      }

      onDestroyModalClose();
      
      // Reload deployments and status after successful destroy
      await loadDeployments();
      await loadDeploymentStatus();
      
    } catch (err) {
      toast({
        title: 'Destroy Failed',
        description: err.message,
        status: 'error',
        duration: 10000,
        isClosable: true,
      });
    } finally {
      setDestroying(false);
    }
  };

  // Download Template Functions
  const downloadTerraformTemplate = () => {
    if (!currentArchitecture?.terraform_template) {
      toast({
        title: 'No Template Available',
        description: 'Terraform template not found for this architecture.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const blob = new Blob([currentArchitecture.terraform_template], { 
        type: 'text/plain' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${currentArchitecture.project_name.replace(/\s+/g, '-').toLowerCase()}-terraform.tf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Download Complete',
        description: 'Terraform template downloaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Download error:', error);
      toast({
        title: 'Download Failed',
        description: 'Failed to download Terraform template',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const downloadCloudFormationTemplate = () => {
    if (!currentArchitecture?.cloudformation_template) {
      toast({
        title: 'No Template Available',
        description: 'CloudFormation template not found for this architecture.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const blob = new Blob([currentArchitecture.cloudformation_template], { 
        type: 'text/yaml' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${currentArchitecture.project_name.replace(/\s+/g, '-').toLowerCase()}-cloudformation.yaml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: 'Download Complete',
        description: 'CloudFormation template downloaded successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Download error:', error);
      toast({
        title: 'Download Failed',
        description: 'Failed to download CloudFormation template',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const downloadAllTemplates = () => {
    downloadTerraformTemplate();
    // Add a small delay to prevent browser blocking multiple downloads
    setTimeout(() => {
      downloadCloudFormationTemplate();
    }, 500);
  };

  const handleRegenerateArchitecture = async () => {
    try {
      setRegenerating(true);
      
      // Call the regenerate endpoint
      const response = await fetch(`/api/v1/projects/${id}/regenerate-architecture`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to regenerate architecture');
      }

      // Reload the architecture data
      await loadArchitecture();
      
      toast({
        title: 'Architecture Regenerated',
        description: 'Your architecture has been successfully regenerated with the latest configurations.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

    } catch (error) {
      console.error('Error regenerating architecture:', error);
      toast({
        title: 'Regeneration Failed',
        description: 'Failed to regenerate architecture. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={6}>
          <Spinner size="xl" color="blue.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Loading Architecture
            </Heading>
            <Text color="gray.600">
              Retrieving your AWS architecture details...
            </Text>
          </VStack>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box maxW="2xl" mx="auto" py={20}>
        <Alert status="error" borderRadius="lg" p={6}>
          <AlertIcon boxSize={6} />
          <VStack align="start" spacing={3}>
            <AlertDescription fontSize="lg" fontWeight="medium">
              {error}
            </AlertDescription>
            <Text fontSize="sm" color="gray.600">
              Project ID: {id}
            </Text>
            <HStack spacing={3}>
              <Button as={Link} to="/" colorScheme="blue" leftIcon={<FaHome />}>
                Back to Projects
              </Button>
              <Button as={Link} to="/create" variant="outline" colorScheme="blue">
                Create New Architecture
              </Button>
            </HStack>
          </VStack>
        </Alert>
      </Box>
    );
  }

  if (!currentArchitecture) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={4}>
          <Text fontSize="lg" color="gray.600">
            No architecture found.
          </Text>
          <Button as={Link} to="/create" colorScheme="blue" leftIcon={<FaHome />}>
            Create New Architecture
          </Button>
        </VStack>
      </Box>
    );
  }

  const { nodes = [], edges = [] } = currentArchitecture.diagram_data || {};

  return (
    <Box maxW="7xl" mx="auto" p={6}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Card shadow="lg">
          <CardHeader>
            <HStack justify="space-between" align="start">
              <VStack align="start" spacing={2}>
                <Heading size="xl" color="gray.800">
                  {currentArchitecture.project_name}
                </Heading>
                <HStack>
                  <Badge colorScheme="green" px={3} py={1} borderRadius="full">
                    Architecture Ready ✓
                  </Badge>
                  <Text color="gray.500" fontSize="sm">
                    ID: {currentArchitecture.id}
                  </Text>
                </HStack>
              </VStack>
              <HStack spacing={3}>
                <Button
                  leftIcon={<FaSync />}
                  colorScheme="orange"
                  variant="outline"
                  onClick={handleRegenerateArchitecture}
                  isLoading={regenerating}
                  loadingText="Regenerating..."
                >
                  Regenerate
                </Button>
                <Button
                  as={Link}
                  to="/"
                  leftIcon={<FaHome />}
                  variant="outline"
                  colorScheme="blue"
                >
                  Back to Projects
                </Button>
                <Button
                  as={Link}
                  to="/create"
                  colorScheme="blue"
                  variant="solid"
                >
                  Create New Architecture
                </Button>
              </HStack>
            </HStack>
          </CardHeader>
        </Card>

        {/* Download Templates Section */}
        <Card shadow="lg">
          <CardHeader>
            <HStack>
              <Icon as={FaDownload} color="purple.500" boxSize={5} />
              <Heading size="lg">Infrastructure as Code Templates</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <Text mb={6} color="gray.600">
              Download your infrastructure templates to deploy this architecture in your AWS account.
            </Text>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
              {/* Terraform Download */}
              <Card variant="outline" borderColor="purple.200">
                <CardBody textAlign="center">
                  <VStack spacing={4}>
                    <Icon as={SiTerraform} color="purple.600" boxSize={10} />
                    <VStack spacing={1}>
                      <Heading size="sm" color="purple.600">Terraform</Heading>
                      <Text fontSize="sm" color="gray.500">Infrastructure as Code</Text>
                    </VStack>
                    <Button
                      colorScheme="purple"
                      leftIcon={<FaDownload />}
                      onClick={downloadTerraformTemplate}
                      isDisabled={!currentArchitecture?.terraform_template}
                      size="sm"
                      w="full"
                    >
                      Download .tf
                    </Button>
                  </VStack>
                </CardBody>
              </Card>

              {/* CloudFormation Download */}
              <Card variant="outline" borderColor="orange.200">
                <CardBody textAlign="center">
                  <VStack spacing={4}>
                    <Icon as={SiAmazonaws} color="orange.600" boxSize={10} />
                    <VStack spacing={1}>
                      <Heading size="sm" color="orange.600">CloudFormation</Heading>
                      <Text fontSize="sm" color="gray.500">AWS Native</Text>
                    </VStack>
                    <Button
                      colorScheme="orange"
                      leftIcon={<FaDownload />}
                      onClick={downloadCloudFormationTemplate}
                      isDisabled={!currentArchitecture?.cloudformation_template}
                      size="sm"
                      w="full"
                    >
                      Download .yaml
                    </Button>
                  </VStack>
                </CardBody>
              </Card>

              {/* Download All */}
              <Card variant="outline" borderColor="blue.200">
                <CardBody textAlign="center">
                  <VStack spacing={4}>
                    <Icon as={FaFileCode} color="blue.600" boxSize={10} />
                    <VStack spacing={1}>
                      <Heading size="sm" color="blue.600">All Templates</Heading>
                      <Text fontSize="sm" color="gray.500">Both formats</Text>
                    </VStack>
                    <Button
                      colorScheme="blue"
                      leftIcon={<FaDownload />}
                      onClick={downloadAllTemplates}
                      isDisabled={!currentArchitecture?.terraform_template && !currentArchitecture?.cloudformation_template}
                      size="sm"
                      w="full"
                    >
                      Download All
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
              
              {/* Deploy Infrastructure */}
              <Card variant="outline" borderColor="green.200" gridColumn={{ base: "1", md: "1 / -1" }}>
                <CardBody textAlign="center">
                  <VStack spacing={4}>
                    <Icon as={FaRocket} color="green.600" boxSize={10} />
                    <VStack spacing={1}>
                      <Heading size="sm" color="green.600">Deploy to AWS</Heading>
                      <Text fontSize="sm" color="gray.500">Deploy infrastructure to your AWS account</Text>
                    </VStack>
                    <HStack spacing={2} w={{ base: "full", md: "auto" }}>
                      <Button
                        colorScheme="green"
                        leftIcon={<FaPlay />}
                        onClick={onDeployModalOpen}
                        isDisabled={!currentArchitecture?.terraform_template && !currentArchitecture?.cloudformation_template}
                        size="sm"
                        flex={1}
                      >
                        Deploy Infrastructure
                      </Button>
                      <Button
                        colorScheme="red"
                        variant="outline"
                        leftIcon={<FaTrash />}
                        onClick={onDestroyModalOpen}
                        isDisabled={deployments.filter(d => d.status === 'success' && !d.dry_run).length === 0}
                        size="sm"
                        flex={1}
                      >
                        Destroy
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            </SimpleGrid>
            
            {/* Management Actions */}
            <HStack justify="center" spacing={4}>
              <Button
                as={Link}
                to="/aws-accounts"
                variant="outline"
                colorScheme="blue"
                leftIcon={<SiAmazonaws />}
              >
                Manage AWS Accounts
              </Button>
            </HStack>
          </CardBody>
        </Card>

        {/* Deployment Status Section */}
        <DeploymentStatus 
          deploymentStatus={deploymentStatus} 
          awsAccounts={awsAccounts}
        />

        {/* Main Content Grid */}
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Architecture Diagram */}
          <Card shadow="lg" gridColumn={{ base: "1", lg: "1 / -1" }}>
            <CardHeader>
              <HStack>
                <Icon as={FaCloud} color="blue.500" boxSize={5} />
                <Heading size="lg">Architecture Diagram</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <Box h="400px" border="1px" borderColor="gray.200" borderRadius="md">
                {nodes.length > 0 ? (
                  <ReactFlow
                    nodes={nodes}
                    edges={edges}
                    fitView
                    attributionPosition="bottom-left"
                  >
                    <Controls />
                    <Background variant="dots" gap={12} size={1} />
                  </ReactFlow>
                ) : (
                  <VStack justify="center" h="full" spacing={4}>
                    <Icon as={FaCloud} boxSize={12} color="gray.300" />
                    <Text color="gray.500">No diagram data available</Text>
                  </VStack>
                )}
              </Box>
            </CardBody>
          </Card>

          {/* AWS Services */}
          <Card shadow="lg">
            <CardHeader>
              <HStack>
                <Icon as={SiAmazonaws} color="orange.500" boxSize={5} />
                <Heading size="lg">AWS Services</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              {Object.keys(currentArchitecture.services).length > 0 ? (
                <VStack spacing={4} align="stretch">
                  {Object.entries(currentArchitecture.services).map(([category, service]) => (
                    <Box key={category}>
                      <HStack justify="space-between" align="start">
                        <VStack align="start" spacing={1}>
                          <Text fontWeight="semibold" textTransform="capitalize" color="gray.700">
                            {category.replace('_', ' ')}
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {service}
                          </Text>
                        </VStack>
                        <Badge colorScheme="orange" variant="subtle">
                          AWS
                        </Badge>
                      </HStack>
                      <Divider mt={3} />
                    </Box>
                  ))}
                </VStack>
              ) : (
                <Text color="gray.500" textAlign="center">No services data available</Text>
              )}
            </CardBody>
          </Card>

          {/* Security Features */}
          <Card shadow="lg">
            <CardHeader>
              <HStack>
                <Icon as={FaShieldAlt} color="green.500" boxSize={5} />
                <Heading size="lg">Security Features</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              {currentArchitecture.security_features.length > 0 ? (
                <SimpleGrid columns={1} spacing={2}>
                  {currentArchitecture.security_features.map((feature, index) => (
                    <Badge
                      key={index}
                      colorScheme="green"
                      variant="subtle"
                      p={2}
                      borderRadius="md"
                      fontSize="sm"
                    >
                      {feature}
                    </Badge>
                  ))}
                </SimpleGrid>
              ) : (
                <Text color="gray.500" textAlign="center">No security features data available</Text>
              )}
            </CardBody>
          </Card>

          {/* Enhanced Features Tabs */}
          <Card shadow="lg" gridColumn={{ base: "1", lg: "1 / -1" }}>
            <CardBody>
              <Tabs variant="enclosed" colorScheme="blue">
                <TabList>
                  <Tab>
                    <HStack>
                      <Icon as={FaDollarSign} />
                      <Text>Enhanced Cost Analysis</Text>
                    </HStack>
                  </Tab>
                  <Tab>
                    <HStack>
                      <Icon as={FaShieldAlt} />
                      <Text>AI Security Recommendations</Text>
                    </HStack>
                  </Tab>
                  <Tab>
                    <HStack>
                      <Icon as={FaEye} />
                      <Text>Basic Cost View</Text>
                    </HStack>
                  </Tab>
                </TabList>

                <TabPanels>
                  <TabPanel>
                    <EnhancedCostAnalysis
                      project={currentArchitecture}
                      questionnaire={currentArchitecture.questionnaire_responses}
                      services={currentArchitecture.services}
                      onCostUpdate={(costData) => {
                        console.log('Cost data updated:', costData);
                      }}
                    />
                  </TabPanel>
                  
                  <TabPanel>
                    <SecurityRecommendationsDashboard
                      project={currentArchitecture}
                      questionnaire={currentArchitecture.questionnaire_responses}
                      services={currentArchitecture.services}
                    />
                  </TabPanel>
                  
                  <TabPanel>
                    {/* Basic Cost Estimate - Original View */}
                    <VStack spacing={4}>
                      <Box textAlign="center" bg="green.50" p={6} borderRadius="lg" w="full">
                        <Text fontSize="3xl" fontWeight="bold" color="green.600">
                          {currentArchitecture.estimated_cost}
                        </Text>
                        <Text color="gray.600" fontSize="sm">
                          Estimated monthly cost (Basic calculation)
                        </Text>
                      </Box>
                      
                      {currentArchitecture.cost_breakdown && currentArchitecture.cost_breakdown.length > 0 && (
                        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} w="full">
                          {currentArchitecture.cost_breakdown.map((item, index) => (
                            <Box key={index} p={4} bg="gray.50" borderRadius="md">
                              <VStack align="start" spacing={1}>
                                <Text fontWeight="semibold" fontSize="sm">
                                  {item.service}
                                </Text>
                                <Text color="green.600" fontWeight="bold">
                                  {item.estimated_monthly_cost}
                                </Text>
                                <Text fontSize="xs" color="gray.600">
                                  {item.description}
                                </Text>
                              </VStack>
                            </Box>
                          ))}
                        </SimpleGrid>
                      )}
                      
                      <Alert status="info">
                        <AlertIcon />
                        <AlertDescription fontSize="sm">
                          This is the basic cost estimate. Switch to "Enhanced Cost Analysis" tab for real-time AWS pricing, 
                          optimization recommendations, and regional comparisons.
                        </AlertDescription>
                      </Alert>
                      
                      <Text fontSize="sm" color="gray.500" textAlign="center">
                        * Costs may vary based on actual usage and AWS pricing changes
                      </Text>
                    </VStack>
                  </TabPanel>
                </TabPanels>
              </Tabs>
            </CardBody>
          </Card>

          {/* Recommendations */}
          {currentArchitecture.recommendations && currentArchitecture.recommendations.length > 0 && (
            <Card shadow="lg" gridColumn={{ base: "1", lg: "1 / -1" }}>
              <CardHeader>
                <HStack>
                  <Icon as={FaFileCode} color="blue.500" boxSize={5} />
                  <Heading size="lg">Recommendations</Heading>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {currentArchitecture.recommendations.map((recommendation, index) => (
                    <Box key={index} p={4} bg="blue.50" borderRadius="md" borderLeft="4px" borderColor="blue.400">
                      <Text fontSize="sm" color="blue.800">
                        {recommendation}
                      </Text>
                    </Box>
                  ))}
                </VStack>
              </CardBody>
            </Card>
          )}
        </SimpleGrid>

        {/* Deployment History Section */}
        <DeploymentHistory 
          deployments={deployments}
          awsAccounts={awsAccounts}
        />

        {/* Deployment Modal */}
        <Modal isOpen={isDeployModalOpen} onClose={onDeployModalClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Deploy Infrastructure to AWS</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={6}>
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" fontWeight="semibold">
                      Infrastructure Deployment
                    </Text>
                    <Text fontSize="xs">
                      This will deploy your architecture to the selected AWS account. 
                      We recommend starting with a dry run to validate the deployment.
                    </Text>
                  </VStack>
                </Alert>

                <FormControl isRequired>
                  <FormLabel>AWS Account</FormLabel>
                  <Select
                    placeholder="Select AWS account"
                    value={selectedAccount}
                    onChange={(e) => setSelectedAccount(e.target.value)}
                  >
                    {awsAccounts.map((account) => (
                      <option key={account.id} value={account.id}>
                        {account.account_name} ({account.aws_region})
                        {!account.is_active && ' - Inactive'}
                      </option>
                    ))}
                  </Select>
                  {awsAccounts.length === 0 && (
                    <Text fontSize="sm" color="red.500" mt={1}>
                      No AWS accounts configured. 
                      <Link to="/aws-accounts" style={{ textDecoration: 'underline' }}>
                        Add an account first
                      </Link>
                    </Text>
                  )}
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Template Type</FormLabel>
                  <Select
                    value={selectedTemplateType}
                    onChange={(e) => setSelectedTemplateType(e.target.value)}
                  >
                    <option value="terraform">Terraform</option>
                    <option value="cloudformation">CloudFormation</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <FormLabel mb={0}>Deployment Mode</FormLabel>
                      <Text fontSize="xs" color="gray.600">
                        {isDryRun 
                          ? "Dry run mode - validate without deploying" 
                          : "Live deployment - creates actual AWS resources"
                        }
                      </Text>
                    </VStack>
                    <Switch
                      colorScheme="orange"
                      isChecked={!isDryRun}
                      onChange={(e) => setIsDryRun(!e.target.checked)}
                    />
                  </HStack>
                </FormControl>

                {!isDryRun && (
                  <Alert status="warning" borderRadius="md">
                    <AlertIcon />
                    <VStack align="start" spacing={1}>
                      <Text fontSize="sm" fontWeight="semibold">
                        Live Deployment Warning
                      </Text>
                      <Text fontSize="xs">
                        This will create actual AWS resources that may incur costs. 
                        Make sure you understand the estimated costs and have proper permissions.
                      </Text>
                    </VStack>
                  </Alert>
                )}
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onDeployModalClose}>
                Cancel
              </Button>
              <Button
                colorScheme={isDryRun ? "blue" : "green"}
                onClick={handleDeployInfrastructure}
                isLoading={deploying}
                loadingText={isDryRun ? "Validating..." : "Deploying..."}
                isDisabled={!selectedAccount || awsAccounts.length === 0}
                leftIcon={isDryRun ? <FaSync /> : <FaRocket />}
              >
                {isDryRun ? "Dry Run" : "Deploy Now"}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Destroy Infrastructure Modal */}
        <Modal isOpen={isDestroyModalOpen} onClose={onDestroyModalClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Destroy Infrastructure</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={6}>
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" fontWeight="semibold">
                      ⚠️ Dangerous Operation
                    </Text>
                    <Text fontSize="xs">
                      This will permanently destroy AWS resources created by your deployment. 
                      This action cannot be undone and may result in data loss.
                    </Text>
                  </VStack>
                </Alert>

                <FormControl isRequired>
                  <FormLabel>Select Deployment to Destroy</FormLabel>
                  <Select
                    placeholder="Select deployment"
                    value={selectedDeployment}
                    onChange={(e) => setSelectedDeployment(e.target.value)}
                  >
                    {deployments
                      .filter(d => d.status === 'success' && !d.dry_run)
                      .map((deployment) => (
                        <option key={deployment.id} value={deployment.id}>
                          {deployment.template_type} - {new Date(deployment.created_at).toLocaleDateString()} 
                          {deployment.stack_name && ` (${deployment.stack_name})`}
                        </option>
                      ))}
                  </Select>
                  {deployments.filter(d => d.status === 'success' && !d.dry_run).length === 0 && (
                    <Text fontSize="sm" color="red.500" mt={1}>
                      No successful deployments found to destroy
                    </Text>
                  )}
                </FormControl>

                <FormControl>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <FormLabel mb={0}>Destroy Mode</FormLabel>
                      <Text fontSize="xs" color="gray.600">
                        {isDestroyDryRun 
                          ? "Dry run mode - show what would be destroyed" 
                          : "Live destroy - permanently delete AWS resources"
                        }
                      </Text>
                    </VStack>
                    <Switch
                      colorScheme="red"
                      isChecked={!isDestroyDryRun}
                      onChange={(e) => setIsDestroyDryRun(!e.target.checked)}
                    />
                  </HStack>
                </FormControl>

                {!isDestroyDryRun && (
                  <FormControl>
                    <HStack justify="space-between">
                      <VStack align="start" spacing={1}>
                        <FormLabel mb={0}>Force Destroy</FormLabel>
                        <Text fontSize="xs" color="gray.600">
                          Try to destroy even if some resources fail to delete
                        </Text>
                      </VStack>
                      <Switch
                        colorScheme="orange"
                        isChecked={forceDestroy}
                        onChange={(e) => setForceDestroy(e.target.checked)}
                      />
                    </HStack>
                  </FormControl>
                )}

                {!isDestroyDryRun && (
                  <Alert status="warning" borderRadius="md">
                    <AlertIcon />
                    <VStack align="start" spacing={1}>
                      <Text fontSize="sm" fontWeight="semibold">
                        Final Warning
                      </Text>
                      <Text fontSize="xs">
                        You are about to permanently delete AWS resources. Make sure you have:
                        <br />• Backed up any important data
                        <br />• Confirmed this is the correct deployment
                        <br />• Proper permissions to delete resources
                      </Text>
                    </VStack>
                  </Alert>
                )}
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onDestroyModalClose}>
                Cancel
              </Button>
              <Button
                colorScheme={isDestroyDryRun ? "blue" : "red"}
                onClick={handleDestroyInfrastructure}
                isLoading={destroying}
                loadingText={isDestroyDryRun ? "Checking..." : "Destroying..."}
                isDisabled={!selectedDeployment}
                leftIcon={isDestroyDryRun ? <FaSync /> : <FaExclamationTriangle />}
              >
                {isDestroyDryRun ? "Dry Run Destroy" : "DESTROY NOW"}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default ArchitectureDashboard;