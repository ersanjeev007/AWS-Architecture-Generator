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
} from 'react-icons/fa';
import { SiTerraform, SiAmazonaws } from 'react-icons/si';
import { projectService } from '../../services/projectService';

const ArchitectureDashboard = () => {
  const { id } = useParams();
  const toast = useToast();
  
  const [currentArchitecture, setCurrentArchitecture] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    if (!id) {
      setError('No project ID provided');
      setLoading(false);
      return;
    }

    loadArchitecture();
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

          {/* Cost Estimate */}
          <Card shadow="lg" gridColumn={{ base: "1", lg: "1 / -1" }}>
            <CardHeader>
              <HStack>
                <Icon as={FaDollarSign} color="green.500" boxSize={5} />
                <Heading size="lg">Cost Estimate</Heading>
              </HStack>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <Box textAlign="center" bg="green.50" p={6} borderRadius="lg" w="full">
                  <Text fontSize="3xl" fontWeight="bold" color="green.600">
                    {currentArchitecture.estimated_cost}
                  </Text>
                  <Text color="gray.600" fontSize="sm">
                    Estimated monthly cost
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
                
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  * Costs may vary based on actual usage and AWS pricing changes
                </Text>
              </VStack>
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
      </VStack>
    </Box>
  );
};

export default ArchitectureDashboard;