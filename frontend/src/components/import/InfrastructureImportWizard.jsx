import React, { useState } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Progress,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  FormControl,
  FormLabel,
  Input,
  Select,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Icon,
  useToast,
  Spinner,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Code,
  Textarea,
  List,
  ListItem,
  ListIcon,
  Divider,
  Collapse,
  IconButton,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import {
  FaAws,
  FaCloud,
  FaServer,
  FaDatabase,
  FaBolt,
  FaShieldAlt,
  FaExclamationTriangle,
  FaCheckCircle,
  FaArrowRight,
  FaArrowLeft,
  FaEye,
  FaDownload,
  FaRocket,
  FaChevronDown,
  FaChevronUp,
  FaCopy,
} from 'react-icons/fa';
import infrastructureImportService from '../../services/infrastructureImportService';

const InfrastructureImportWizard = ({ onClose }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scannedInfrastructure, setScannedInfrastructure] = useState(null);
  const [generatedTemplates, setGeneratedTemplates] = useState({});
  const [securityAnalysis, setSecurityAnalysis] = useState(null);
  const [showTemplateDetails, setShowTemplateDetails] = useState({});
  
  const [formData, setFormData] = useState({
    aws_credentials: {
      access_key_id: '',
      secret_access_key: '',
      session_token: '',
      region: 'us-east-1',
      account_id: ''
    },
    project_name: '',
    template_type: 'terraform'
  });

  const navigate = useNavigate();
  const toast = useToast();
  const { isOpen: isTemplateModalOpen, onOpen: onTemplateModalOpen, onClose: onTemplateModalClose } = useDisclosure();
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const steps = [
    { title: 'AWS Credentials', description: 'Connect to your AWS account' },
    { title: 'Scan Infrastructure', description: 'Discover existing resources' },
    { title: 'Review & Generate', description: 'Generate templates and analyze security' },
    { title: 'Create Project', description: 'Import as new project' }
  ];

  const handleInputChange = (field, value) => {
    if (field.startsWith('aws_credentials.')) {
      const credField = field.split('.')[1];
      setFormData(prev => ({
        ...prev,
        aws_credentials: {
          ...prev.aws_credentials,
          [credField]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const validateCredentials = () => {
    const errors = infrastructureImportService.validateCredentials(formData.aws_credentials);
    if (errors.length > 0) {
      setError(errors.join(', '));
      return false;
    }
    return true;
  };

  const handleScanInfrastructure = async () => {
    if (!validateCredentials()) return;

    try {
      setLoading(true);
      setError(null);

      // For demo purposes, use mock data instead of actual scanning
      // In production, this would call the real API
      const mockInfrastructure = infrastructureImportService.getMockInfrastructure();
      
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      setScannedInfrastructure(mockInfrastructure);
      
      toast({
        title: 'Infrastructure Scanned Successfully',
        description: `Discovered ${infrastructureImportService.getTotalResourceCount(mockInfrastructure)} resources across ${infrastructureImportService.getDiscoveredServices(mockInfrastructure).length} services`,
        status: 'success',
        duration: 4000,
        isClosable: true,
      });
      
      setCurrentStep(2);
    } catch (err) {
      setError(err.message);
      toast({
        title: 'Scan Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateTemplates = async () => {
    if (!scannedInfrastructure) return;

    try {
      setLoading(true);
      setError(null);

      // Generate both Terraform and CloudFormation templates
      const [terraformResponse, cloudFormationResponse, securityResponse] = await Promise.all([
        infrastructureImportService.generateTerraform(scannedInfrastructure),
        infrastructureImportService.generateCloudFormation(scannedInfrastructure),
        infrastructureImportService.analyzeImportedSecurity(scannedInfrastructure)
      ]);

      setGeneratedTemplates({
        terraform: terraformResponse.terraform_template,
        cloudformation: cloudFormationResponse.cloudformation_template
      });

      setSecurityAnalysis(securityResponse.security_analysis);

      toast({
        title: 'Templates Generated',
        description: 'Infrastructure templates and security analysis completed',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (err) {
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

  const handleCreateProject = async () => {
    if (!formData.project_name.trim()) {
      setError('Project name is required');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const importRequest = {
        project_name: formData.project_name,
        template_type: formData.template_type,
        aws_credentials: formData.aws_credentials,
        infrastructure_data: scannedInfrastructure
      };

      const response = await infrastructureImportService.importInfrastructure(importRequest);

      toast({
        title: 'Project Created Successfully',
        description: `Project "${formData.project_name}" has been created from imported infrastructure`,
        status: 'success',
        duration: 4000,
        isClosable: true,
      });

      // Navigate to the new project
      navigate(`/project/${response.project_id}`);
    } catch (err) {
      setError(err.message);
      toast({
        title: 'Import Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewTemplate = (templateType) => {
    setSelectedTemplate({
      type: templateType,
      content: generatedTemplates[templateType]
    });
    onTemplateModalOpen();
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast({
      title: 'Copied to clipboard',
      status: 'success',
      duration: 2000,
    });
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <VStack spacing={6}>
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Connect to AWS Account</AlertTitle>
                <AlertDescription>
                  Provide your AWS credentials to scan and import existing infrastructure. 
                  We recommend using temporary credentials with read-only permissions.
                </AlertDescription>
              </Box>
            </Alert>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
              <FormControl isRequired>
                <FormLabel>AWS Access Key ID</FormLabel>
                <Input
                  placeholder="AKIAIOSFODNN7EXAMPLE"
                  value={formData.aws_credentials.access_key_id}
                  onChange={(e) => handleInputChange('aws_credentials.access_key_id', e.target.value)}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>AWS Secret Access Key</FormLabel>
                <Input
                  type="password"
                  placeholder="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
                  value={formData.aws_credentials.secret_access_key}
                  onChange={(e) => handleInputChange('aws_credentials.secret_access_key', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Session Token (Optional)</FormLabel>
                <Input
                  placeholder="For temporary credentials"
                  value={formData.aws_credentials.session_token}
                  onChange={(e) => handleInputChange('aws_credentials.session_token', e.target.value)}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>AWS Region</FormLabel>
                <Select
                  value={formData.aws_credentials.region}
                  onChange={(e) => handleInputChange('aws_credentials.region', e.target.value)}
                >
                  {infrastructureImportService.getAWSRegions().map(region => (
                    <option key={region.value} value={region.value}>
                      {region.label}
                    </option>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Account ID (Optional)</FormLabel>
                <Input
                  placeholder="123456789012"
                  value={formData.aws_credentials.account_id}
                  onChange={(e) => handleInputChange('aws_credentials.account_id', e.target.value)}
                />
              </FormControl>
            </SimpleGrid>

            <HStack justify="flex-end" w="full">
              <Button leftIcon={<FaArrowRight />} colorScheme="blue" onClick={nextStep}>
                Continue to Scan
              </Button>
            </HStack>
          </VStack>
        );

      case 1:
        return (
          <VStack spacing={6}>
            <Alert status="warning" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Infrastructure Scanning</AlertTitle>
                <AlertDescription>
                  We'll scan your AWS account for existing resources including EC2 instances, 
                  RDS databases, S3 buckets, Lambda functions, and VPC configurations.
                </AlertDescription>
              </Box>
            </Alert>

            <Card w="full">
              <CardHeader>
                <Heading size="md">Scan Configuration</Heading>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  <VStack align="start">
                    <Text fontWeight="medium">Region:</Text>
                    <Badge colorScheme="blue">{formData.aws_credentials.region}</Badge>
                  </VStack>
                  <VStack align="start">
                    <Text fontWeight="medium">Account ID:</Text>
                    <Text fontSize="sm" color="gray.600">
                      {formData.aws_credentials.account_id || 'Will be detected'}
                    </Text>
                  </VStack>
                </SimpleGrid>
              </CardBody>
            </Card>

            {loading ? (
              <VStack spacing={4}>
                <Spinner size="xl" color="blue.500" />
                <Text>Scanning your AWS infrastructure...</Text>
                <Text fontSize="sm" color="gray.600">This may take a few minutes</Text>
              </VStack>
            ) : (
              <HStack justify="space-between" w="full">
                <Button leftIcon={<FaArrowLeft />} variant="outline" onClick={prevStep}>
                  Back
                </Button>
                <Button
                  leftIcon={<FaCloud />}
                  colorScheme="blue"
                  onClick={handleScanInfrastructure}
                  isLoading={loading}
                >
                  Start Scan
                </Button>
              </HStack>
            )}
          </VStack>
        );

      case 2:
        return (
          <VStack spacing={6}>
            {scannedInfrastructure && (
              <>
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Infrastructure Discovered</AlertTitle>
                    <AlertDescription>
                      Found {infrastructureImportService.getTotalResourceCount(scannedInfrastructure)} resources 
                      across {infrastructureImportService.getDiscoveredServices(scannedInfrastructure).length} AWS services
                    </AlertDescription>
                  </Box>
                </Alert>

                <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} w="full">
                  {infrastructureImportService.getDiscoveredServices(scannedInfrastructure).map(service => {
                    const serviceData = scannedInfrastructure.services[service];
                    const resourceCount = Object.values(serviceData).reduce((total, resources) => {
                      return total + (Array.isArray(resources) ? resources.length : 0);
                    }, 0);

                    const serviceIcons = {
                      ec2: FaServer,
                      rds: FaDatabase,
                      s3: FaCloud,
                      lambda: FaBolt,
                      vpc: FaAws
                    };

                    return (
                      <Card key={service}>
                        <CardBody>
                          <VStack>
                            <Icon as={serviceIcons[service] || FaCloud} boxSize={8} color="blue.500" />
                            <Text fontWeight="bold" textTransform="uppercase">{service}</Text>
                            <Badge colorScheme="blue">{resourceCount} resources</Badge>
                          </VStack>
                        </CardBody>
                      </Card>
                    );
                  })}
                </SimpleGrid>

                <HStack spacing={4} w="full">
                  <Button
                    leftIcon={<FaRocket />}
                    colorScheme="green"
                    onClick={handleGenerateTemplates}
                    isLoading={loading}
                    loadingText="Generating..."
                  >
                    Generate Templates & Analyze Security
                  </Button>
                </HStack>

                {(generatedTemplates.terraform || generatedTemplates.cloudformation) && (
                  <Card w="full">
                    <CardHeader>
                      <Heading size="md">Generated Templates</Heading>
                    </CardHeader>
                    <CardBody>
                      <Tabs>
                        <TabList>
                          <Tab>Terraform</Tab>
                          <Tab>CloudFormation</Tab>
                          <Tab>Security Analysis</Tab>
                        </TabList>
                        <TabPanels>
                          <TabPanel px={0}>
                            <VStack spacing={4} align="start">
                              <Text>
                                Terraform configuration generated with {scannedInfrastructure?.services ? Object.keys(scannedInfrastructure.services).length : 0} service types
                              </Text>
                              <HStack>
                                <Button
                                  size="sm"
                                  leftIcon={<FaEye />}
                                  onClick={() => handleViewTemplate('terraform')}
                                >
                                  View Template
                                </Button>
                                <Button
                                  size="sm"
                                  leftIcon={<FaDownload />}
                                  variant="outline"
                                >
                                  Download
                                </Button>
                              </HStack>
                            </VStack>
                          </TabPanel>
                          <TabPanel px={0}>
                            <VStack spacing={4} align="start">
                              <Text>
                                CloudFormation template generated with all discovered resources
                              </Text>
                              <HStack>
                                <Button
                                  size="sm"
                                  leftIcon={<FaEye />}
                                  onClick={() => handleViewTemplate('cloudformation')}
                                >
                                  View Template
                                </Button>
                                <Button
                                  size="sm"
                                  leftIcon={<FaDownload />}
                                  variant="outline"
                                >
                                  Download
                                </Button>
                              </HStack>
                            </VStack>
                          </TabPanel>
                          <TabPanel px={0}>
                            {securityAnalysis && (
                              <VStack spacing={4} align="start">
                                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4} w="full">
                                  <VStack>
                                    <Icon as={FaExclamationTriangle} color="red.500" boxSize={6} />
                                    <Text fontSize="2xl" fontWeight="bold" color="red.500">
                                      {securityAnalysis.imported_findings?.filter(f => f.severity === 'high').length || 0}
                                    </Text>
                                    <Text fontSize="sm">High Risk</Text>
                                  </VStack>
                                  <VStack>
                                    <Icon as={FaShieldAlt} color="orange.500" boxSize={6} />
                                    <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                                      {securityAnalysis.imported_findings?.filter(f => f.severity === 'medium').length || 0}
                                    </Text>
                                    <Text fontSize="sm">Medium Risk</Text>
                                  </VStack>
                                  <VStack>
                                    <Icon as={FaCheckCircle} color="green.500" boxSize={6} />
                                    <Text fontSize="2xl" fontWeight="bold" color="green.500">
                                      {Math.round(securityAnalysis.security_posture_score || 85)}
                                    </Text>
                                    <Text fontSize="sm">Security Score</Text>
                                  </VStack>
                                </SimpleGrid>
                                
                                {securityAnalysis.imported_findings?.length > 0 && (
                                  <Box w="full">
                                    <Text fontWeight="medium" mb={2}>Security Findings:</Text>
                                    <List spacing={2}>
                                      {securityAnalysis.imported_findings.slice(0, 3).map((finding, index) => (
                                        <ListItem key={index} fontSize="sm">
                                          <ListIcon 
                                            as={finding.severity === 'high' ? FaExclamationTriangle : FaShieldAlt} 
                                            color={finding.severity === 'high' ? 'red.500' : 'orange.500'} 
                                          />
                                          {finding.title}
                                        </ListItem>
                                      ))}
                                    </List>
                                  </Box>
                                )}
                              </VStack>
                            )}
                          </TabPanel>
                        </TabPanels>
                      </Tabs>
                    </CardBody>
                  </Card>
                )}

                <HStack justify="space-between" w="full">
                  <Button leftIcon={<FaArrowLeft />} variant="outline" onClick={prevStep}>
                    Back
                  </Button>
                  <Button
                    leftIcon={<FaArrowRight />}
                    colorScheme="blue"
                    onClick={nextStep}
                    isDisabled={!generatedTemplates.terraform && !generatedTemplates.cloudformation}
                  >
                    Create Project
                  </Button>
                </HStack>
              </>
            )}
          </VStack>
        );

      case 3:
        return (
          <VStack spacing={6}>
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Create Project</AlertTitle>
                <AlertDescription>
                  Create a new project from your imported infrastructure. You can deploy and manage it like any other architecture.
                </AlertDescription>
              </Box>
            </Alert>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
              <FormControl isRequired>
                <FormLabel>Project Name</FormLabel>
                <Input
                  placeholder="My Imported Infrastructure"
                  value={formData.project_name}
                  onChange={(e) => handleInputChange('project_name', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>Template Type</FormLabel>
                <Select
                  value={formData.template_type}
                  onChange={(e) => handleInputChange('template_type', e.target.value)}
                >
                  <option value="terraform">Terraform</option>
                  <option value="cloudformation">CloudFormation</option>
                </Select>
              </FormControl>
            </SimpleGrid>

            <HStack justify="space-between" w="full">
              <Button leftIcon={<FaArrowLeft />} variant="outline" onClick={prevStep}>
                Back
              </Button>
              <Button
                leftIcon={<FaRocket />}
                colorScheme="green"
                onClick={handleCreateProject}
                isLoading={loading}
                loadingText="Creating Project..."
              >
                Create Project
              </Button>
            </HStack>
          </VStack>
        );

      default:
        return null;
    }
  };

  return (
    <Container maxW="4xl" py={8}>
      <VStack spacing={8}>
        {/* Header */}
        <VStack spacing={4} textAlign="center">
          <Icon as={FaAws} boxSize={12} color="orange.500" />
          <Heading size="lg">Import AWS Infrastructure</Heading>
          <Text color="gray.600" maxW="md">
            Scan your existing AWS account and import infrastructure as Infrastructure as Code templates
          </Text>
        </VStack>

        {/* Progress */}
        <Box w="full">
          <Progress value={(currentStep / (steps.length - 1)) * 100} colorScheme="blue" mb={4} />
          <HStack justify="space-between">
            {steps.map((step, index) => (
              <VStack key={index} spacing={1} flex={1}>
                <Badge
                  colorScheme={index <= currentStep ? 'blue' : 'gray'}
                  variant={index === currentStep ? 'solid' : 'outline'}
                >
                  {index + 1}
                </Badge>
                <Text fontSize="xs" textAlign="center" fontWeight="medium">
                  {step.title}
                </Text>
              </VStack>
            ))}
          </HStack>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert status="error" borderRadius="md">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Step Content */}
        <Box w="full">
          {renderStepContent()}
        </Box>

        {/* Template View Modal */}
        <Modal isOpen={isTemplateModalOpen} onClose={onTemplateModalClose} size="6xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {selectedTemplate?.type === 'terraform' ? 'Terraform Configuration' : 'CloudFormation Template'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Text fontSize="sm" color="gray.600">
                    Generated from AWS account scan
                  </Text>
                  <Button
                    size="sm"
                    leftIcon={<FaCopy />}
                    onClick={() => copyToClipboard(selectedTemplate?.content)}
                  >
                    Copy
                  </Button>
                </HStack>
                <Box maxH="500px" overflowY="auto">
                  <Code as="pre" p={4} fontSize="sm" whiteSpace="pre-wrap" w="full">
                    {selectedTemplate?.content}
                  </Code>
                </Box>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button onClick={onTemplateModalClose}>Close</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default InfrastructureImportWizard;