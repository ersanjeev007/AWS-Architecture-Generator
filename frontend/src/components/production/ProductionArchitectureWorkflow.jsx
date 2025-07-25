import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Card,
  CardHeader,
  CardBody,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Progress,
  Badge,
  Divider,
  SimpleGrid,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Code,
  useToast,
  Collapse,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  Switch,
  NumberInput,
  NumberInputField,
  Spinner,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer
} from '@chakra-ui/react';
import { 
  FaAws, 
  FaRocket, 
  FaShieldAlt, 
  FaDownload, 
  FaUpload,
  FaCheckCircle,
  FaExclamationTriangle,
  FaTimesCircle,
  FaCloudUploadAlt,
  FaCode,
  FaCogs,
  FaEye,
  FaCheck,
  FaInfoCircle,
  FaChevronDown,
  FaChevronUp
} from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

import { apiClient } from '../../services/api';
import { useAuth } from '../../hooks/useAuth';
import { QUESTIONNAIRE_QUESTIONS } from '../../utils/constants';

const ProductionArchitectureWorkflow = () => {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  
  const [currentTab, setCurrentTab] = useState(0);
  const [workflowStep, setWorkflowStep] = useState('choose'); // choose, create, import, deploy, monitor
  const [questionnaireStep, setQuestionnaireStep] = useState(0); // Multi-step questionnaire
  const [loading, setLoading] = useState(false);
  const [deploymentData, setDeploymentData] = useState(null);
  const [importData, setImportData] = useState(null);
  const [deploymentStatus, setDeploymentStatus] = useState(null);
  const [showDeployModal, setShowDeployModal] = useState(false);
  const [selectedAwsAccount, setSelectedAwsAccount] = useState(null);
  const [awsAccounts, setAwsAccounts] = useState([]);
  const [deploymentCredentials, setDeploymentCredentials] = useState({
    access_key_id: '',
    secret_access_key: '',
    session_token: '',
    region: 'us-west-2'
  });
  
  // Form states
  const [createFormData, setCreateFormData] = useState({
    project_name: '',
    description: '',
    deployment_tool: 'terraform',
    dry_run: true,
    questionnaire: {
      // Step 1: Basic Info
      application_type: '',
      expected_users: '',
      
      // Step 2: Technical Requirements
      performance_requirements: '',
      availability_requirements: '',
      data_sensitivity: '',
      
      // Step 3: Services & Features
      services: {
        compute: [],
        storage: [],
        database: [],
        networking: [],
        security: [],
        monitoring: []
      },
      
      // Step 4: Compliance & Budget
      compliance_requirements: [],
      budget_range: '',
      backup_requirements: '',
      
      // Always high security
      security_level: 'high'
    }
  });
  
  const [importFormData, setImportFormData] = useState({
    project_name: '',
    services_to_import: []
  });
  
  const { isOpen: isCredentialsModalOpen, onOpen: onCredentialsModalOpen, onClose: onCredentialsModalClose } = useDisclosure();
  const { isOpen: isTerraformModalOpen, onOpen: onTerraformModalOpen, onClose: onTerraformModalClose } = useDisclosure();
  const { isOpen: isDeployModalOpen, onOpen: onDeployModalOpen, onClose: onDeployModalClose } = useDisclosure();
  
  const workflowSteps = [
    { id: 'choose', title: 'Choose Approach', icon: FaCogs },
    { id: 'configure', title: 'Configure', icon: FaCode },
    { id: 'deploy', title: 'Deploy', icon: FaRocket },
    { id: 'monitor', title: 'Monitor', icon: FaEye }
  ];
  
  const handleCreateFromScratch = async (dryRun = true) => {
    setLoading(true);
    
    try {
      // For dry run, no AWS credentials needed - just generate the plan
      if (dryRun) {
        const response = await apiClient.post('/production-infrastructure/create-from-scratch', {
          ...createFormData,
          dry_run: true,
          aws_credentials: { region: 'us-west-2' } // Minimal creds for planning
        });
        
        setDeploymentData(response.data);
        
        toast({
          title: 'Architecture Plan Generated',
          description: 'Review the plan and infrastructure code. Click Deploy to apply to AWS.',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        setWorkflowStep('review');
        return;
      }
      
      // For actual deployment, use deployment credentials
      const response = await apiClient.post('/production-infrastructure/create-from-scratch', {
        ...createFormData,
        dry_run: false,
        aws_credentials: deploymentCredentials
      });
      
      setDeploymentData(response.data);
      
      toast({
        title: 'Deployment Started',
        description: 'Your AWS infrastructure is being created with full security policies',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
        
      setWorkflowStep('deploy');
      startDeploymentStatusPolling(response.data.deployment_id);
      
    } catch (error) {
      toast({
        title: 'Deployment Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleImportExisting = async () => {
    setLoading(true);
    
    try {
      const response = await apiClient.post('/production-infrastructure/import-existing', importFormData);
      
      setImportData(response.data);
      
      toast({
        title: 'Infrastructure Imported Successfully',
        description: `Imported ${response.data.summary.total_resources} resources with security analysis`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      setWorkflowStep('import-review');
      
    } catch (error) {
      toast({
        title: 'Import Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const handleApplySecurityPolicies = async (securityGapIds) => {
    setLoading(true);
    
    try {
      const response = await apiClient.post('/production-infrastructure/apply-security-policies', {
        deployment_id: importData.import_id,
        security_gap_ids: securityGapIds,
        aws_credentials: importFormData.aws_credentials
      });
      
      toast({
        title: 'Security Policies Applied',
        description: `Applying ${securityGapIds.length} security fixes`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      // Start monitoring the security policy application
      startDeploymentStatusPolling(importData.import_id);
      
    } catch (error) {
      toast({
        title: 'Security Policy Application Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const startDeploymentStatusPolling = (deploymentId) => {
    const pollStatus = async () => {
      try {
        const response = await apiClient.get(`/production-infrastructure/deployment-status/${deploymentId}`);
        setDeploymentStatus(response.data);
        
        if (response.data.status === 'complete') {
          toast({
            title: 'Deployment Complete',
            description: 'Your AWS infrastructure has been successfully deployed',
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
          setWorkflowStep('complete');
          return;
        } else if (response.data.status === 'failed') {
          toast({
            title: 'Deployment Failed',
            description: 'Check the logs for error details',
            status: 'error',
            duration: 8000,
            isClosable: true,
          });
          return;
        }
        
        // Continue polling if not complete
        setTimeout(pollStatus, 5000);
        
      } catch (error) {
        console.error('Status polling failed:', error);
        setTimeout(pollStatus, 10000); // Retry after 10 seconds on error
      }
    };
    
    pollStatus();
  };
  
  const validateAWSCredentials = async (credentials) => {
    try {
      const response = await apiClient.get('/production-infrastructure/validate-aws-credentials', {
        params: credentials
      });
      
      if (response.data.valid) {
        toast({
          title: 'AWS Credentials Valid',
          description: `Connected to AWS account ${response.data.account_id}`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        return true;
      } else {
        toast({
          title: 'Invalid AWS Credentials',
          description: response.data.error,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return false;
      }
    } catch (error) {
      toast({
        title: 'Credential Validation Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return false;
    }
  };
  
  const renderChooseApproach = () => (
    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={8}>
      <Card 
        variant="elevated" 
        cursor="pointer" 
        onClick={() => {
          setWorkflowStep('create');
          setQuestionnaireStep(0);
        }}
        _hover={{ transform: 'translateY(-4px)', shadow: 'lg' }}
        transition="all 0.2s"
      >
        <CardHeader>
          <VStack spacing={4}>
            <Box color="blue.500" fontSize="4xl">
              <FaRocket />
            </Box>
            <Heading size="lg" textAlign="center">
              Create New Architecture
            </Heading>
          </VStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Text textAlign="center" color="gray.600">
              Build AWS infrastructure from scratch with comprehensive security policies
            </Text>
            
            <VStack spacing={2} align="start">
              <Text fontWeight="bold" color="green.600">✅ What you get:</Text>
              <Text fontSize="sm">• Production-ready Terraform/CloudFormation code</Text>
              <Text fontSize="sm">• Full security policy implementation</Text>
              <Text fontSize="sm">• Compliance framework integration</Text>
              <Text fontSize="sm">• Cost-optimized resource configuration</Text>
              <Text fontSize="sm">• One-click deployment to AWS</Text>
              <Text fontSize="sm">• Real-time deployment monitoring</Text>
            </VStack>
            
            <Badge colorScheme="blue" variant="subtle" textAlign="center">
              Perfect for new projects
            </Badge>
          </VStack>
        </CardBody>
      </Card>
      
      <Card 
        variant="elevated" 
        cursor="pointer" 
        onClick={() => setWorkflowStep('import')}
        _hover={{ transform: 'translateY(-4px)', shadow: 'lg' }}
        transition="all 0.2s"
      >
        <CardHeader>
          <VStack spacing={4}>
            <Box color="orange.500" fontSize="4xl">
              <FaUpload />
            </Box>
            <Heading size="lg" textAlign="center">
              Import Existing Infrastructure
            </Heading>
          </VStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Text textAlign="center" color="gray.600">
              Import and analyze your existing AWS infrastructure with Terraformer
            </Text>
            
            <VStack spacing={2} align="start">
              <Text fontWeight="bold" color="green.600">✅ What you get:</Text>
              <Text fontSize="sm">• Complete infrastructure scan and import</Text>
              <Text fontSize="sm">• Security gap analysis and recommendations</Text>
              <Text fontSize="sm">• Compliance status assessment</Text>
              <Text fontSize="sm">• Auto-generated Terraform code</Text>
              <Text fontSize="sm">• One-click security policy application</Text>
              <Text fontSize="sm">• Visual architecture diagram</Text>
            </VStack>
            
            <Badge colorScheme="orange" variant="subtle" textAlign="center">
              Perfect for existing AWS accounts
            </Badge>
          </VStack>
        </CardBody>
      </Card>
    </SimpleGrid>
  );
  
  const questionnaireSteps = [
    { title: 'Project Basics', icon: FaCode },
    { title: 'Application Type', icon: FaCogs },
    { title: 'Technical Requirements', icon: FaShieldAlt },
    { title: 'AWS Services', icon: FaAws },
    { title: 'Compliance & Budget', icon: FaCheckCircle }
  ];

  const renderCreateForm = () => (
    <VStack spacing={6} align="stretch">
      {/* Progress Steps */}
      <Card>
        <CardBody>
          <VStack spacing={4}>
            <HStack justify="space-between" width="100%">
              <Text fontSize="lg" fontWeight="bold">
                Step {questionnaireStep + 1} of {questionnaireSteps.length}: {questionnaireSteps[questionnaireStep].title}
              </Text>
              <Text fontSize="sm" color="gray.500">
                {Math.round(((questionnaireStep + 1) / questionnaireSteps.length) * 100)}% Complete
              </Text>
            </HStack>
            <Progress 
              value={((questionnaireStep + 1) / questionnaireSteps.length) * 100} 
              colorScheme="blue" 
              size="md" 
              width="100%" 
            />
          </VStack>
        </CardBody>
      </Card>

      {/* Step Content */}
      {renderQuestionnaireStep()}
      
      {/* Navigation Buttons */}
      <HStack justify="space-between">
        <Button
          variant="ghost"
          onClick={() => {
            if (questionnaireStep > 0) {
              setQuestionnaireStep(questionnaireStep - 1);
            } else {
              setWorkflowStep('choose');
            }
          }}
        >
          {questionnaireStep > 0 ? 'Previous' : 'Back to Selection'}
        </Button>
        <Button
          colorScheme="blue"
          onClick={() => {
            if (questionnaireStep < questionnaireSteps.length - 1) {
              setQuestionnaireStep(questionnaireStep + 1);
            } else {
              handleCreateArchitecture();
            }
          }}
          isDisabled={!isCurrentStepValid()}
        >
          {questionnaireStep < questionnaireSteps.length - 1 ? 'Next' : 'Generate Architecture'}
        </Button>
      </HStack>
      
    </VStack>
  );

  const renderQuestionnaireStep = () => {
    switch (questionnaireStep) {
      case 0: return renderProjectBasicsStep();
      case 1: return renderApplicationTypeStep();
      case 2: return renderTechnicalRequirementsStep();
      case 3: return renderAWSServicesStep();
      case 4: return renderComplianceBudgetStep();
      default: return renderProjectBasicsStep();
    }
  };

  const isCurrentStepValid = () => {
    switch (questionnaireStep) {
      case 0: return createFormData.project_name.trim() !== '';
      case 1: return createFormData.questionnaire.application_type !== '' && 
                     createFormData.questionnaire.compute_preference !== '' &&
                     createFormData.questionnaire.traffic_volume !== '';
      case 2: return createFormData.questionnaire.database_type !== '' && 
                     createFormData.questionnaire.data_sensitivity !== '';
      case 3: return true; // Auto-select services if none chosen
      case 4: return createFormData.questionnaire.budget_range !== '';
      default: return true;
    }
  };

  const handleCreateArchitecture = async () => {
    setLoading(true);
    
    try {
      // Auto-select default services if none selected
      const finalFormData = { ...createFormData };
      const hasSelectedServices = Object.values(finalFormData.questionnaire.services).some(arr => arr && arr.length > 0);
      
      if (!hasSelectedServices) {
        // Auto-select based on application type
        const appType = finalFormData.questionnaire.application_type;
        let defaultServices = {
          compute: ['EC2', 'Lambda'],
          storage: ['S3', 'EBS'],
          database: ['RDS'],
          networking: ['VPC', 'CloudFront'],
          security: ['IAM', 'KMS'],
          monitoring: ['CloudWatch', 'CloudTrail']
        };
        
        // Customize based on application type
        if (appType === 'api-microservices') {
          defaultServices.compute = ['Lambda', 'ECS'];
          defaultServices.database = ['DynamoDB'];
          defaultServices.networking.push('API Gateway');
        } else if (appType === 'data-analytics') {
          defaultServices.compute.push('EMR');
          defaultServices.database = ['Redshift', 'S3'];
          defaultServices.storage.push('Data Lake');
        } else if (appType === 'machine-learning') {
          defaultServices.compute = ['SageMaker', 'Lambda'];
          defaultServices.storage.push('S3');
        }
        
        finalFormData.questionnaire.services = defaultServices;
      }
      
      const response = await apiClient.post('/production-infrastructure/create-from-scratch', {
        ...finalFormData,
        dry_run: true,
        aws_credentials: { region: 'us-west-2' }
      });
      
      setDeploymentData(response.data);
      setWorkflowStep('review');
      
      toast({
        title: 'Architecture Generated Successfully',
        description: 'Your infrastructure plan is ready for review',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
    } catch (error) {
      toast({
        title: 'Generation Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 8000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadArchitectureDocument = () => {
    if (!deploymentData) return;
    
    const document = `
# AWS Architecture Document
Generated on: ${new Date().toLocaleDateString()}

## Project Information
- **Project Name**: ${createFormData.project_name}
- **Description**: ${createFormData.description || 'No description provided'}
- **Application Type**: ${createFormData.questionnaire.application_type}
- **Expected Users**: ${createFormData.questionnaire.expected_users}
- **Performance Requirements**: ${createFormData.questionnaire.performance_requirements}
- **Availability Requirements**: ${createFormData.questionnaire.availability_requirements}%
- **Data Sensitivity**: ${createFormData.questionnaire.data_sensitivity}
- **Budget Range**: ${createFormData.questionnaire.budget_range}
- **Compliance Requirements**: ${createFormData.questionnaire.compliance_requirements.join(', ') || 'None'}

## Architecture Overview
${deploymentData.security_features ? '### Security Features\n' + deploymentData.security_features.map(f => `- ${f}`).join('\n') : ''}

${deploymentData.compliance_frameworks ? '\n### Compliance Frameworks\n' + deploymentData.compliance_frameworks.map(f => `- ${f}`).join('\n') : ''}

${deploymentData.estimated_cost ? '\n### Estimated Monthly Cost\n$' + deploymentData.estimated_cost : ''}

${deploymentData.resources_planned ? '\n### Resources to be Created\n' + deploymentData.resources_planned + ' AWS resources' : ''}

## Infrastructure as Code
\`\`\`terraform
${deploymentData.terraform_code || 'Terraform code will be generated'}
\`\`\`

## Next Steps
${deploymentData.next_steps ? deploymentData.next_steps.map(step => `- ${step}`).join('\n') : '- Review the architecture\n- Deploy to AWS when ready\n- Monitor deployment progress'}

---
Generated with AWS Architecture Generator
`;

    const blob = new Blob([document], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${createFormData.project_name || 'aws-architecture'}-plan.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: 'Document Downloaded',
      description: 'Architecture document downloaded successfully',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  // Clean info box for better readability
  const InfoBox = ({ children, variant = "info" }) => {
    const colorScheme = {
      info: { bg: "blue.50", border: "blue.200", icon: "💡" },
      tip: { bg: "green.50", border: "green.200", icon: "💡" },
      warning: { bg: "orange.50", border: "orange.200", icon: "⚠️" }
    }[variant];
    
    return (
      <Box 
        p={3} 
        bg={colorScheme.bg} 
        border="1px solid" 
        borderColor={colorScheme.border} 
        borderRadius="md" 
        fontSize="sm"
      >
        <HStack align="start" spacing={2}>
          <Text>{colorScheme.icon}</Text>
          <Box>{children}</Box>
        </HStack>
      </Box>
    );
  };

  // Simple option card component
  const OptionCard = ({ option, isSelected, onClick, showDetails = false }) => (
    <Card 
      variant="outline" 
      cursor="pointer"
      borderColor={isSelected ? 'blue.500' : 'gray.200'}
      bg={isSelected ? 'blue.50' : 'white'}
      onClick={onClick}
      width="100%"
      _hover={{ borderColor: 'blue.300', shadow: 'sm' }}
      transition="all 0.2s"
    >
      <CardBody p={4}>
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={1} flex={1}>
            <HStack>
              <Text fontWeight="bold" fontSize="md">{option.label}</Text>
              {option.recommended && <Badge colorScheme="green" size="sm">Recommended</Badge>}
              {option.popular && <Badge colorScheme="blue" size="sm">Popular</Badge>}
            </HStack>
            <Text fontSize="sm" color="gray.600">{option.description}</Text>
          </VStack>
          {showDetails && option.detailedInfo && (
            <Text fontSize="sm" color="green.600" fontWeight="medium" minW="fit-content">
              {option.detailedInfo.costRange}
            </Text>
          )}
        </HStack>
      </CardBody>
    </Card>
  );

  const renderProjectBasicsStep = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Project Basics</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          <FormControl isRequired>
            <FormLabel>Project Name</FormLabel>
            <Input
              value={createFormData.project_name}
              onChange={(e) => setCreateFormData({...createFormData, project_name: e.target.value})}
              placeholder="my-aws-project"
            />
          </FormControl>
          
          <FormControl>
            <FormLabel>Description</FormLabel>
            <Textarea
              value={createFormData.description}
              onChange={(e) => setCreateFormData({...createFormData, description: e.target.value})}
              placeholder="Description of your AWS architecture"
            />
          </FormControl>
          
          <Alert status="info">
            <AlertIcon />
            <Box>
              <AlertTitle fontSize="sm">Enterprise Security Enabled</AlertTitle>
              <AlertDescription fontSize="xs">
                All architectures include high-security configurations with encryption, IAM best practices, and compliance frameworks. Deployment tool selection will be available in the architecture view.
              </AlertDescription>
            </Box>
          </Alert>
        </VStack>
      </CardBody>
    </Card>
  );

  const renderApplicationTypeStep = () => {
    const computeQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'compute_preference');
    const trafficQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'traffic_volume');
    
    return (
      <Card>
        <CardHeader>
          <Heading size="md">Application Type & Scale</Heading>
          <Text fontSize="sm" color="gray.600" mt={2}>
            Tell us about your application to recommend the best AWS services
          </Text>
        </CardHeader>
        <CardBody>
          <VStack spacing={8}>
            {/* Application Type */}
            <FormControl isRequired>
              <FormLabel fontSize="lg" fontWeight="semibold">What type of application are you building?</FormLabel>
              <Select
                value={createFormData.questionnaire.application_type}
                onChange={(e) => setCreateFormData({
                  ...createFormData,
                  questionnaire: {...createFormData.questionnaire, application_type: e.target.value}
                })}
                placeholder="Select application type"
                size="lg"
              >
                <option value="web-application">🌐 Web Application (Frontend + Backend)</option>
                <option value="api-microservices">⚡ API/Microservices (Serverless APIs)</option>
                <option value="data-analytics">📊 Data Analytics (Big Data Processing)</option>
                <option value="machine-learning">🤖 Machine Learning (AI/ML Workloads)</option>
                <option value="mobile-backend">📱 Mobile Backend (App APIs)</option>
                <option value="enterprise-app">🏢 Enterprise Application (Business Systems)</option>
                <option value="iot-platform">🌐 IoT Platform (Device Management)</option>
                <option value="ecommerce">🛒 E-commerce (Online Store)</option>
              </Select>
            </FormControl>
            
            <Divider />
            
            {/* Compute Strategy */}
            <FormControl>
              <FormLabel fontSize="lg" fontWeight="semibold">How do you want to run your application?</FormLabel>
              <InfoBox>
                <Text>Different compute options offer various benefits in terms of cost, scalability, and management overhead.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {computeQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={option}
                    isSelected={createFormData.questionnaire.compute_preference === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, compute_preference: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
            
            <Divider />
            
            {/* Traffic Volume */}
            <FormControl>
              <FormLabel fontSize="lg" fontWeight="semibold">Expected daily traffic</FormLabel>
              <InfoBox>
                <Text>This helps us size your infrastructure and set up auto-scaling.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {trafficQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={option}
                    isSelected={createFormData.questionnaire.traffic_volume === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, traffic_volume: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  const renderTechnicalRequirementsStep = () => {
    const databaseQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'database_type');
    const storageQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'storage_needs');
    const dataSecurityQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'data_sensitivity');
    
    return (
      <Card>
        <CardHeader>
          <Heading size="md">Technical Requirements</Heading>
          <Text fontSize="sm" color="gray.600" mt={2}>
            Configure data storage and security requirements
          </Text>
        </CardHeader>
        <CardBody>
          <VStack spacing={8}>
            {/* Database Type */}
            <FormControl isRequired>
              <FormLabel fontSize="lg" fontWeight="semibold">What type of database do you need?</FormLabel>
              <InfoBox>
                <Text>SQL databases are great for structured data with relationships, while NoSQL excels at flexible, scalable applications.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {databaseQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={option}
                    isSelected={createFormData.questionnaire.database_type === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, database_type: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
            
            <Divider />
            
            {/* Storage Requirements */}
            <FormControl>
              <FormLabel fontSize="lg" fontWeight="semibold">How much file storage do you expect?</FormLabel>
              <InfoBox>
                <Text>Storage requirements help us determine the right AWS storage services and estimate costs.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {storageQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={option}
                    isSelected={createFormData.questionnaire.storage_needs === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, storage_needs: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
            
            <Divider />
            
            {/* Data Security */}
            <FormControl>
              <FormLabel fontSize="lg" fontWeight="semibold">How sensitive is your data?</FormLabel>
              <InfoBox variant="warning">
                <Text>Data sensitivity determines security controls and compliance measures. All architectures include high security by default.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {dataSecurityQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={option}
                    isSelected={createFormData.questionnaire.data_sensitivity === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, data_sensitivity: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
          </VStack>
        </CardBody>
      </Card>
    );
  };

  const renderAWSServicesStep = () => {
    const serviceCategories = {
      compute: {
        label: 'Compute Services',
        options: ['EC2', 'Lambda', 'ECS', 'EKS', 'Fargate', 'Batch']
      },
      storage: {
        label: 'Storage Services', 
        options: ['S3', 'EBS', 'EFS', 'FSx']
      },
      database: {
        label: 'Database Services',
        options: ['RDS', 'DynamoDB', 'Aurora', 'ElastiCache', 'Redshift']
      },
      networking: {
        label: 'Networking',
        options: ['VPC', 'CloudFront', 'Route53', 'API Gateway', 'Load Balancer']
      },
      security: {
        label: 'Security Services',
        options: ['IAM', 'Cognito', 'KMS', 'Secrets Manager', 'WAF']
      },
      monitoring: {
        label: 'Monitoring & Logging',
        options: ['CloudWatch', 'X-Ray', 'CloudTrail', 'Config']
      }
    };

    return (
      <Card>
        <CardHeader>
          <Heading size="md">AWS Services Selection</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={6}>
            {Object.entries(serviceCategories).map(([category, {label, options}]) => (
              <Box key={category} width="100%">
                <Text fontWeight="bold" mb={2}>{label}</Text>
                <SimpleGrid columns={{ base: 2, md: 3 }} spacing={2}>
                  {options.map(service => (
                    <Button
                      key={service}
                      size="sm"
                      variant={createFormData.questionnaire.services[category]?.includes(service) ? "solid" : "outline"}
                      colorScheme={createFormData.questionnaire.services[category]?.includes(service) ? "blue" : "gray"}
                      onClick={() => {
                        const currentServices = createFormData.questionnaire.services[category] || [];
                        const isSelected = currentServices.includes(service);
                        const newServices = isSelected 
                          ? currentServices.filter(s => s !== service)
                          : [...currentServices, service];
                        
                        setCreateFormData({
                          ...createFormData,
                          questionnaire: {
                            ...createFormData.questionnaire,
                            services: {
                              ...createFormData.questionnaire.services,
                              [category]: newServices
                            }
                          }
                        });
                      }}
                    >
                      {service}
                    </Button>
                  ))}
                </SimpleGrid>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>
    );
  };

  const renderComplianceBudgetStep = () => {
    const complianceQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'compliance_requirements');
    const budgetQuestion = QUESTIONNAIRE_QUESTIONS.find(q => q.id === 'budget_range');
    
    return (
      <Card>
        <CardHeader>
          <Heading size="md">Compliance & Budget</Heading>
          <Text fontSize="sm" color="gray.600" mt={2}>
            Configure compliance requirements and budget constraints
          </Text>
        </CardHeader>
        <CardBody>
          <VStack spacing={8}>
            {/* Compliance Requirements */}
            <FormControl>
              <FormLabel fontSize="lg" fontWeight="semibold">Compliance Requirements (Optional)</FormLabel>
              <InfoBox>
                <Text>Select any compliance standards your application must meet. You can select multiple or none if not applicable.</Text>
              </InfoBox>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={3} mt={4}>
                {complianceQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={{
                      ...option,
                      label: option.value === 'none' ? '🚫 ' + option.label : '✅ ' + option.label
                    }}
                    isSelected={createFormData.questionnaire.compliance_requirements.includes(option.value)}
                    onClick={() => {
                      const current = createFormData.questionnaire.compliance_requirements;
                      const isSelected = current.includes(option.value);
                      let newCompliance;
                      
                      if (option.value === 'none') {
                        newCompliance = isSelected ? [] : ['none'];
                      } else {
                        newCompliance = isSelected 
                          ? current.filter(f => f !== option.value)
                          : [...current.filter(f => f !== 'none'), option.value];
                      }
                      
                      setCreateFormData({
                        ...createFormData,
                        questionnaire: {
                          ...createFormData.questionnaire,
                          compliance_requirements: newCompliance
                        }
                      });
                    }}
                    showDetails={false}
                  />
                ))}
              </SimpleGrid>
            </FormControl>
            
            <Divider />
            
            {/* Budget Range */}
            <FormControl isRequired>
              <FormLabel fontSize="lg" fontWeight="semibold">Expected Monthly Budget</FormLabel>
              <InfoBox>
                <Text>This helps us recommend cost-effective solutions and suggest Reserved Instances for savings.</Text>
              </InfoBox>
              <VStack spacing={3} mt={4}>
                {budgetQuestion?.options.map(option => (
                  <OptionCard
                    key={option.value}
                    option={{
                      ...option,
                      label: '💰 ' + option.label
                    }}
                    isSelected={createFormData.questionnaire.budget_range === option.value}
                    onClick={() => setCreateFormData({
                      ...createFormData,
                      questionnaire: {...createFormData.questionnaire, budget_range: option.value}
                    })}
                    showDetails={true}
                  />
                ))}
              </VStack>
            </FormControl>
          </VStack>
        </CardBody>
      </Card>
    );
  };
  
  const renderImportForm = () => (
    <VStack spacing={6} align="stretch">
      <Card>
        <CardHeader>
          <Heading size="md">Import Configuration</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <FormControl isRequired>
              <FormLabel>Project Name</FormLabel>
              <Input
                value={importFormData.project_name}
                onChange={(e) => setImportFormData({...importFormData, project_name: e.target.value})}
                placeholder="imported-infrastructure"
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Services to Import (Optional - leave empty for all)</FormLabel>
              <Text fontSize="sm" color="gray.600" mb={2}>
                Select specific services to import, or leave empty to import all discovered resources
              </Text>
              {/* Add service selection checkboxes here */}
            </FormControl>
          </VStack>
        </CardBody>
      </Card>
      
      <Card>
        <CardHeader>
          <Heading size="md">AWS Credentials</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <Alert status="warning">
              <AlertIcon />
              <Box>
                <AlertTitle>Read Permissions Required</AlertTitle>
                <AlertDescription>
                  Import requires read permissions across AWS services to discover resources
                </AlertDescription>
              </Box>
            </Alert>
            
            <HStack spacing={4} width="100%">
              <FormControl isRequired>
                <FormLabel>AWS Access Key ID</FormLabel>
                <Input
                  type="password"
                  value={importFormData.aws_credentials.access_key_id}
                  onChange={(e) => setImportFormData({
                    ...importFormData,
                    aws_credentials: {...importFormData.aws_credentials, access_key_id: e.target.value}
                  })}
                  placeholder="AKIA..."
                />
              </FormControl>
              
              <FormControl isRequired>
                <FormLabel>AWS Secret Access Key</FormLabel>
                <Input
                  type="password"
                  value={importFormData.aws_credentials.secret_access_key}
                  onChange={(e) => setImportFormData({
                    ...importFormData,
                    aws_credentials: {...importFormData.aws_credentials, secret_access_key: e.target.value}
                  })}
                  placeholder="Secret Key"
                />
              </FormControl>
            </HStack>
            
            <HStack spacing={4} width="100%">
              <FormControl>
                <FormLabel>AWS Session Token (Optional)</FormLabel>
                <Input
                  type="password"
                  value={importFormData.aws_credentials.session_token}
                  onChange={(e) => setImportFormData({
                    ...importFormData,
                    aws_credentials: {...importFormData.aws_credentials, session_token: e.target.value}
                  })}
                  placeholder="Session Token"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>AWS Region</FormLabel>
                <Select
                  value={importFormData.aws_credentials.region}
                  onChange={(e) => setImportFormData({
                    ...importFormData,
                    aws_credentials: {...importFormData.aws_credentials, region: e.target.value}
                  })}
                >
                  <option value="us-east-1">US East (N. Virginia)</option>
                  <option value="us-west-2">US West (Oregon)</option>
                  <option value="eu-west-1">Europe (Ireland)</option>
                  <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                </Select>
              </FormControl>
            </HStack>
            
            <Button
              colorScheme="orange"
              variant="outline"
              onClick={() => validateAWSCredentials(importFormData.aws_credentials)}
            >
              Validate Credentials
            </Button>
          </VStack>
        </CardBody>
      </Card>
      
      <HStack spacing={4} justify="center">
        <Button onClick={() => setWorkflowStep('choose')}>
          Back
        </Button>
        <Button
          colorScheme="orange"
          onClick={handleImportExisting}
          isLoading={loading}
          loadingText="Importing Infrastructure..."
        >
          Import Infrastructure
        </Button>
      </HStack>
    </VStack>
  );
  
  const renderDeploymentReview = () => (
    <VStack spacing={6} align="stretch">
      {deploymentData && (
        <>
          <Alert status="success">
            <AlertIcon />
            <Box>
              <AlertTitle>Architecture Plan Generated Successfully!</AlertTitle>
              <AlertDescription>
                Review the plan below and deploy when ready
              </AlertDescription>
            </Box>
          </Alert>
          
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  ${deploymentData.estimated_cost}
                </Text>
                <Text fontSize="sm" color="gray.600">Estimated Monthly Cost</Text>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {deploymentData.resources_planned}
                </Text>
                <Text fontSize="sm" color="gray.600">Resources to Create</Text>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                  {deploymentData.security_features?.length || 7}
                </Text>
                <Text fontSize="sm" color="gray.600">Security Features</Text>
              </CardBody>
            </Card>
          </SimpleGrid>
          
          <Card>
            <CardHeader>
              <Heading size="md">Security Features Included</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={2}>
                {deploymentData.security_features?.map((feature, index) => (
                  <HStack key={index} spacing={2}>
                    <FaCheckCircle color="green" />
                    <Text fontSize="sm">{feature}</Text>
                  </HStack>
                )) || [
                  "Enhanced IAM policies with least privilege",
                  "VPC with private subnets and NACLs",  
                  "CloudTrail logging enabled",
                  "GuardDuty threat detection",
                  "AWS Config compliance monitoring",
                  "KMS encryption for all supported services",
                  "Security Hub centralized security findings"
                ].map((feature, index) => (
                  <HStack key={index} spacing={2}>
                    <FaCheckCircle color="green" />
                    <Text fontSize="sm">{feature}</Text>
                  </HStack>
                ))}
              </SimpleGrid>
            </CardBody>
          </Card>
          
          <Card>
            <CardHeader>
              <HStack justify="space-between">
                <Heading size="md">Generated Infrastructure Code</Heading>
                <Button size="sm" onClick={onTerraformModalOpen}>
                  View Full Code
                </Button>
              </HStack>
            </CardHeader>
            <CardBody>
              <Code display="block" whiteSpace="pre" p={4} bg="gray.50" borderRadius="md">
                {deploymentData.terraform_code?.substring(0, 500) + '...' || 'Terraform code will be displayed here'}
              </Code>
            </CardBody>
          </Card>
          
          <HStack spacing={4} justify="center">
            <Button onClick={() => setWorkflowStep('create')}>
              Back to Edit
            </Button>
            <Button
              colorScheme="blue"
              variant="outline"
              onClick={downloadArchitectureDocument}
              leftIcon={<FaDownload />}
            >
              Download Document
            </Button>
            <Button
              colorScheme="green"
              onClick={() => handleCreateFromScratch(false)}
              isLoading={loading}
              loadingText="Deploying..."
              leftIcon={<FaRocket />}
            >
              Deploy to AWS
            </Button>
          </HStack>
        </>
      )}
    </VStack>
  );
  
  const renderImportReview = () => (
    <VStack spacing={6} align="stretch">
      {importData && (
        <>
          <Alert status="success">
            <AlertIcon />
            <Box>
              <AlertTitle>Infrastructure Imported Successfully!</AlertTitle>
              <AlertDescription>
                {importData.summary.total_resources} resources imported with security analysis
              </AlertDescription>
            </Box>
          </Alert>
          
          <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6}>
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {importData.summary.total_resources}
                </Text>
                <Text fontSize="sm" color="gray.600">Total Resources</Text>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {importData.summary.security_score}/100
                </Text>
                <Text fontSize="sm" color="gray.600">Security Score</Text>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="red.500">
                  {importData.summary.security_gaps.critical + importData.summary.security_gaps.high}
                </Text>
                <Text fontSize="sm" color="gray.600">Critical/High Issues</Text>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                  ${importData.summary.total_estimated_cost}
                </Text>
                <Text fontSize="sm" color="gray.600">Monthly Cost Est.</Text>
              </CardBody>
            </Card>
          </SimpleGrid>
          
          <Tabs>
            <TabList>
              <Tab>Security Gaps</Tab>
              <Tab>Resources</Tab>
              <Tab>Compliance</Tab>
              <Tab>Terraform Code</Tab>
            </TabList>
            
            <TabPanels>
              <TabPanel>
                <VStack spacing={4} align="stretch">
                  {importData.security_gaps.length > 0 ? (
                    <>
                      <Alert status="warning">
                        <AlertIcon />
                        <Box>
                          <AlertTitle>Security Issues Found</AlertTitle>
                          <AlertDescription>
                            {importData.security_gaps.length} security gaps identified that should be addressed
                          </AlertDescription>
                        </Box>
                      </Alert>
                      
                      <TableContainer>
                        <Table size="sm">
                          <Thead>
                            <Tr>
                              <Th>Resource</Th>
                              <Th>Issue Type</Th>
                              <Th>Severity</Th>
                              <Th>Description</Th>
                              <Th>Fix Available</Th>
                            </Tr>
                          </Thead>
                          <Tbody>
                            {importData.security_gaps.map((gap) => (
                              <Tr key={gap.gap_id}>
                                <Td>{gap.resource_id}</Td>
                                <Td>{gap.gap_type.replace('_', ' ')}</Td>
                                <Td>
                                  <Badge
                                    colorScheme={
                                      gap.severity === 'critical' ? 'red' :
                                      gap.severity === 'high' ? 'orange' :
                                      gap.severity === 'medium' ? 'yellow' : 'gray'
                                    }
                                  >
                                    {gap.severity}
                                  </Badge>
                                </Td>
                                <Td>{gap.description}</Td>
                                <Td>
                                  {gap.can_auto_fix ? (
                                    <Badge colorScheme="green">Auto-fix</Badge>
                                  ) : (
                                    <Badge colorScheme="gray">Manual</Badge>
                                  )}
                                </Td>
                              </Tr>
                            ))}
                          </Tbody>
                        </Table>
                      </TableContainer>
                      
                      <Button
                        colorScheme="red"
                        onClick={() => handleApplySecurityPolicies(
                          importData.security_gaps.filter(g => g.can_auto_fix).map(g => g.gap_id)
                        )}
                        isLoading={loading}
                        loadingText="Applying Security Fixes..."
                      >
                        Apply All Auto-Fix Security Policies
                      </Button>
                    </>
                  ) : (
                    <Alert status="success">
                      <AlertIcon />
                      <AlertTitle>No Security Issues Found</AlertTitle>
                      <AlertDescription>
                        Your infrastructure meets all security requirements
                      </AlertDescription>
                    </Alert>
                  )}
                </VStack>
              </TabPanel>
              
              <TabPanel>
                <TableContainer>
                  <Table size="sm">
                    <Thead>
                      <Tr>
                        <Th>Resource Name</Th>
                        <Th>Type</Th>
                        <Th>Region</Th>
                        <Th>Security Status</Th>
                        <Th>Monthly Cost</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {importData.imported_resources.map((resource) => (
                        <Tr key={resource.resource_id}>
                          <Td>{resource.resource_name}</Td>
                          <Td>{resource.resource_type}</Td>
                          <Td>{resource.region}</Td>
                          <Td>
                            {resource.security_compliant ? (
                              <Badge colorScheme="green">Compliant</Badge>
                            ) : (
                              <Badge colorScheme="red">
                                {resource.security_issues_count} Issues
                              </Badge>
                            )}
                          </Td>
                          <Td>${resource.estimated_monthly_cost}</Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              </TabPanel>
              
              <TabPanel>
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                  {Object.entries(importData.summary.compliance_status).map(([framework, status]) => (
                    <Card key={framework}>
                      <CardBody>
                        <VStack align="start" spacing={2}>
                          <HStack justify="space-between" width="100%">
                            <Text fontWeight="bold">{framework}</Text>
                            <Badge
                              colorScheme={status.compliant ? 'green' : 'red'}
                            >
                              {status.status}
                            </Badge>
                          </HStack>
                          <Progress 
                            value={status.score} 
                            colorScheme={status.score >= 80 ? 'green' : status.score >= 60 ? 'yellow' : 'red'}
                            width="100%"
                          />
                          <Text fontSize="sm" color="gray.600">
                            {status.score}% Compliant
                          </Text>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </SimpleGrid>
              </TabPanel>
              
              <TabPanel>
                <Card>
                  <CardHeader>
                    <HStack justify="space-between">
                      <Heading size="md">Generated Terraform Code</Heading>
                      <Button size="sm" onClick={onTerraformModalOpen}>
                        View Full Code
                      </Button>
                    </HStack>
                  </CardHeader>
                  <CardBody>
                    <Code display="block" whiteSpace="pre" p={4} bg="gray.50" borderRadius="md">
                      {importData.terraform_code?.substring(0, 1000) + '...' || 'Terraform code will be displayed here'}
                    </Code>
                  </CardBody>
                </Card>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </>
      )}
    </VStack>
  );
  
  const renderDeploymentProgress = () => (
    <VStack spacing={6} align="stretch">
      {deploymentStatus && (
        <>
          <Card>
            <CardBody>
              <VStack spacing={4}>
                <Heading size="lg" textAlign="center">
                  Deployment in Progress
                </Heading>
                
                <Progress 
                  value={deploymentStatus.progress_percentage} 
                  colorScheme="blue" 
                  size="lg" 
                  width="100%"
                />
                
                <Text fontSize="lg" fontWeight="bold">
                  {deploymentStatus.progress_percentage.toFixed(1)}% Complete
                </Text>
                
                <Text color="gray.600">
                  {deploymentStatus.current_step}
                </Text>
                
                {deploymentStatus.estimated_completion && (
                  <Text fontSize="sm" color="gray.500">
                    Estimated completion: {deploymentStatus.estimated_completion}
                  </Text>
                )}
              </VStack>
            </CardBody>
          </Card>
          
          <Card>
            <CardHeader>
              <Heading size="md">Deployment Logs</Heading>
            </CardHeader>
            <CardBody>
              <Code display="block" whiteSpace="pre-line" p={4} bg="gray.50" borderRadius="md" maxH="300px" overflowY="auto">
                {deploymentStatus.logs.join('\n')}
              </Code>
            </CardBody>
          </Card>
          
          {deploymentStatus.errors.length > 0 && (
            <Alert status="error">
              <AlertIcon />
              <Box>
                <AlertTitle>Deployment Errors</AlertTitle>
                <AlertDescription>
                  {deploymentStatus.errors.join(', ')}
                </AlertDescription>
              </Box>
            </Alert>
          )}
        </>
      )}
    </VStack>
  );
  
  const renderWorkflowStep = () => {
    switch (workflowStep) {
      case 'choose':
        return renderChooseApproach();
      case 'create':
        return renderCreateForm();
      case 'import':
        return renderImportForm();
      case 'review':
        return renderDeploymentReview();
      case 'import-review':
        return renderImportReview();
      case 'deploy':
        return renderDeploymentProgress();
      case 'complete':
        return (
          <VStack spacing={6}>
            <Alert status="success">
              <AlertIcon />
              <Box>
                <AlertTitle>Deployment Complete!</AlertTitle>
                <AlertDescription>
                  Your AWS infrastructure has been successfully deployed with full security policies
                </AlertDescription>
              </Box>
            </Alert>
            
            <HStack spacing={4}>
              <Button colorScheme="blue" onClick={() => navigate('/dashboard')}>
                View Dashboard
              </Button>
              <Button onClick={() => setWorkflowStep('choose')}>
                Start New Project
              </Button>
            </HStack>
          </VStack>
        );
      default:
        return renderChooseApproach();
    }
  };
  
  return (
    <Box p={8} maxW="1200px" mx="auto">
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="xl" mb={2}>
            Production AWS Architecture Generator
          </Heading>
          <Text color="gray.600" fontSize="lg">  
            Deploy production-ready AWS infrastructure with comprehensive security policies
          </Text>
        </Box>
        
        {/* Workflow Progress */}
        <Card>
          <CardBody>
            <HStack spacing={4} justify="center">
              {workflowSteps.map((step, index) => (
                <React.Fragment key={step.id}>
                  <VStack spacing={2}>
                    <Box
                      p={3}
                      borderRadius="full"
                      bg={
                        workflowStep === step.id ? 'blue.500' :
                        ['review', 'import-review', 'deploy', 'complete'].includes(workflowStep) && index <= 2 ? 'green.500' :
                        'gray.200'
                      }
                      color={
                        workflowStep === step.id || (['review', 'import-review', 'deploy', 'complete'].includes(workflowStep) && index <= 2) ? 'white' : 'gray.500'
                      }
                    >
                      <step.icon />
                    </Box>
                    <Text fontSize="sm" fontWeight="bold" textAlign="center">
                      {step.title}
                    </Text>
                  </VStack>
                  {index < workflowSteps.length - 1 && (
                    <Box flex={1} height="2px" bg="gray.200" />
                  )}
                </React.Fragment>
              ))}
            </HStack>
          </CardBody>
        </Card>
        
        {/* Main Content */}
        {renderWorkflowStep()}
      </VStack>
      
      {/* Terraform Code Modal */}
      <Modal isOpen={isTerraformModalOpen} onClose={onTerraformModalClose} size="6xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Generated Infrastructure Code</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <Code display="block" whiteSpace="pre" p={4} bg="gray.50" borderRadius="md" maxH="500px" overflowY="auto">
              {(deploymentData?.terraform_code || importData?.terraform_code) || 'No code available'}
            </Code>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default ProductionArchitectureWorkflow;