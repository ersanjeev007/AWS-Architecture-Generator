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
  Icon,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  Container,
  Flex,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
} from '@chakra-ui/react';
import { Link, useNavigate } from 'react-router-dom';
import {
  FaPlus,
  FaCloud,
  FaDollarSign,
  FaEye,
  FaTrash,
  FaEllipsisV,
  FaServer,
  FaDatabase,
  FaShieldAlt,
  FaDownload,
  FaChevronDown,
} from 'react-icons/fa';
import { SiAmazonaws } from 'react-icons/si';
import { projectService } from '../../services/projectService';
import { extractErrorMessage } from '../../utils/errorUtils';
import InfrastructureImportWizard from '../import/InfrastructureImportWizard';

const ProjectsHomePage = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(null);
  const toast = useToast();
  const navigate = useNavigate();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isImportOpen, onOpen: onImportOpen, onClose: onImportClose } = useDisclosure();
  const [projectToDelete, setProjectToDelete] = useState(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const projectsData = await projectService.listProjects();
      setProjects(projectsData);
    } catch (err) {
      console.error('Error loading projects:', err);
      setError(extractErrorMessage(err, 'Failed to load projects'));
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (projectId) => {
    try {
      setDeleteLoading(projectId);
      await projectService.deleteProject(projectId);
      
      // Remove from local state
      setProjects(projects.filter(p => p.id !== projectId));
      
      toast({
        title: 'Project Deleted',
        description: 'Project deleted successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
      console.error('Error deleting project:', err);
      toast({
        title: 'Delete Failed',
        description: err.message || 'Failed to delete project. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setDeleteLoading(null);
      onClose();
      setProjectToDelete(null);
    }
  };

  const openDeleteModal = (project) => {
    setProjectToDelete(project);
    onOpen();
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getServiceCount = (services) => {
    return Object.keys(services || {}).length;
  };

  const getSecurityCount = (securityFeatures) => {
    return Array.isArray(securityFeatures) ? securityFeatures.length : 0;
  };

  if (loading) {
    return (
      <Container maxW="7xl" py={20}>
        <VStack spacing={6}>
          <Spinner size="xl" color="awsBlue.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Loading Projects
            </Heading>
            <Text color="gray.600">
              Retrieving your saved AWS architectures...
            </Text>
          </VStack>
        </VStack>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxW="2xl" py={20}>
        <Alert status="error" borderRadius="lg" p={6}>
          <AlertIcon boxSize={6} />
          <VStack align="start" spacing={3}>
            <AlertDescription fontSize="lg" fontWeight="medium">
              {typeof error === 'string' ? error : extractErrorMessage(error, 'Failed to load projects')}
            </AlertDescription>
            <Button onClick={loadProjects} colorScheme="awsBlue">
              Try Again
            </Button>
          </VStack>
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Flex justify="space-between" align="center">
          <VStack align="start" spacing={2}>
            <Heading size="2xl" color="gray.800">
              AWS Architecture Projects
            </Heading>
            <Text color="gray.600" fontSize="lg">
              Manage and view your saved cloud architectures
            </Text>
          </VStack>
          <Menu>
            <MenuButton
              as={Button}
              rightIcon={<FaChevronDown />}
              colorScheme="awsBlue"
              size="lg"
            >
              Create Architecture
            </MenuButton>
            <MenuList>
              <MenuItem
                icon={<FaPlus />}
                as={Link}
                to="/create"
              >
                Create New Architecture
              </MenuItem>
              <MenuItem
                icon={<FaDownload />}
                onClick={onImportOpen}
              >
                Import from AWS Account
              </MenuItem>
            </MenuList>
          </Menu>
        </Flex>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <Card shadow="lg" textAlign="center" py={20}>
            <CardBody>
              <VStack spacing={6}>
                <Icon as={FaCloud} boxSize={16} color="gray.300" />
                <VStack spacing={3}>
                  <Heading size="lg" color="gray.600">
                    No Projects Yet
                  </Heading>
                  <Text color="gray.500" maxW="md">
                    Create your first AWS architecture to get started. Our intelligent generator will help you design the perfect cloud solution.
                  </Text>
                </VStack>
                <HStack spacing={4}>
                  <Button
                    as={Link}
                    to="/create"
                    leftIcon={<FaPlus />}
                    colorScheme="awsBlue"
                    size="lg"
                  >
                    Create New Architecture
                  </Button>
                  <Button
                    leftIcon={<FaDownload />}
                    variant="outline"
                    colorScheme="awsBlue"
                    size="lg"
                    onClick={onImportOpen}
                  >
                    Import from AWS
                  </Button>
                </HStack>
              </VStack>
            </CardBody>
          </Card>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {projects.map((project) => (
              <Card key={project.id} shadow="lg" _hover={{ shadow: 'xl' }} transition="all 0.2s">
                <CardHeader pb={3}>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                      <Heading size="md" color="gray.800" noOfLines={1}>
                        {project.project_name}
                      </Heading>
                      <Text fontSize="sm" color="gray.500">
                        {formatDate(project.created_at)}
                      </Text>
                    </VStack>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        aria-label="More options"
                        icon={<FaEllipsisV />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem
                          icon={<FaEye />}
                          as={Link}
                          to={`/project/${project.id}`}
                        >
                          View Architecture
                        </MenuItem>
                        <MenuItem
                          icon={<FaTrash />}
                          color="red.500"
                          onClick={() => openDeleteModal(project)}
                        >
                          Delete Project
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </CardHeader>
                
                <CardBody pt={0}>
                  <VStack spacing={4} align="stretch">
                    {/* Description */}
                    {project.description && (
                      <Text fontSize="sm" color="gray.600" noOfLines={2}>
                        {project.description}
                      </Text>
                    )}

                    {/* Quick Stats */}
                    <SimpleGrid columns={3} spacing={3}>
                      <VStack spacing={1}>
                        <Icon as={SiAmazonaws} color="aws.500" boxSize={4} />
                        <Text fontSize="xs" color="gray.500" textAlign="center">
                          {getServiceCount(project.architecture_data?.services)} Services
                        </Text>
                      </VStack>
                      <VStack spacing={1}>
                        <Icon as={FaShieldAlt} color="green.500" boxSize={4} />
                        <Text fontSize="xs" color="gray.500" textAlign="center">
                          {getSecurityCount(project.architecture_data?.security_features)} Security
                        </Text>
                      </VStack>
                      <VStack spacing={1}>
                        <Icon as={FaDollarSign} color="green.500" boxSize={4} />
                        <Text fontSize="xs" color="gray.500" textAlign="center">
                          {project.architecture_data?.estimated_cost || 'N/A'}
                        </Text>
                      </VStack>
                    </SimpleGrid>

                    {/* Main Services Preview */}
                    {project.architecture_data?.services && (
                      <VStack spacing={2} align="stretch">
                        <Text fontSize="sm" fontWeight="semibold" color="gray.700">
                          Key Services:
                        </Text>
                        <VStack spacing={1} align="stretch">
                          {Object.entries(project.architecture_data.services)
                            .slice(0, 3)
                            .map(([category, service]) => (
                              <HStack key={category} justify="space-between">
                                <Text fontSize="xs" color="gray.600" textTransform="capitalize">
                                  {category.replace('_', ' ')}:
                                </Text>
                                <Badge colorScheme="awsBlue" variant="subtle" fontSize="xs">
                                  {service.split(' ')[1] || service} {/* Show just service name */}
                                </Badge>
                              </HStack>
                            ))}
                          {Object.keys(project.architecture_data.services).length > 3 && (
                            <Text fontSize="xs" color="gray.500" textAlign="center">
                              +{Object.keys(project.architecture_data.services).length - 3} more
                            </Text>
                          )}
                        </VStack>
                      </VStack>
                    )}

                    {/* View Button */}
                    <Button
                      as={Link}
                      to={`/project/${project.id}`}
                      leftIcon={<FaEye />}
                      colorScheme="awsBlue"
                      variant="outline"
                      size="sm"
                      w="full"
                    >
                      View Architecture
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}

        {/* Delete Confirmation Modal */}
        <Modal isOpen={isOpen} onClose={onClose} isCentered>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Delete Project</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Text>
                Are you sure you want to delete "{projectToDelete?.project_name}"? 
                This action cannot be undone.
              </Text>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button
                colorScheme="red"
                onClick={() => handleDeleteProject(projectToDelete?.id)}
                isLoading={deleteLoading === projectToDelete?.id}
                loadingText="Deleting..."
              >
                Delete
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Infrastructure Import Modal */}
        <Modal isOpen={isImportOpen} onClose={onImportClose} size="full">
          <ModalOverlay />
          <ModalContent>
            <ModalCloseButton />
            <ModalBody p={0}>
              <InfrastructureImportWizard onClose={onImportClose} />
            </ModalBody>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default ProjectsHomePage;