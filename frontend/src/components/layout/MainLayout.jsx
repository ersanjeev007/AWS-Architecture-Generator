import React, { useState } from 'react';
import {
  Box,
  Flex,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useDisclosure,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Badge,
  Tooltip,
  useColorModeValue,
  useBreakpointValue,
} from '@chakra-ui/react';
import {
  FaHome,
  FaProjectDiagram,
  FaAws,
  FaUsers,
  FaCog,
  FaShieldAlt,
  FaDollarSign,
  FaChartBar,
  FaBars,
  FaSignOutAlt,
  FaUser,
  FaBell,
  FaSearch,
} from 'react-icons/fa';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const MainLayout = ({ children }) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  
  const bg = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const sidebarBg = useColorModeValue('gray.50', 'gray.800');
  const activeBg = useColorModeValue('blue.50', 'blue.900');
  const activeColor = useColorModeValue('blue.600', 'blue.200');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  
  const isMobile = useBreakpointValue({ base: true, md: false });

  const navigationItems = [
    {
      name: 'Dashboard',
      path: '/',
      icon: FaHome,
      badge: null,
    },
    {
      name: 'Architectures',
      path: '/architectures',
      icon: FaProjectDiagram,
      badge: null,
    },
    {
      name: 'AWS Accounts',
      path: '/aws-accounts',
      icon: FaAws,
      badge: null,
    },
    {
      name: 'Cost Analysis',
      path: '/cost-analysis',
      icon: FaDollarSign,
      badge: 'New',
    },
    {
      name: 'Security',
      path: '/security',
      icon: FaShieldAlt,
      badge: 'AI',
    },
    {
      name: 'Analytics',
      path: '/analytics',
      icon: FaChartBar,
      badge: null,
    },
    ...(user?.is_admin ? [{
      name: 'Users',
      path: '/users',
      icon: FaUsers,
      badge: null,
    }] : []),
    {
      name: 'Settings',
      path: '/settings',
      icon: FaCog,
      badge: null,
    },
  ];

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const Sidebar = ({ onClose: drawerOnClose }) => (
    <VStack
      h="full"
      w={sidebarCollapsed && !isMobile ? "80px" : "280px"}
      bg={sidebarBg}
      borderRight="1px"
      borderRightColor={borderColor}
      py={4}
      px={sidebarCollapsed && !isMobile ? 2 : 4}
      spacing={0}
      transition="all 0.3s"
    >
      {/* Logo/Brand */}
      <HStack
        w="full"
        justify={sidebarCollapsed && !isMobile ? "center" : "flex-start"}
        mb={8}
        px={2}
      >
        <Box
          w="40px"
          h="40px"
          bg="blue.500"
          borderRadius="lg"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <FaAws color="white" size="20px" />
        </Box>
        {(!sidebarCollapsed || isMobile) && (
          <VStack align="start" spacing={0}>
            <Heading size="md" color="blue.600">
              AWS Gen
            </Heading>
            <Text fontSize="xs" color={textColor}>
              Architecture Generator
            </Text>
          </VStack>
        )}
      </HStack>

      {/* Navigation Items */}
      <VStack w="full" spacing={1} flex={1}>
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Tooltip
              key={item.path}
              label={item.name}
              placement="right"
              isDisabled={!sidebarCollapsed || isMobile}
            >
              <Box w="full">
                <Button
                  as={Link}
                  to={item.path}
                  w="full"
                  justifyContent={sidebarCollapsed && !isMobile ? "center" : "flex-start"}
                  variant="ghost"
                  leftIcon={<Icon />}
                  bg={isActive ? activeBg : 'transparent'}
                  color={isActive ? activeColor : textColor}
                  _hover={{
                    bg: isActive ? activeBg : 'gray.100',
                    color: isActive ? activeColor : 'gray.900',
                  }}
                  borderRadius="lg"
                  px={sidebarCollapsed && !isMobile ? 2 : 4}
                  onClick={drawerOnClose}
                >
                  {(!sidebarCollapsed || isMobile) && (
                    <>
                      <Text flex={1} textAlign="left">
                        {item.name}
                      </Text>
                      {item.badge && (
                        <Badge
                          colorScheme={item.badge === 'New' ? 'green' : 'purple'}
                          variant="solid"
                          fontSize="xs"
                          borderRadius="full"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Button>
              </Box>
            </Tooltip>
          );
        })}
      </VStack>

      {/* User Profile Section */}
      {(!sidebarCollapsed || isMobile) && (
        <Box w="full" pt={4} borderTop="1px" borderTopColor={borderColor}>
          <Menu>
            <MenuButton
              as={Button}
              variant="ghost"
              w="full"
              justifyContent="flex-start"
              px={4}
            >
              <HStack>
                <Avatar size="sm" name={user?.full_name || user?.username} />
                <VStack align="start" spacing={0}>
                  <Text fontSize="sm" fontWeight="medium">
                    {user?.full_name || user?.username}
                  </Text>
                  <Text fontSize="xs" color={textColor}>
                    {user?.is_admin ? 'Administrator' : 'User'}
                  </Text>
                </VStack>
              </HStack>
            </MenuButton>
            <MenuList>
              <MenuItem icon={<FaUser />} as={Link} to="/profile">
                Profile Settings
              </MenuItem>
              <MenuItem icon={<FaCog />} as={Link} to="/settings">
                App Settings
              </MenuItem>
              <MenuDivider />
              <MenuItem icon={<FaSignOutAlt />} onClick={handleLogout}>
                Sign Out
              </MenuItem>
            </MenuList>
          </Menu>
        </Box>
      )}
    </VStack>
  );

  return (
    <Flex h="100vh" bg={bg}>
      {/* Desktop Sidebar */}
      {!isMobile && <Sidebar />}

      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="sm">
        <DrawerOverlay />
        <DrawerContent>
          <DrawerCloseButton />
          <DrawerBody p={0}>
            <Sidebar onClose={onClose} />
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Main Content Area */}
      <Flex direction="column" flex={1} overflow="hidden">
        {/* Top Header */}
        <HStack
          w="full"
          h="64px"
          bg={bg}
          borderBottom="1px"
          borderBottomColor={borderColor}
          px={6}
          justify="space-between"
        >
          <HStack>
            {isMobile && (
              <IconButton
                icon={<FaBars />}
                variant="ghost"
                onClick={onOpen}
                aria-label="Open menu"
              />
            )}
            {!isMobile && (
              <IconButton
                icon={<FaBars />}
                variant="ghost"
                onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                aria-label="Toggle sidebar"
              />
            )}
            
            <Heading size="md" color="gray.700">
              AWS Architecture Generator
            </Heading>
          </HStack>

          <HStack spacing={3}>
            <IconButton
              icon={<FaSearch />}
              variant="ghost"
              aria-label="Search"
            />
            <IconButton
              icon={<FaBell />}
              variant="ghost"
              aria-label="Notifications"
            />
            
            {isMobile && (
              <Menu>
                <MenuButton as={IconButton} icon={<FaUser />} variant="ghost" />
                <MenuList>
                  <MenuItem icon={<FaUser />} as={Link} to="/profile">
                    Profile Settings
                  </MenuItem>
                  <MenuItem icon={<FaCog />} as={Link} to="/settings">
                    App Settings
                  </MenuItem>
                  <MenuDivider />
                  <MenuItem icon={<FaSignOutAlt />} onClick={handleLogout}>
                    Sign Out
                  </MenuItem>
                </MenuList>
              </Menu>
            )}
          </HStack>
        </HStack>

        {/* Page Content */}
        <Box flex={1} overflow="auto" p={6}>
          {children}
        </Box>
      </Flex>
    </Flex>
  );
};

export default MainLayout;