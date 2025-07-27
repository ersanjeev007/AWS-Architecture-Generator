import React, { useState } from 'react';
import {
  Box,
  Flex,
  VStack,
  HStack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  Alert,
  AlertIcon,
  AlertDescription,
  Card,
  CardBody,
  CardHeader,
  Link,
  Divider,
  useToast,
  InputGroup,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { FaAws } from 'react-icons/fa';
import { Link as RouterLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import { extractErrorMessage } from '../../utils/errorUtils';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  
  const from = location.state?.from?.pathname || '/';

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(formData.username, formData.password);
      toast({
        title: 'Login Successful',
        description: 'Welcome back!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate(from, { replace: true });
    } catch (err) {
      setError(extractErrorMessage(err, 'Login failed. Please check your credentials.'));
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setFormData({ username: 'demo', password: 'demo' });
    setLoading(true);
    
    try {
      await login('demo', 'demo');
      toast({
        title: 'Demo Login Successful',
        description: 'Welcome to the demo!',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      navigate(from, { replace: true });
    } catch (err) {
      setError('Demo login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Flex
      minH="100vh"
      align="center"
      justify="center"
      bg="gray.50"
      py={12}
      px={6}
    >
      <VStack spacing={8} w="full" maxW="md">
        {/* Logo and Header */}
        <VStack spacing={4}>
          <Box
            w="80px"
            h="80px"
            bg="blue.500"
            borderRadius="xl"
            display="flex"
            alignItems="center"
            justifyContent="center"
            shadow="lg"
          >
            <FaAws color="white" size="36px" />
          </Box>
          <VStack spacing={2}>
            <Heading size="xl" color="gray.800">
              AWS Architecture Generator
            </Heading>
            <Text color="gray.600" fontSize="lg">
              Sign in to your account
            </Text>
          </VStack>
        </VStack>

        {/* Login Form */}
        <Card w="full" shadow="xl">
          <CardHeader pb={2}>
            <Heading size="md" textAlign="center" color="gray.700">
              Welcome Back
            </Heading>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit}>
              <VStack spacing={5}>
                {error && (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    <AlertDescription>{typeof error === 'string' ? error : extractErrorMessage(error, 'Login failed')}</AlertDescription>
                  </Alert>
                )}

                <FormControl isRequired>
                  <FormLabel>Username</FormLabel>
                  <Input
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username"
                    size="lg"
                    bg="white"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <InputGroup size="lg">
                    <Input
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter your password"
                      bg="white"
                    />
                    <InputRightElement>
                      <IconButton
                        variant="ghost"
                        icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                        onClick={() => setShowPassword(!showPassword)}
                        aria-label="Toggle password visibility"
                      />
                    </InputRightElement>
                  </InputGroup>
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  size="lg"
                  w="full"
                  isLoading={loading}
                  loadingText="Signing in..."
                >
                  Sign In
                </Button>
              </VStack>
            </form>
          </CardBody>
        </Card>

        {/* Register Link */}
        <Text color="gray.600">
          Don't have an account?{' '}
          <Link as={RouterLink} to="/register" color="blue.500" fontWeight="medium">
            Create one here
          </Link>
        </Text>

        {/* Features Highlight */}
        <Card w="full" variant="outline">
          <CardBody>
            <VStack spacing={3}>
              <Heading size="sm" color="gray.700">
                Features
              </Heading>
              <VStack spacing={2} fontSize="sm" color="gray.600">
                <HStack>
                  <Text>✨ AI-Powered Security Recommendations</Text>
                </HStack>
                <HStack>
                  <Text>💰 Real-time AWS Cost Analysis</Text>
                </HStack>
                <HStack>
                  <Text>🏗️ Infrastructure as Code Generation</Text>
                </HStack>
                <HStack>
                  <Text>⚡ One-Click Deployment</Text>
                </HStack>
              </VStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Flex>
  );
};

export default LoginPage;