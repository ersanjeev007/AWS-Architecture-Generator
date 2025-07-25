import React from 'react';
import {
  Box,
  Container,
  VStack,
  Heading,
  Text,
  Button,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Collapse,
  useDisclosure,
  Icon,
} from '@chakra-ui/react';
import { FaExclamationTriangle, FaRedo, FaHome } from 'react-icons/fa';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // You can log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <Container maxW="2xl" py={20}>
          <VStack spacing={8} textAlign="center">
            <Icon as={FaExclamationTriangle} boxSize={16} color="red.500" />
            
            <VStack spacing={4}>
              <Heading size="xl" color="red.600">
                Oops! Something went wrong
              </Heading>
              <Text fontSize="lg" color="gray.600">
                We're sorry, but something unexpected happened. Our team has been notified.
              </Text>
            </VStack>

            <Alert status="error" borderRadius="lg" maxW="md">
              <AlertIcon />
              <Box>
                <AlertTitle>Application Error</AlertTitle>
                <AlertDescription>
                  The application encountered an unexpected error and needs to be reloaded.
                </AlertDescription>
              </Box>
            </Alert>

            <VStack spacing={4}>
              <Button
                colorScheme="blue"
                size="lg"
                leftIcon={<FaRedo />}
                onClick={this.handleReload}
              >
                Reload Application
              </Button>
              
              <Button
                variant="outline"
                leftIcon={<FaHome />}
                onClick={this.handleGoHome}
              >
                Go to Homepage
              </Button>
            </VStack>

            {/* Developer Error Details */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <ErrorDetails
                error={this.state.error}
                errorInfo={this.state.errorInfo}
              />
            )}
          </VStack>
        </Container>
      );
    }

    return this.props.children;
  }
}

// Developer error details component (only shows in development)
const ErrorDetails = ({ error, errorInfo }) => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <Box w="full" maxW="2xl">
      <Button
        variant="ghost"
        size="sm"
        onClick={onToggle}
        color="gray.600"
      >
        {isOpen ? 'Hide' : 'Show'} Error Details
      </Button>
      
      <Collapse in={isOpen} animateOpacity>
        <Box mt={4} p={4} bg="red.50" borderRadius="md" border="1px" borderColor="red.200">
          <VStack align="stretch" spacing={4}>
            <Box>
              <Text fontWeight="bold" color="red.700" mb={2}>
                Error Message:
              </Text>
              <Code colorScheme="red" p={2} borderRadius="md" w="full" fontSize="sm">
                {error.toString()}
              </Code>
            </Box>
            
            {errorInfo && (
              <Box>
                <Text fontWeight="bold" color="red.700" mb={2}>
                  Component Stack:
                </Text>
                <Code colorScheme="red" p={2} borderRadius="md" w="full" fontSize="xs" whiteSpace="pre-wrap">
                  {errorInfo.componentStack}
                </Code>
              </Box>
            )}
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
};

export default ErrorBoundary;