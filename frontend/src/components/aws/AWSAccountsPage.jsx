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
  Icon,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  AlertDescription,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  InputGroup,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react';
import { 
  FaPlus, 
  FaAws, 
  FaCheck, 
  FaTimes, 
  FaEdit, 
  FaTrash, 
  FaEye, 
  FaEyeSlash,
  FaSync,
  FaClock,
  FaExclamationTriangle
} from 'react-icons/fa';
import { awsAccountService } from '../../services/awsAccountService';

const AWSAccountsPage = () => {
  const toast = useToast();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [accounts, setAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    account_name: '',
    aws_region: 'us-west-2',
    description: '',
    aws_access_key_id: '',
    aws_secret_access_key: '',
    aws_session_token: ''
  });
  const [showSecrets, setShowSecrets] = useState({
    access_key: false,
    secret_key: false,
    session_token: false
  });
  const [submitting, setSubmitting] = useState(false);
  const [validatingAccount, setValidatingAccount] = useState(null);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      setError(null);
      const accountsData = await awsAccountService.listAccounts();
      setAccounts(accountsData);
    } catch (err) {
      setError(err.message);
      toast({
        title: 'Failed to Load Accounts',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!formData.account_name || !formData.aws_access_key_id || !formData.aws_secret_access_key) {
      toast({
        title: 'Validation Error',
        description: 'Please fill in all required fields',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setSubmitting(true);
      await awsAccountService.createAccount(formData);
      
      toast({
        title: 'Account Added Successfully',
        description: 'AWS account has been added and validated',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Reset form and close modal
      setFormData({
        account_name: '',
        aws_region: 'us-west-2',
        description: '',
        aws_access_key_id: '',
        aws_secret_access_key: '',
        aws_session_token: ''
      });
      onClose();
      
      // Reload accounts
      await loadAccounts();
      
    } catch (err) {
      toast({
        title: 'Failed to Add Account',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const handleValidateAccount = async (accountId) => {
    try {
      setValidatingAccount(accountId);
      const result = await awsAccountService.validateAccount(accountId);
      
      toast({
        title: 'Validation Complete',
        description: result.message,
        status: result.is_valid ? 'success' : 'error',
        duration: 3000,
        isClosable: true,
      });

      // Reload accounts to get updated status
      await loadAccounts();
      
    } catch (err) {
      toast({
        title: 'Validation Failed',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setValidatingAccount(null);
    }
  };

  const handleDeleteAccount = async (accountId, accountName) => {
    if (!window.confirm(`Are you sure you want to delete the AWS account "${accountName}"?`)) {
      return;
    }

    try {
      await awsAccountService.deleteAccount(accountId);
      
      toast({
        title: 'Account Deleted',
        description: 'AWS account has been deleted successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });

      // Reload accounts
      await loadAccounts();
      
    } catch (err) {
      toast({
        title: 'Failed to Delete Account',
        description: err.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const toggleSecretVisibility = (field) => {
    setShowSecrets(prev => ({
      ...prev,
      [field]: !prev[field]
    }));
  };

  if (loading) {
    return (
      <Box textAlign="center" py={20}>
        <VStack spacing={6}>
          <Spinner size="xl" color="orange.500" thickness="4px" />
          <VStack spacing={2}>
            <Heading size="lg" color="gray.700">
              Loading AWS Accounts
            </Heading>
            <Text color="gray.600">
              Retrieving your configured AWS accounts...
            </Text>
          </VStack>
        </VStack>
      </Box>
    );
  }

  return (
    <Box maxW="7xl" mx="auto" p={6}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Card shadow="lg">
          <CardHeader>
            <HStack justify="space-between" align="start">
              <VStack align="start" spacing={2}>
                <Heading size="xl" color="gray.800">
                  AWS Accounts Configuration
                </Heading>
                <Text color="gray.600">
                  Manage your AWS accounts for infrastructure deployment
                </Text>
              </VStack>
              <Button
                leftIcon={<FaPlus />}
                colorScheme="orange"
                onClick={onOpen}
              >
                Add AWS Account
              </Button>
            </HStack>
          </CardHeader>
        </Card>

        {/* Error Display */}
        {error && (
          <Alert status="error" borderRadius="lg">
            <AlertIcon />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Accounts Grid */}
        {accounts.length === 0 ? (
          <Card shadow="lg">
            <CardBody textAlign="center" py={20}>
              <VStack spacing={4}>
                <Icon as={FaAws} boxSize={12} color="gray.300" />
                <VStack spacing={2}>
                  <Heading size="md" color="gray.500">
                    No AWS Accounts Configured
                  </Heading>
                  <Text color="gray.400">
                    Add your first AWS account to start deploying infrastructure
                  </Text>
                </VStack>
                <Button
                  leftIcon={<FaPlus />}
                  colorScheme="orange"
                  onClick={onOpen}
                >
                  Add AWS Account
                </Button>
              </VStack>
            </CardBody>
          </Card>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
            {accounts.map((account) => (
              <Card key={account.id} shadow="lg" borderRadius="lg">
                <CardHeader>
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1}>
                      <Heading size="md" color="gray.800">
                        {account.account_name}
                      </Heading>
                      <HStack>
                        {account.is_active ? (
                          <Badge colorScheme="green" variant="subtle">
                            <HStack spacing={1}>
                              <FaCheck size={10} />
                              <Text>Active</Text>
                            </HStack>
                          </Badge>
                        ) : (
                          <Badge colorScheme="red" variant="subtle">
                            <HStack spacing={1}>
                              <FaTimes size={10} />
                              <Text>Inactive</Text>
                            </HStack>
                          </Badge>
                        )}
                        <Badge colorScheme="blue" variant="outline">
                          {account.aws_region}
                        </Badge>
                      </HStack>
                    </VStack>
                    <Icon as={FaAws} color="orange.500" boxSize={6} />
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4} align="stretch">
                    {account.description && (
                      <Text fontSize="sm" color="gray.600">
                        {account.description}
                      </Text>
                    )}
                    
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>
                        Last Validated
                      </Text>
                      <HStack>
                        <Icon as={FaClock} color="gray.400" size={12} />
                        <Text fontSize="sm" color="gray.600">
                          {formatDate(account.last_validated)}
                        </Text>
                      </HStack>
                    </Box>

                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        variant="outline"
                        leftIcon={<FaSync />}
                        onClick={() => handleValidateAccount(account.id)}
                        isLoading={validatingAccount === account.id}
                        loadingText="Validating..."
                        flex={1}
                      >
                        Validate
                      </Button>
                      <IconButton
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        icon={<FaTrash />}
                        onClick={() => handleDeleteAccount(account.id, account.account_name)}
                        aria-label="Delete account"
                      />
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}

        {/* Add Account Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Add AWS Account</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <Alert status="warning" borderRadius="md">
                  <AlertIcon />
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" fontWeight="semibold">
                      Security Notice
                    </Text>
                    <Text fontSize="xs">
                      Your AWS credentials will be encrypted and stored securely. 
                      Use IAM users with minimal required permissions for deployment.
                    </Text>
                  </VStack>
                </Alert>

                <FormControl isRequired>
                  <FormLabel>Account Name</FormLabel>
                  <Input
                    placeholder="My AWS Account"
                    value={formData.account_name}
                    onChange={(e) => setFormData({...formData, account_name: e.target.value})}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>AWS Region</FormLabel>
                  <Select
                    value={formData.aws_region}
                    onChange={(e) => setFormData({...formData, aws_region: e.target.value})}
                  >
                    <option value="us-east-1">US East (N. Virginia)</option>
                    <option value="us-east-2">US East (Ohio)</option>
                    <option value="us-west-1">US West (N. California)</option>
                    <option value="us-west-2">US West (Oregon)</option>
                    <option value="eu-west-1">Europe (Ireland)</option>
                    <option value="eu-west-2">Europe (London)</option>
                    <option value="eu-central-1">Europe (Frankfurt)</option>
                    <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                    <option value="ap-southeast-2">Asia Pacific (Sydney)</option>
                    <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Description</FormLabel>
                  <Textarea
                    placeholder="Optional description for this account"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    rows={2}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>AWS Access Key ID</FormLabel>
                  <InputGroup>
                    <Input
                      type={showSecrets.access_key ? "text" : "password"}
                      placeholder="AKIA..."
                      value={formData.aws_access_key_id}
                      onChange={(e) => setFormData({...formData, aws_access_key_id: e.target.value})}
                    />
                    <InputRightElement>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        icon={showSecrets.access_key ? <FaEyeSlash /> : <FaEye />}
                        onClick={() => toggleSecretVisibility('access_key')}
                        aria-label="Toggle visibility"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>AWS Secret Access Key</FormLabel>
                  <InputGroup>
                    <Input
                      type={showSecrets.secret_key ? "text" : "password"}
                      placeholder="Secret access key"
                      value={formData.aws_secret_access_key}
                      onChange={(e) => setFormData({...formData, aws_secret_access_key: e.target.value})}
                    />
                    <InputRightElement>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        icon={showSecrets.secret_key ? <FaEyeSlash /> : <FaEye />}
                        onClick={() => toggleSecretVisibility('secret_key')}
                        aria-label="Toggle visibility"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <FormControl>
                  <FormLabel>AWS Session Token (Optional)</FormLabel>
                  <InputGroup>
                    <Input
                      type={showSecrets.session_token ? "text" : "password"}
                      placeholder="Session token for temporary credentials"
                      value={formData.aws_session_token}
                      onChange={(e) => setFormData({...formData, aws_session_token: e.target.value})}
                    />
                    <InputRightElement>
                      <IconButton
                        variant="ghost"
                        size="sm"
                        icon={showSecrets.session_token ? <FaEyeSlash /> : <FaEye />}
                        onClick={() => toggleSecretVisibility('session_token')}
                        aria-label="Toggle visibility"
                      />
                    </InputRightElement>
                  </InputGroup>
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    Only required for temporary credentials from AWS STS
                  </Text>
                </FormControl>
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button 
                colorScheme="orange" 
                onClick={handleSubmit}
                isLoading={submitting}
                loadingText="Adding Account..."
              >
                Add Account
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default AWSAccountsPage;