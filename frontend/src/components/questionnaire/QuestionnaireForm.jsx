import React, { useState } from 'react';
import {
  Box,
  Card,
  CardBody,
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
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Collapse,
  IconButton,
  Tooltip,
  Badge,
  Divider,
  SimpleGrid,
  useDisclosure,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeftIcon, ChevronRightIcon, InfoIcon, ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons';
import { FaRocket, FaSave, FaQuestionCircle, FaLightbulb, FaAws, FaShieldAlt, FaDollarSign } from 'react-icons/fa';
import { projectService } from '../../services/projectService';
import { QUESTIONNAIRE_QUESTIONS } from '../../utils/constants';

const QuestionnaireForm = () => {
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

  // Save modal state
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [saving, setSaving] = useState(false);
  
  // Loading and error states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Help and explanation states
  const [showExplanation, setShowExplanation] = useState(true);
  const { isOpen: isHelpOpen, onToggle: onHelpToggle } = useDisclosure();

  const navigate = useNavigate();
  const toast = useToast();

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

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      
      console.log('Generating architecture with data:', formData);
      
      const result = await projectService.generateArchitecture(formData);
      
      console.log('Generation result:', result);
      
      toast({
        title: 'Architecture Generated!',
        description: 'Your AWS architecture has been created successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      if (result.project_id) {
        console.log('Navigating to project:', result.project_id);
        navigate(`/project/${result.project_id}`);
      } else {
        console.error('No project ID in result:', result);
        throw new Error('No project ID returned from server');
      }
      
    } catch (err) {
      console.error('Error generating architecture:', err);
      setError(err.message);
      toast({
        title: 'Generation Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      const projectData = {
        questionnaire: formData,
        save_name: saveName.trim() || formData.project_name
      };
      
      const result = await projectService.createProject(projectData);
      
      toast({
        title: 'Project Saved!',
        description: 'Your project has been saved successfully.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      setShowSaveModal(false);
      navigate(`/project/${result.id}`);
      
    } catch (err) {
      toast({
        title: 'Save Failed',
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

  // Enhanced explanation component
  const QuestionExplanation = ({ question }) => (
    <Card bg="blue.50" borderLeft="4px" borderColor="blue.400" mb={6}>
      <CardBody p={4}>
        <VStack align="start" spacing={3}>
          <HStack>
            <FaLightbulb color="#3182CE" />
            <Text fontWeight="bold" color="blue.800">
              Why we ask this
            </Text>
          </HStack>
          <Text fontSize="sm" color="blue.700">
            {question.explanation || "This helps us understand your requirements to suggest the best AWS services for your project."}
          </Text>
          
          {question.impact && (
            <VStack align="start" spacing={2} w="full">
              <Text fontWeight="semibold" fontSize="sm" color="blue.800">
                Impact on your architecture:
              </Text>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={2} w="full">
                {question.impact.services && (
                  <HStack>
                    <FaAws color="#FF9900" />
                    <Text fontSize="xs" color="blue.600">
                      Services: {question.impact.services}
                    </Text>
                  </HStack>
                )}
                {question.impact.security && (
                  <HStack>
                    <FaShieldAlt color="#38A169" />
                    <Text fontSize="xs" color="blue.600">
                      Security: {question.impact.security}
                    </Text>
                  </HStack>
                )}
                {question.impact.cost && (
                  <HStack>
                    <FaDollarSign color="#38A169" />
                    <Text fontSize="xs" color="blue.600">
                      Cost: {question.impact.cost}
                    </Text>
                  </HStack>
                )}
              </SimpleGrid>
            </VStack>
          )}
        </VStack>
      </CardBody>
    </Card>
  );

  // Enhanced option component with detailed explanations
  const EnhancedOption = ({ option, value, isSelected, onSelect, type }) => {
    const [showDetails, setShowDetails] = useState(false);
    
    return (
      <Card 
        variant="outline" 
        cursor="pointer"
        borderColor={isSelected ? "blue.400" : "gray.200"}
        bg={isSelected ? "blue.50" : "white"}
        _hover={{ borderColor: "blue.300", shadow: "md" }}
        transition="all 0.2s"
      >
        <CardBody p={4}>
          <VStack align="stretch" spacing={3}>
            <HStack justify="space-between" align="start">
              <HStack flex={1} align="start" spacing={3}>
                {type === 'radio' ? (
                  <Radio 
                    value={value} 
                    colorScheme="blue" 
                    size="lg"
                    isChecked={isSelected}
                    onChange={() => onSelect(value)}
                  />
                ) : (
                  <Checkbox 
                    value={value} 
                    colorScheme="blue" 
                    size="lg"
                    isChecked={isSelected}
                    onChange={() => onSelect(value)}
                  />
                )}
                <VStack align="start" spacing={1} flex={1}>
                  <HStack>
                    <Text fontWeight="semibold" color="gray.800">
                      {option.label}
                    </Text>
                    {option.recommended && (
                      <Badge colorScheme="green" size="sm">
                        Recommended
                      </Badge>
                    )}
                    {option.popular && (
                      <Badge colorScheme="blue" size="sm">
                        Popular
                      </Badge>
                    )}
                  </HStack>
                  {option.description && (
                    <Text fontSize="sm" color="gray.600">
                      {option.description}
                    </Text>
                  )}
                </VStack>
              </HStack>
              
              {option.detailedInfo && (
                <Tooltip label={showDetails ? "Hide details" : "Show details"} placement="top">
                  <IconButton
                    icon={<InfoIcon />}
                    size="sm"
                    variant="ghost"
                    colorScheme="blue"
                    aria-label="Toggle detailed information"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent triggering the radio/checkbox
                      setShowDetails(!showDetails);
                    }}
                    bg={showDetails ? "blue.100" : "transparent"}
                  />
                </Tooltip>
              )}
            </HStack>

            {/* Detailed information section */}
            <Collapse in={showDetails} animateOpacity>
              {option.detailedInfo && (
                <Box mt={3} pt={3} borderTop="1px" borderColor="gray.200">
                  <VStack align="start" spacing={3}>
                    {option.detailedInfo.awsServices && (
                      <HStack align="start">
                        <FaAws color="#FF9900" />
                        <VStack align="start" spacing={1}>
                          <Text fontSize="xs" fontWeight="semibold" color="orange.600">
                            AWS Services:
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {option.detailedInfo.awsServices}
                          </Text>
                        </VStack>
                      </HStack>
                    )}
                    
                    {option.detailedInfo.costRange && (
                      <HStack align="start">
                        <FaDollarSign color="#38A169" />
                        <VStack align="start" spacing={1}>
                          <Text fontSize="xs" fontWeight="semibold" color="green.600">
                            Typical Cost Range:
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {option.detailedInfo.costRange}
                          </Text>
                        </VStack>
                      </HStack>
                    )}

                    {option.detailedInfo.useCase && (
                      <HStack align="start">
                        <FaQuestionCircle color="#805AD5" />
                        <VStack align="start" spacing={1}>
                          <Text fontSize="xs" fontWeight="semibold" color="purple.600">
                            Best For:
                          </Text>
                          <Text fontSize="xs" color="gray.600">
                            {option.detailedInfo.useCase}
                          </Text>
                        </VStack>
                      </HStack>
                    )}
                  </VStack>
                </Box>
              )}
            </Collapse>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  const renderInput = () => {
    switch (currentQuestion.type) {
      case 'text':
        return (
          <VStack spacing={4} align="stretch">
            <Input
              value={currentValue || ''}
              onChange={(e) => handleInputChange(currentQuestion.id, e.target.value)}
              placeholder={currentQuestion.placeholder}
              size="lg"
              focusBorderColor="blue.500"
            />
            {currentQuestion.examples && (
              <Card bg="gray.50" variant="outline">
                <CardBody p={3}>
                  <Text fontSize="sm" fontWeight="semibold" color="gray.700" mb={2}>
                    Examples:
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {currentQuestion.examples.join(', ')}
                  </Text>
                </CardBody>
              </Card>
            )}
          </VStack>
        );
      
      case 'textarea':
        return (
          <VStack spacing={4} align="stretch">
            <Textarea
              value={currentValue || ''}
              onChange={(e) => handleInputChange(currentQuestion.id, e.target.value)}
              placeholder={currentQuestion.placeholder}
              size="lg"
              rows={4}
              focusBorderColor="blue.500"
            />
            {currentQuestion.examples && (
              <Card bg="gray.50" variant="outline">
                <CardBody p={3}>
                  <Text fontSize="sm" fontWeight="semibold" color="gray.700" mb={2}>
                    Example descriptions:
                  </Text>
                  <VStack align="start" spacing={1}>
                    {currentQuestion.examples.map((example, idx) => (
                      <Text key={idx} fontSize="sm" color="gray.600">
                        • {example}
                      </Text>
                    ))}
                  </VStack>
                </CardBody>
              </Card>
            )}
          </VStack>
        );
      
      case 'radio':
        return (
          <RadioGroup
            value={currentValue || ''}
            onChange={(value) => handleInputChange(currentQuestion.id, value)}
          >
            <Stack spacing={4}>
              {currentQuestion.options.map((option) => (
                <EnhancedOption
                  key={option.value}
                  option={option}
                  value={option.value}
                  isSelected={currentValue === option.value}
                  onSelect={(value) => handleInputChange(currentQuestion.id, value)}
                  type="radio"
                />
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
                <EnhancedOption
                  key={option.value}
                  option={option}
                  value={option.value}
                  isSelected={(currentValue || []).includes(option.value)}
                  onSelect={(value) => {
                    const current = currentValue || [];
                    const newValue = current.includes(value)
                      ? current.filter(v => v !== value)
                      : [...current, value];
                    handleInputChange(currentQuestion.id, newValue);
                  }}
                  type="checkbox"
                />
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
          <Spinner size="xl" color="blue.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Generating Your AWS Architecture
            </Heading>
            <Text color="gray.600" maxW="md">
              We're analyzing your requirements and creating a custom architecture 
              with security recommendations and Infrastructure as Code templates...
            </Text>
          </VStack>
        </VStack>
      </Box>
    );
  }

  return (
    <Box maxW="5xl" mx="auto">
      <VStack spacing={8}>
        {/* Progress Bar */}
        <Box w="full">
          <HStack justify="space-between" mb={2}>
            <Text fontSize="sm" color="gray.600">
              Step {currentStep + 1} of {QUESTIONNAIRE_QUESTIONS.length}
            </Text>
            <HStack spacing={4}>
              <Text fontSize="sm" color="gray.600">
                {Math.round(progressPercentage)}% Complete
              </Text>
              <Button
                size="sm"
                leftIcon={showExplanation ? <ChevronUpIcon /> : <ChevronDownIcon />}
                variant="ghost"
                onClick={() => setShowExplanation(!showExplanation)}
              >
                {showExplanation ? 'Hide' : 'Show'} Help
              </Button>
            </HStack>
          </HStack>
          <Progress
            value={progressPercentage}
            colorScheme="blue"
            size="lg"
            borderRadius="full"
          />
        </Box>

        {/* Question Card */}
        <Card w="full" shadow="xl">
          <CardBody p={8}>
            <VStack spacing={6} align="stretch">
              {/* Question Header */}
              <VStack spacing={3} align="start">
                <HStack justify="space-between" w="full">
                  <VStack align="start" spacing={2}>
                    <Heading size="lg" color="gray.800">
                      {currentQuestion.title}
                    </Heading>
                    <Heading size="md" fontWeight="medium" color="gray.600">
                      {currentQuestion.question}
                    </Heading>
                  </VStack>
                  {currentQuestion.category && (
                    <Badge colorScheme="purple" p={2} borderRadius="md">
                      {currentQuestion.category}
                    </Badge>
                  )}
                </HStack>
                
                {currentQuestion.description && (
                  <Text color="gray.500" fontSize="sm">
                    {currentQuestion.description}
                  </Text>
                )}
              </VStack>

              {/* Explanation Section */}
              <Collapse in={showExplanation} animateOpacity>
                <QuestionExplanation question={currentQuestion} />
              </Collapse>

              <Divider />

              {/* Input Section */}
              {renderInput()}

              {/* Error Display */}
              {error && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
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

          <HStack spacing={4}>
            {/* Save Button (show on last step) */}
            {isLastStep && (
              <Button
                leftIcon={<FaSave />}
                onClick={() => setShowSaveModal(true)}
                isDisabled={!isValueValid}
                colorScheme="green"
                variant="outline"
                size="lg"
              >
                Save Project
              </Button>
            )}

            {/* Generate/Next Button */}
            {isLastStep ? (
              <Button
                rightIcon={<FaRocket />}
                onClick={handleGenerate}
                isDisabled={!isValueValid || loading}
                isLoading={loading}
                loadingText="Generating..."
                colorScheme="blue"
                size="lg"
                px={8}
              >
                Generate Architecture
              </Button>
            ) : (
              <Button
                rightIcon={<ChevronRightIcon />}
                onClick={nextStep}
                isDisabled={!isValueValid}
                colorScheme="blue"
                size="lg"
              >
                Next
              </Button>
            )}
          </HStack>
        </HStack>
      </VStack>

      {/* Save Modal */}
      <Modal isOpen={showSaveModal} onClose={() => setShowSaveModal(false)}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Save Project</ModalHeader>
          <ModalBody>
            <FormControl>
              <FormLabel>Project Name</FormLabel>
              <Input
                value={saveName}
                onChange={(e) => setSaveName(e.target.value)}
                placeholder={formData.project_name || "Enter project name"}
              />
              <Text fontSize="sm" color="gray.500" mt={2}>
                Leave empty to use "{formData.project_name}"
              </Text>
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="outline" mr={3} onClick={() => setShowSaveModal(false)}>
              Cancel
            </Button>
            <Button
              colorScheme="green"
              onClick={handleSave}
              isLoading={saving}
              leftIcon={<FaSave />}
            >
              Save Project
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default QuestionnaireForm;