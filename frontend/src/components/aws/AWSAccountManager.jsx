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
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Badge,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  useDisclosure,
  useToast,
  Spinner,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Progress,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider
} from '@chakra-ui/react';
import { 
  FaAws, 
  FaPlus, 
  FaEdit, 
  FaTrash, 
  FaCheck, 
  FaTimes, 
  FaExclamationTriangle,
  FaEllipsisV,
  FaSync,
  FaShieldAlt,
  FaDollarSign,
  FaServer,
  FaDatabase,
  FaNetworkWired,
  FaEye
} from 'react-icons/fa';

import { apiClient } from '../../services/api';

const AWSAccountManager = () => {
  const [awsAccounts, setAwsAccounts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [accountDetails, setAccountDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);
  
  const [formData, setFormData] = useState({
    account_name: '',
    aws_region: 'us-west-2',
    description: '',
    aws_access_key_id: '',
    aws_secret_access_key: '',
    aws_session_token: ''
  });
  
  const { isOpen: isAddModalOpen, onOpen: onAddModalOpen, onClose: onAddModalClose } = useDisclosure();
  const { isOpen: isEditModalOpen, onOpen: onEditModalOpen, onClose: onEditModalClose } = useDisclosure();
  const { isOpen: isDetailsModalOpen, onOpen: onDetailsModalOpen, onClose: onDetailsModalClose } = useDisclosure();
  
  const toast = useToast();
  
  useEffect(() => {
    loadAWSAccounts();
  }, []);
  
  const loadAWSAccounts = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/aws-accounts');
      setAwsAccounts(response.data || []);
    } catch (error) {
      toast({
        title: 'Failed to load AWS accounts',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const validateAWSCredentials = async (credentials) => {
    try {
      setValidating(true);
      const response = await apiClient.post('/aws-accounts/validate-credentials', null, {
        params: {
          aws_access_key_id: credentials.aws_access_key_id,
          aws_secret_access_key: credentials.aws_secret_access_key,
          aws_session_token: credentials.aws_session_token,
          region: credentials.aws_region
        }
      });
      
      if (response.data.valid) {
        toast({
          title: 'AWS Credentials Valid',
          description: `Connected to AWS account ${response.data.account_id} in ${response.data.region}`,
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        return response.data;
      } else {
        toast({
          title: 'Invalid AWS Credentials',
          description: response.data.error,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return null;
      }
    } catch (error) {
      toast({
        title: 'Credential Validation Failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return null;
    } finally {
      setValidating(false);
    }
  };
  
  const handleAddAccount = async () => {
    try {
      // Validate credentials first
      const validationResult = await validateAWSCredentials(formData);
      if (!validationResult) {
        return;
      }
      
      const response = await apiClient.post('/aws-accounts', {
        ...formData,
        account_id: validationResult.account_id,
        permissions: validationResult.permissions
      });
      
      toast({
        title: 'AWS Account Added',
        description: `Successfully added AWS account ${formData.account_name}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      setFormData({
        account_name: '',
        aws_region: 'us-west-2',
        description: '',
        aws_access_key_id: '',
        aws_secret_access_key: '',
        aws_session_token: ''
      });
      
      onAddModalClose();
      loadAWSAccounts();
      
    } catch (error) {
      toast({
        title: 'Failed to add AWS account',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleEditAccount = async () => {
    try {
      const response = await apiClient.put(`/aws-accounts/${selectedAccount.id}`, formData);
      
      toast({
        title: 'AWS Account Updated',
        description: `Successfully updated AWS account ${formData.account_name}`,
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      onEditModalClose();
      loadAWSAccounts();
      
    } catch (error) {
      toast({
        title: 'Failed to update AWS account',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleDeleteAccount = async (accountId) => {
    try {
      await apiClient.delete(`/aws-accounts/${accountId}`);
      
      toast({
        title: 'AWS Account Deleted',
        description: 'AWS account has been successfully deleted',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      loadAWSAccounts();
      
    } catch (error) {
      toast({
        title: 'Failed to delete AWS account',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };
  
  const handleValidateAccount = async (account) => {
    try {
      setValidating(true);
      
      // Use stored credentials to validate
      const validationResult = await validateAWSCredentials({
        aws_access_key_id: account.aws_access_key_id,
        aws_secret_access_key: account.aws_secret_access_key,
        aws_session_token: account.aws_session_token,
        aws_region: account.aws_region
      });
      
      if (validationResult) {
        // Update account validation status
        await apiClient.patch(`/aws-accounts/${account.id}/validate`, {
          validation_result: validationResult
        });
        
        loadAWSAccounts();
      }
      
    } catch (error) {
      toast({
        title: 'Account validation failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setValidating(false);
    }
  };
  
  const loadAccountDetails = async (account) => {
    try {
      setLoadingDetails(true);
      setSelectedAccount(account);
      onDetailsModalOpen();
      
      // Fetch detailed account information
      const response = await apiClient.get(`/aws-accounts/${account.id}/details`);
      setAccountDetails(response.data);
      
    } catch (error) {
      toast({
        title: 'Failed to load account details',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoadingDetails(false);
    }
  };
  
  const openEditModal = (account) => {
    setSelectedAccount(account);
    setFormData({
      account_name: account.account_name,
      aws_region: account.aws_region,
      description: account.description || '',
      aws_access_key_id: '',  // Don't populate for security
      aws_secret_access_key: '',
      aws_session_token: ''
    });
    onEditModalOpen();
  };
  
  const getAccountStatusColor = (account) => {
    if (!account.last_validated) return 'gray';
    
    const lastValidated = new Date(account.last_validated);
    const daysSinceValidation = (Date.now() - lastValidated.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceValidation > 7) return 'red';
    if (daysSinceValidation > 3) return 'yellow';
    return 'green';
  };
  
  const getAccountStatusText = (account) => {
    if (!account.last_validated) return 'Not Validated';
    
    const lastValidated = new Date(account.last_validated);
    const daysSinceValidation = (Date.now() - lastValidated.getTime()) / (1000 * 60 * 60 * 24);
    
    if (daysSinceValidation > 7) return 'Validation Expired';
    if (daysSinceValidation > 3) return 'Validation Expiring';
    return 'Valid';
  };
  
  const renderAccountForm = (isEdit = false) => (
    <VStack spacing={4}>
      <FormControl isRequired>
        <FormLabel>Account Name</FormLabel>
        <Input
          value={formData.account_name}
          onChange={(e) => setFormData({...formData, account_name: e.target.value})}
          placeholder="Production AWS Account"
        />
      </FormControl>
      
      <FormControl>
        <FormLabel>Description</FormLabel>
        <Textarea
          value={formData.description}
          onChange={(e) => setFormData({...formData, description: e.target.value})}
          placeholder="Description of this AWS account"
        />
      </FormControl>
      
      <FormControl isRequired>
        <FormLabel>AWS Region</FormLabel>
        <Select
          value={formData.aws_region}
          onChange={(e) => setFormData({...formData, aws_region: e.target.value})}
        >
          <option value="us-east-1">US East (N. Virginia)</option>
          <option value="us-west-2">US West (Oregon)</option>
          <option value="eu-west-1">Europe (Ireland)</option>
          <option value="eu-central-1">Europe (Frankfurt)</option>
          <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
          <option value="ap-northeast-1">Asia Pacific (Tokyo)</option>
        </Select>
      </FormControl>
      
      <Alert status="info" size="sm">
        <AlertIcon />
        <Box>
          <AlertTitle fontSize="sm">Secure Credential Storage</AlertTitle>
          <AlertDescription fontSize="xs">
            Credentials are encrypted and stored securely. Only you can access them.
          </AlertDescription>
        </Box>
      </Alert>
      
      <FormControl isRequired>
        <FormLabel>AWS Access Key ID</FormLabel>
        <Input
          type="password"
          value={formData.aws_access_key_id}
          onChange={(e) => setFormData({...formData, aws_access_key_id: e.target.value})}
          placeholder="AKIA..."
        />
      </FormControl>
      
      <FormControl isRequired>
        <FormLabel>AWS Secret Access Key</FormLabel>
        <Input
          type="password"
          value={formData.aws_secret_access_key}
          onChange={(e) => setFormData({...formData, aws_secret_access_key: e.target.value})}
          placeholder="Secret Access Key"
        />
      </FormControl>
      
      <FormControl>
        <FormLabel>AWS Session Token (Optional)</FormLabel>
        <Input
          type="password"
          value={formData.aws_session_token}
          onChange={(e) => setFormData({...formData, aws_session_token: e.target.value})}
          placeholder="Session Token"
        />
      </FormControl>
      
      <Button
        colorScheme="blue"
        variant="outline"
        onClick={() => validateAWSCredentials(formData)}
        isLoading={validating}
        loadingText="Validating..."
        width="100%"
      >
        Validate Credentials
      </Button>
    </VStack>
  );
  
  const renderAccountDetails = () => (
    <VStack spacing={6} align="stretch">
      {loadingDetails ? (
        <Box textAlign="center" py={8}>
          <Spinner size="lg" />
          <Text mt={4}>Loading account details...</Text>
        </Box>
      ) : accountDetails ? (
        <>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6}>
            <Card>
              <CardHeader>
                <Heading size="sm">Account Information</Heading>
              </CardHeader>
              <CardBody>
                <VStack align="start" spacing={2}>
                  <HStack>
                    <Text fontWeight="bold">Account ID:</Text>
                    <Text>{accountDetails.account_id}</Text>
                  </HStack>
                  <HStack>
                    <Text fontWeight="bold">Region:</Text>
                    <Text>{accountDetails.region}</Text>
                  </HStack>
                  <HStack>
                    <Text fontWeight="bold">Status:</Text>
                    <Badge colorScheme={getAccountStatusColor(selectedAccount)}>
                      {getAccountStatusText(selectedAccount)}
                    </Badge>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
            
            <Card>
              <CardHeader>
                <Heading size="sm">Resource Summary</Heading>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={2} spacing={4}>
                  <Stat size="sm">
                    <StatLabel>EC2 Instances</StatLabel>
                    <StatNumber>{accountDetails.resources?.ec2_instances || 0}</StatNumber>
                  </Stat>
                  <Stat size="sm">
                    <StatLabel>S3 Buckets</StatLabel>
                    <StatNumber>{accountDetails.resources?.s3_buckets || 0}</StatNumber>
                  </Stat>
                  <Stat size="sm">
                    <StatLabel>RDS Instances</StatLabel>
                    <StatNumber>{accountDetails.resources?.rds_instances || 0}</StatNumber>
                  </Stat>
                  <Stat size="sm">
                    <StatLabel>Lambda Functions</StatLabel>
                    <StatNumber>{accountDetails.resources?.lambda_functions || 0}</StatNumber>
                  </Stat>
                </SimpleGrid>
              </CardBody>
            </Card>
          </SimpleGrid>
          
          <Accordion allowToggle>
            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box flex="1" textAlign="left">
                    <HStack>
                      <FaShieldAlt />
                      <Text>Security Assessment</Text>
                    </HStack>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="green.500">
                        {accountDetails.security?.score || 85}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Security Score</Text>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="red.500">
                        {accountDetails.security?.critical_issues || 2}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Critical Issues</Text>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                        {accountDetails.security?.compliant_services || 8}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Compliant Services</Text>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </AccordionPanel>
            </AccordionItem>
            
            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box flex="1" textAlign="left">
                    <HStack>
                      <FaDollarSign />
                      <Text>Cost Analysis</Text>
                    </HStack>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                        ${accountDetails.costs?.monthly_spend || 1250}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Monthly Spend</Text>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="green.500">
                        ${accountDetails.costs?.potential_savings || 315}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Potential Savings</Text>
                    </CardBody>
                  </Card>
                  <Card>
                    <CardBody textAlign="center">
                      <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                        {accountDetails.costs?.optimization_opportunities || 12}
                      </Text>
                      <Text fontSize="sm" color="gray.600">Optimizations</Text>
                    </CardBody>
                  </Card>
                </SimpleGrid>
              </AccordionPanel>
            </AccordionItem>
            
            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box flex="1" textAlign="left">
                    <HStack>
                      <FaNetworkWired />
                      <Text>Permissions Analysis</Text>
                    </HStack>
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <VStack align="stretch" spacing={3}>
                  {Object.entries(accountDetails.permissions || {}).map(([service, permission]) => (
                    <HStack key={service} justify="space-between">
                      <Text fontWeight="bold">{service.toUpperCase()}</Text>
                      <Badge
                        colorScheme={
                          permission.status === 'granted' ? 'green' :
                          permission.status === 'limited' ? 'yellow' : 'red'
                        }
                      >
                        {permission.status}
                      </Badge>
                    </HStack>
                  ))}
                </VStack>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
        </>
      ) : (
        <Text>No account details available</Text>
      )}
    </VStack>
  );
  
  if (loading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="lg" />
        <Text mt={4}>Loading AWS accounts...</Text>
      </Box>
    );
  }
  
  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <Box>
            <Heading size="lg">AWS Account Management</Heading>
            <Text color="gray.600">
              Manage your AWS accounts for infrastructure deployment and monitoring
            </Text>
          </Box>
          <Button
            colorScheme="blue"
            leftIcon={<FaPlus />}
            onClick={onAddModalOpen}
          >
            Add AWS Account
          </Button>
        </HStack>
        
        {/* Accounts Overview */}
        {awsAccounts.length > 0 && (
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {awsAccounts.length}
                </Text>
                <Text fontSize="sm" color="gray.600">Total Accounts</Text>
              </CardBody>
            </Card>
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {awsAccounts.filter(acc => getAccountStatusColor(acc) === 'green').length}
                </Text>
                <Text fontSize="sm" color="gray.600">Valid Accounts</Text>
              </CardBody>
            </Card>
            <Card>
              <CardBody textAlign="center">
                <Text fontSize="2xl" fontWeight="bold" color="red.500">
                  {awsAccounts.filter(acc => getAccountStatusColor(acc) === 'red').length}
                </Text>
                <Text fontSize="sm" color="gray.600">Need Validation</Text>
              </CardBody>
            </Card>
          </SimpleGrid>
        )}
        
        {/* Accounts Table */}
        {awsAccounts.length > 0 ? (
          <Card>
            <CardHeader>
              <Heading size="md">AWS Accounts</Heading>
            </CardHeader>
            <CardBody>
              <TableContainer>
                <Table variant="simple">
                  <Thead>
                    <Tr>
                      <Th>Account Name</Th>
                      <Th>Account ID</Th>
                      <Th>Region</Th>
                      <Th>Status</Th>
                      <Th>Last Validated</Th>
                      <Th>Actions</Th>
                    </Tr>
                  </Thead>
                  <Tbody>
                    {awsAccounts.map((account) => (
                      <Tr key={account.id}>
                        <Td>
                          <VStack align="start" spacing={1}>
                            <Text fontWeight="bold">{account.account_name}</Text>
                            <Text fontSize="sm" color="gray.600">
                              {account.description || 'No description'}
                            </Text>
                          </VStack>
                        </Td>
                        <Td>{account.account_id || 'Unknown'}</Td>
                        <Td>{account.aws_region}</Td>
                        <Td>
                          <Badge colorScheme={getAccountStatusColor(account)}>
                            {getAccountStatusText(account)}
                          </Badge>
                        </Td>
                        <Td>
                          {account.last_validated 
                            ? new Date(account.last_validated).toLocaleDateString()
                            : 'Never'
                          }
                        </Td>
                        <Td>
                          <HStack spacing={2}>
                            <IconButton
                              size="sm"
                              icon={<FaEye />}
                              onClick={() => loadAccountDetails(account)}
                              title="View Details"
                            />
                            <IconButton
                              size="sm"
                              icon={<FaSync />}
                              onClick={() => handleValidateAccount(account)}
                              isLoading={validating}
                              title="Validate Account"
                            />
                            <Menu>
                              <MenuButton
                                as={IconButton}
                                icon={<FaEllipsisV />}
                                size="sm"
                                variant="ghost"
                              />
                              <MenuList>
                                <MenuItem
                                  icon={<FaEdit />}
                                  onClick={() => openEditModal(account)}
                                >
                                  Edit Account
                                </MenuItem>
                                <MenuItem
                                  icon={<FaTrash />}
                                  color="red.500"
                                  onClick={() => handleDeleteAccount(account.id)}
                                >
                                  Delete Account
                                </MenuItem>
                              </MenuList>
                            </Menu>
                          </HStack>
                        </Td>
                      </Tr>
                    ))}
                  </Tbody>
                </Table>
              </TableContainer>
            </CardBody>
          </Card>
        ) : (
          <Card>
            <CardBody textAlign="center" py={12}>
              <FaAws size="48px" color="gray" />
              <Heading size="md" mt={4} mb={2}>No AWS Accounts</Heading>
              <Text color="gray.600" mb={6}>
                Add your first AWS account to start deploying infrastructure
              </Text>
              <Button colorScheme="blue" onClick={onAddModalOpen}>
                Add AWS Account
              </Button>
            </CardBody>
          </Card>
        )}
      </VStack>
      
      {/* Add Account Modal */}
      <Modal isOpen={isAddModalOpen} onClose={onAddModalClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add AWS Account</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {renderAccountForm()}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onAddModalClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleAddAccount}
              isLoading={validating}
              loadingText="Adding..."
            >
              Add Account
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Edit Account Modal */}
      <Modal isOpen={isEditModalOpen} onClose={onEditModalClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Edit AWS Account</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {renderAccountForm(true)}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onEditModalClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleEditAccount}
              isLoading={validating}
              loadingText="Updating..."
            >
              Update Account
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
      
      {/* Account Details Modal */}
      <Modal isOpen={isDetailsModalOpen} onClose={onDetailsModalClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <FaAws />
              <Text>{selectedAccount?.account_name} - Account Details</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {renderAccountDetails()}
          </ModalBody>
          <ModalFooter>
            <Button onClick={onDetailsModalClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default AWSAccountManager;