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
  Progress,
  Input,
  Textarea,
  RadioGroup,
  Radio,
  CheckboxGroup,
  Checkbox,
  Stack,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
} from '@chakra-ui/react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { FaSave, FaEye, FaHome } from 'react-icons/fa';
import { projectService } from '../../services/projectService';
import { extractErrorMessage } from '../../utils/errorUtils';
import { QUESTIONNAIRE_QUESTIONS } from '../../utils/constants';

const ProjectEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  
  const [project, setProject] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    project_name: '',
    description: '',
    traffic_volume: '',
    data_sensitivity: '',
    compute_preference: '',
    database_type: '',
    storage_needs: '',
    geographical_reach: '',
    budget_range: '',
    compliance_requirements: []
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      setLoading(true);
      const projectData = await projectService.getProject(id);
      setProject(projectData);
      setFormData(projectData.questionnaire_data);
    } catch (err) {
      setError(extractErrorMessage(err, 'Failed to load project'));
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (questionId, value) => {
    if (questionId === 'compliance_requirements') {
      setFormData(prev => ({
        ...prev,
        [questionId]: value
      }));
    } else {
      setFormData(prev => ({ ...prev, [questionId]: value }));
    }
  };

  const nextStep = () => {
    if (currentStep < QUESTIONNAIRE_QUESTIONS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const updateData = { questionnaire: formData };
      await projectService.updateProject(id, updateData);
      
      toast({
        title: 'Project Updated!',
        description: 'Your project has been updated and architecture regenerated.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      navigate(`/project/${id}`);
      
    } catch (err) {
      toast({
        title: 'Update Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  const currentQuestion = QUESTIONNAIRE_QUESTIONS[currentStep];
  const currentValue = formData[currentQuestion.id];
  const isLastStep = currentStep === QUESTIONNAIRE_QUESTIONS.length - 1;
  const progressPercentage = ((currentStep + 1) / QUESTIONNAIRE_QUESTIONS.length) * 100;
  
  const isValueValid = currentValue && (
    !Array.isArray(currentValue) || currentValue.length > 0
  );

  const renderInput = () => {
    switch (currentQuestion.type) {
      case 'text':
        return (
          <Input
            value={currentValue || ''}
            onChange={(e) => handleInputChange(currentQuestion.id, e.target.value)}
            placeholder={currentQuestion.placeholder}
            size="lg"
            focusBorderColor="awsBlue.500"
          />
        );
      
      case 'textarea':
        return (
          <Textarea
            value={currentValue || ''}
            onChange={(e) => handleInputChange(currentQuestion.id, e.target.value)}
            placeholder={currentQuestion.placeholder}
            size="lg"
            rows={4}
            focusBorderColor="awsBlue.500"
          />
        );
      
      case 'radio':
        return (
          <RadioGroup
            value={currentValue || ''}
            onChange={(value) => handleInputChange(currentQuestion.id, value)}
          >
            <Stack spacing={4}>
              {currentQuestion.options.map((option) => (
                <Card key={option.value} variant="outline" cursor="pointer">
                  <CardBody>
                    <Radio value={option.value} colorScheme="awsBlue" size="lg">
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="semibold">{option.label}</Text>
                        {option.description && (
                          <Text fontSize="sm" color="gray.600">
                            {option.description}
                          </Text>
                        )}
                      </VStack>
                    </Radio>
                  </CardBody>
                </Card>
              ))}
            </Stack>
          </RadioGroup>
        );
      
      case 'checkbox':
        return (
          <CheckboxGroup
            value={currentValue || []}
            onChange={(value) => handleInputChange(currentQuestion.id, value)}
          >
            <Stack spacing={4}>
              {currentQuestion.options.map((option) => (
                <Card key={option.value} variant="outline">
                  <CardBody>
                    <Checkbox value={option.value} colorScheme="awsBlue" size="lg">
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="semibold">{option.label}</Text>
                        {option.description && (
                          <Text fontSize="sm" color="gray.600">
                            {option.description}
                          </Text>
                        )}
                      </VStack>
                    </Checkbox>
                  </CardBody>
                </Card>
              ))}
            </Stack>
          </CheckboxGroup>
        );
      
      default:
        return null;
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
              Loading project details for editing...
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

  if (saving) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={6}>
          <Spinner size="xl" color="awsBlue.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Updating Project
            </Heading>
            <Text color="gray.600" maxW="md">
              Saving your changes and regenerating the architecture...
            </Text>
          </VStack>
        </VStack>
      </Box>
    );
  }

  return (
    <Box maxW="4xl" mx="auto">
      <VStack spacing={8}>
        {/* Header */}
        <Card w="full" shadow="lg">
          <CardHeader>
            <HStack justify="space-between" align="center">
              <VStack align="start" spacing={1}>
                <Heading size="xl">Edit Project</Heading>
                <Text color="gray.600">
                  {project?.project_name || 'Untitled Project'}
                </Text>
              </VStack>
              <Button
                as={Link}
                to={`/project/${id}`}
                leftIcon={<FaEye />}
                variant="outline"
              >
                View Project
              </Button>
            </HStack>
          </CardHeader>
        </Card>

        {/* Progress Bar */}
        <Box w="full">
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" color="gray.600">
              Step {currentStep + 1} of {QUESTIONNAIRE_QUESTIONS.length}
            </Text>
            <Text fontSize="sm" color="gray.600">
              {Math.round(progressPercentage)}% Complete
            </Text>
          </HStack>
          <Progress
            value={progressPercentage}
            colorScheme="awsBlue"
            size="lg"
            borderRadius="full"
          />
        </Box>

        {/* Question Card */}
        <Card w="full" shadow="xl">
          <CardBody p={8}>
            <VStack spacing={6} align="stretch">
              <VStack spacing={3} align="start">
                <Heading size="lg" color="gray.800">
                  {currentQuestion.title}
                </Heading>
                <Heading size="md" fontWeight="medium" color="gray.600">
                  {currentQuestion.question}
                </Heading>
                {currentQuestion.description && (
                  <Text color="gray.500" fontSize="sm">
                    {currentQuestion.description}
                  </Text>
                )}
              </VStack>

              {renderInput()}
            </VStack>
          </CardBody>
        </Card>

        {/* Navigation */}
        <HStack w="full" justify="space-between">
          <Button
            leftIcon={<ChevronLeftIcon />}
            onClick={prevStep}
            isDisabled={currentStep === 0}
            variant="outline"
            size="lg"
          >
            Previous
          </Button>

          {isLastStep ? (
            <Button
              rightIcon={<FaSave />}
              onClick={handleSave}
              isDisabled={!isValueValid}
              colorScheme="green"
              size="lg"
              px={8}
            >
              Save Changes
            </Button>
          ) : (
            <Button
              rightIcon={<ChevronRightIcon />}
              onClick={nextStep}
              isDisabled={!isValueValid}
              colorScheme="awsBlue"
              size="lg"
            >
              Next
            </Button>
          )}
        </HStack>
      </VStack>
    </Box>
  );
};

export default ProjectEdit;