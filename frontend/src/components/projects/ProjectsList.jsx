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
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  IconButton,
} from '@chakra-ui/react';
import { Link } from 'react-router-dom';
import { FaEdit, FaTrash, FaEye, FaPlus } from 'react-icons/fa';
import { projectService } from '../../services/projectService';

const ProjectsList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const toast = useToast();

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      const projectList = await projectService.listProjects();
      setProjects(projectList);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (projectId, projectName) => {
    if (window.confirm(`Are you sure you want to delete "${projectName}"?`)) {
      try {
        await projectService.deleteProject(projectId);
        toast({
          title: 'Project Deleted',
          description: `"${projectName}" has been deleted successfully.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        loadProjects(); // Reload the list
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
        <VStack spacing={4}>
          <Spinner size="xl" color="awsBlue.500" />
          <Text>Loading your saved projects...</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert status="error" borderRadius="md">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <Heading size="xl">Saved Projects</Heading>
          <Button
            as={Link}
            to="/"
            leftIcon={<FaPlus />}
            colorScheme="awsBlue"
            size="lg"
          >
            New Project
          </Button>
        </HStack>

        {/* Projects Grid */}
        {projects.length === 0 ? (
          <Card>
            <CardBody textAlign="center" py={12}>
              <VStack spacing={4}>
                <Text fontSize="lg" color="gray.600">
                  No saved projects yet
                </Text>
                <Button
                  as={Link}
                  to="/"
                  leftIcon={<FaPlus />}
                  colorScheme="awsBlue"
                >
                  Create Your First Project
                </Button>
              </VStack>
            </CardBody>
          </Card>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {projects.map((project) => (
              <Card key={project.id} shadow="lg" _hover={{ shadow: 'xl' }}>
                <CardHeader>
                  <VStack align="start" spacing={2}>
                    <Heading size="md" noOfLines={1}>
                      {project.project_name}
                    </Heading>
                    <Badge colorScheme="green" variant="subtle">
                      Saved Project
                    </Badge>
                  </VStack>
                </CardHeader>
                <CardBody pt={0}>
                  <VStack spacing={4} align="stretch">
                    <Text color="gray.600" noOfLines={3} fontSize="sm">
                      {project.description}
                    </Text>
                    
                    <VStack spacing={2} align="start" fontSize="xs" color="gray.500">
                      <Text>Created: {new Date(project.created_at).toLocaleDateString()}</Text>
                      <Text>Updated: {new Date(project.updated_at).toLocaleDateString()}</Text>
                    </VStack>

                    <HStack spacing={2}>
                      <Button
                        as={Link}
                        to={`/project/${project.id}`}
                        leftIcon={<FaEye />}
                        size="sm"
                        colorScheme="awsBlue"
                        variant="outline"
                        flex={1}
                      >
                        View
                      </Button>
                      <Button
                        as={Link}
                        to={`/project/${project.id}/edit`}
                        leftIcon={<FaEdit />}
                        size="sm"
                        colorScheme="aws"
                        variant="outline"
                        flex={1}
                      >
                        Edit
                      </Button>
                      <IconButton
                        icon={<FaTrash />}
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => handleDelete(project.id, project.project_name)}
                        aria-label="Delete project"
                      />
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </VStack>
    </Box>
  );
};

export default ProjectsList;