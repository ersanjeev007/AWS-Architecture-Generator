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
  Card,
  CardBody,
  CardHeader,
  Link,
  useToast,
  InputGroup,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';
import { FaAws } from 'react-icons/fa';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    confirmPassword: '',
    email: '',
    full_name: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

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

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 4) {
      setError('Password must be at least 4 characters long');
      setLoading(false);
      return;
    }

    try {
      await register({
        username: formData.username,
        password: formData.password,
        email: formData.email || null,
        full_name: formData.full_name || null,
      });
      
      toast({
        title: 'Registration Successful',
        description: 'Your account has been created. Please login.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Registration failed. Please try again.');
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
              Create Account
            </Heading>
            <Text color="gray.600" fontSize="lg">
              Join the AWS Architecture Generator
            </Text>
          </VStack>
        </VStack>

        {/* Registration Form */}
        <Card w="full" shadow="xl">
          <CardHeader pb={2}>
            <Heading size="md" textAlign="center" color="gray.700">
              Sign Up
            </Heading>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleSubmit}>
              <VStack spacing={4}>
                {error && (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    {error}
                  </Alert>
                )}

                <FormControl isRequired>
                  <FormLabel>Username</FormLabel>
                  <Input
                    name="username"
                    type="text"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Choose a username"
                    bg="white"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Full Name</FormLabel>
                  <Input
                    name="full_name"
                    type="text"
                    value={formData.full_name}
                    onChange={handleChange}
                    placeholder="Your full name (optional)"
                    bg="white"
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Email</FormLabel>
                  <Input
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="your.email@example.com (optional)"
                    bg="white"
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <InputGroup>
                    <Input
                      name="password"
                      type={showPassword ? 'text' : 'password'}
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Create a password"
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

                <FormControl isRequired>
                  <FormLabel>Confirm Password</FormLabel>
                  <InputGroup>
                    <Input
                      name="confirmPassword"
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Confirm your password"
                      bg="white"
                    />
                    <InputRightElement>
                      <IconButton
                        variant="ghost"
                        icon={showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        aria-label="Toggle confirm password visibility"
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
                  loadingText="Creating account..."
                >
                  Create Account
                </Button>
              </VStack>
            </form>
          </CardBody>
        </Card>

        {/* Login Link */}
        <Text color="gray.600">
          Already have an account?{' '}
          <Link as={RouterLink} to="/login" color="blue.500" fontWeight="medium">
            Sign in here
          </Link>
        </Text>
      </VStack>
    </Flex>
  );
};

export default RegisterPage;