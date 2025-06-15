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
  Badge,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
} from '@chakra-ui/react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { FaEdit, FaEye, FaHome, FaTrash } from 'react-icons/fa';
import { projectService } from '../../services/projectService';
import ArchitectureDashboard from '../architecture/ArchitectureDashboard';

const ProjectView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [project, setProject] = useState(null);
  const [architecture, setArchitecture] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const [projectData, architectureData] = await Promise.all([
        projectService.getProject(id),
        projectService.getProjectArchitecture(id)
      ]);
      setProject(projectData);
      setArchitecture(architectureData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm(`Are you sure you want to delete "${project.project_name}"?`)) {
      try {
        await projectService.deleteProject(id);
        toast({
          title: 'Project Deleted',
          description: 'Project has been deleted successfully.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/projects');
      } catch (err) {
        toast({
          title: 'Delete Failed',
          description: err.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={6}>
          <Spinner size="xl" color="awsBlue.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Loading Project
            </Heading>
            <Text color="gray.600">
              Retrieving your saved project details...
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
            <HStack spacing={3}>
              <Button as={Link} to="/projects" colorScheme="awsBlue" leftIcon={<FaEye />}>
                View All Projects
              </Button>
              <Button as={Link} to="/" variant="outline" leftIcon={<FaHome />}>
                Return Home
              </Button>
            </HStack>
          </VStack>
        </Alert>
      </Box>
    );
  }

  if (!project || !architecture) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={4}>
          <Text fontSize="lg" color="gray.600">
            Project not found.
          </Text>
          <HStack spacing={3}>
            <Button as={Link} to="/projects" colorScheme="awsBlue" leftIcon={<FaEye />}>
              View All Projects
            </Button>
            <Button as={Link} to="/" variant="outline" leftIcon={<FaHome />}>
              Return Home
            </Button>
          </HStack>
        </VStack>
      </Box>
    );
  }

  return (
    <Box>
      <VStack spacing={8} align="stretch">
        {/* Project Header */}
        <Card shadow="lg">
          <CardHeader>
            <HStack justify="space-between" align="start">
              <VStack align="start" spacing={2}>
                <Heading size="xl" color="gray.800">
                  {project.project_name}
                </Heading>
                <HStack spacing={3}>
                  <Badge colorScheme="blue" px={3} py={1} borderRadius="full">
                    Saved Project
                  </Badge>
                  <Text color="gray.500" fontSize="sm">
                    Created: {new Date(project.created_at).toLocaleDateString()}
                  </Text>
                  <Text color="gray.500" fontSize="sm">
                    Updated: {new Date(project.updated_at).toLocaleDateString()}
                  </Text>
                </HStack>
              </VStack>
              <HStack spacing={3}>
                <Button
                  as={Link}
                  to={`/project/${id}/edit`}
                  leftIcon={<FaEdit />}
                  colorScheme="aws"
                  variant="outline"
                >
                  Edit Project
                </Button>
                <Button
                  onClick={handleDelete}
                  leftIcon={<FaTrash />}
                  colorScheme="red"
                  variant="outline"
                >
                  Delete
                </Button>
                <Button
                  as={Link}
                  to="/projects"
                  leftIcon={<FaEye />}
                  variant="outline"
                >
                  All Projects
                </Button>
              </HStack>
            </HStack>
          </CardHeader>
        </Card>

        {/* Project Description */}
        <Card shadow="lg">
          <CardHeader>
            <Heading size="lg">Project Description</Heading>
          </CardHeader>
          <CardBody>
            <Text color="gray.700" lineHeight="tall">
              {project.description}
            </Text>
          </CardBody>
        </Card>

        {/* Architecture Display - Use the saved architecture data */}
        <Box>
          <Heading size="lg" mb={6}>Generated Architecture</Heading>
          <ArchitectureDashboard savedArchitecture={architecture} />
        </Box>
      </VStack>
    </Box>
  );
};

export default ProjectView;