import React from 'react';
import {
  Box,
  Container,
  Flex,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  useColorModeValue,
  Icon,
  Spacer,
} from '@chakra-ui/react';
import { Link, useLocation } from 'react-router-dom';
import { FaAws, FaHome } from 'react-icons/fa';

const Layout = ({ children }) => {
  const location = useLocation();
  const isHomePage = location.pathname === '/';
  
  const bgGradient = useColorModeValue(
    'linear(to-br, awsBlue.500, aws.500)',
    'linear(to-br, awsBlue.800, aws.800)'
  );

  return (
    <Box minH="100vh" bg="gray.50">
      <Box bgGradient={bgGradient} color="white" pb={isHomePage ? 16 : 8}>
        <Container maxW="container.xl">
          <Flex py={4} align="center">
            <HStack spacing={3}>
              <Icon as={FaAws} boxSize={8} />
              <Link to="/">
                <Heading size="lg" fontWeight="bold">
                  Architecture Generator
                </Heading>
              </Link>
            </HStack>
            
            <Spacer />
            
            {!isHomePage && (
              <Button
                as={Link}
                to="/"
                variant="outline"
                colorScheme="whiteAlpha"
                leftIcon={<FaHome />}
                size="sm"
              >
                New Project
              </Button>
            )}
          </Flex>
          
          {isHomePage && (
            <VStack spacing={4} align="center" py={12}>
              <Heading size="2xl" textAlign="center" fontWeight="extrabold">
                Generate Custom AWS Architectures
              </Heading>
              <Text fontSize="xl" textAlign="center" maxW="2xl" opacity={0.9}>
                Answer a few questions and get a tailored AWS architecture with 
                Infrastructure as Code templates, cost estimates, and security recommendations
              </Text>
            </VStack>
          )}
        </Container>
      </Box>

      <Container maxW="container.xl" py={8}>
        {children}
      </Container>

      <Box bg="gray.800" color="white" py={8} mt={12}>
        <Container maxW="container.xl">
          <VStack spacing={4}>
            <HStack spacing={2}>
              <Icon as={FaAws} />
              <Text fontSize="sm">AWS Architecture Generator</Text>
            </HStack>
            <Text fontSize="sm" color="gray.400" textAlign="center">
              Built with ❤️. Generate production-ready AWS architectures in minutes.
            </Text>
          </VStack>
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;