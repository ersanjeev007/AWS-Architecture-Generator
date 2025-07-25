import React, { useState } from 'react';
import {
  Box,
  Container,
  VStack,
  HStack,
  Heading,
  Text,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Badge,
  Button,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  Avatar,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useDisclosure,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Icon,
  InputGroup,
  InputLeftElement,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import {
  FaUsers,
  FaUserPlus,
  FaEdit,
  FaTrash,
  FaEllipsisV,
  FaSearch,
  FaShieldAlt,
  FaUserCog,
  FaCrown,
  FaEye,
  FaDownload,
  FaFilter,
  FaProjectDiagram,
} from 'react-icons/fa';

const UserManagementPage = () => {
  const [selectedUser, setSelectedUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('all');
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const toast = useToast();

  // Mock user data
  const mockUsers = [
    {
      id: '1',
      username: 'demo',
      email: 'demo@example.com',
      fullName: 'Demo User',
      role: 'admin',
      status: 'active',
      lastLogin: '2 hours ago',
      createdAt: '2024-01-15',
      projectsCount: 12,
      deploymentsCount: 45,
      avatar: null
    },
    {
      id: '2',
      username: 'john.doe',
      email: 'john.doe@company.com',
      fullName: 'John Doe',
      role: 'user',
      status: 'active',
      lastLogin: '1 day ago',
      createdAt: '2024-02-20',
      projectsCount: 8,
      deploymentsCount: 23,
      avatar: null
    },
    {
      id: '3',
      username: 'jane.smith',
      email: 'jane.smith@company.com',
      fullName: 'Jane Smith',
      role: 'user',
      status: 'active',
      lastLogin: '3 days ago',
      createdAt: '2024-03-10',
      projectsCount: 15,
      deploymentsCount: 67,
      avatar: null
    },
    {
      id: '4',
      username: 'mike.wilson',
      email: 'mike.wilson@company.com',
      fullName: 'Mike Wilson',
      role: 'user',
      status: 'inactive',
      lastLogin: '2 weeks ago',
      createdAt: '2024-01-30',
      projectsCount: 3,
      deploymentsCount: 8,
      avatar: null
    },
  ];

  const [users, setUsers] = useState(mockUsers);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    fullName: '',
    role: 'user',
    status: 'active'
  });

  const ComingSoonAlert = () => (
    <Alert status="info" borderRadius="lg" mb={6}>
      <AlertIcon />
      <Box>
        <AlertTitle>User Management System</AlertTitle>
        <AlertDescription>
          Manage users, roles, and permissions across your organization. Full audit logging and enterprise features available.
        </AlertDescription>
      </Box>
    </Alert>
  );

  const UserStats = () => (
    <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaUsers} boxSize={8} color="blue.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">{users.length}</Text>
              <Text fontSize="sm" color="gray.600">Total Users</Text>
              <Text fontSize="xs" color="green.500">+2 this month</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaShieldAlt} boxSize={8} color="purple.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">
                {users.filter(u => u.role === 'admin').length}
              </Text>
              <Text fontSize="sm" color="gray.600">Administrators</Text>
              <Text fontSize="xs" color="blue.500">System access</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaUserCog} boxSize={8} color="green.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">
                {users.filter(u => u.status === 'active').length}
              </Text>
              <Text fontSize="sm" color="gray.600">Active Users</Text>
              <Text fontSize="xs" color="green.500">Online now</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      <Card>
        <CardBody>
          <HStack>
            <Icon as={FaProjectDiagram} boxSize={8} color="orange.500" />
            <VStack align="start" spacing={0}>
              <Text fontSize="2xl" fontWeight="bold">
                {users.reduce((sum, user) => sum + user.projectsCount, 0)}
              </Text>
              <Text fontSize="sm" color="gray.600">Total Projects</Text>
              <Text fontSize="xs" color="orange.500">All users</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>
    </SimpleGrid>
  );

  const handleCreateUser = () => {
    const newUser = {
      id: (users.length + 1).toString(),
      ...formData,
      lastLogin: 'Never',
      createdAt: new Date().toISOString().split('T')[0],
      projectsCount: 0,
      deploymentsCount: 0,
      avatar: null
    };
    
    setUsers([...users, newUser]);
    setFormData({
      username: '',
      email: '',
      fullName: '',
      role: 'user',
      status: 'active'
    });
    onClose();
    
    toast({
      title: 'User created successfully',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handleDeleteUser = (userId) => {
    setUsers(users.filter(u => u.id !== userId));
    onDeleteClose();
    
    toast({
      title: 'User deleted successfully',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.fullName.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = filterRole === 'all' || user.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const UserTable = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <Heading size="md">User Management</Heading>
          <HStack>
            <InputGroup maxW="300px">
              <InputLeftElement>
                <Icon as={FaSearch} color="gray.400" />
              </InputLeftElement>
              <Input
                placeholder="Search users..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </InputGroup>
            <Select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              maxW="150px"
            >
              <option value="all">All Roles</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
            </Select>
            <Button
              leftIcon={<FaUserPlus />}
              colorScheme="blue"
              onClick={onOpen}
              minW="120px"
              size="md"
            >
              Add User
            </Button>
          </HStack>
        </HStack>
      </CardHeader>
      <CardBody>
        <TableContainer>
          <Table variant="simple">
            <Thead>
              <Tr>
                <Th>User</Th>
                <Th>Email</Th>
                <Th>Role</Th>
                <Th>Status</Th>
                <Th>Projects</Th>
                <Th>Last Login</Th>
                <Th>Actions</Th>
              </Tr>
            </Thead>
            <Tbody>
              {filteredUsers.map((user) => (
                <Tr key={user.id}>
                  <Td>
                    <HStack>
                      <Avatar size="sm" name={user.fullName} />
                      <VStack align="start" spacing={0}>
                        <Text fontWeight="medium">{user.fullName}</Text>
                        <Text fontSize="sm" color="gray.600">@{user.username}</Text>
                      </VStack>
                    </HStack>
                  </Td>
                  <Td>{user.email}</Td>
                  <Td>
                    <Badge
                      colorScheme={user.role === 'admin' ? 'purple' : 'blue'}
                      leftIcon={user.role === 'admin' ? <FaCrown /> : <FaUserCog />}
                    >
                      {user.role}
                    </Badge>
                  </Td>
                  <Td>
                    <Badge
                      colorScheme={user.status === 'active' ? 'green' : 'gray'}
                    >
                      {user.status}
                    </Badge>
                  </Td>
                  <Td>
                    <Text fontWeight="medium">{user.projectsCount}</Text>
                    <Text fontSize="xs" color="gray.500">
                      {user.deploymentsCount} deployments
                    </Text>
                  </Td>
                  <Td>
                    <Text fontSize="sm">{user.lastLogin}</Text>
                  </Td>
                  <Td>
                    <Menu>
                      <MenuButton
                        as={IconButton}
                        icon={<FaEllipsisV />}
                        variant="ghost"
                        size="sm"
                      />
                      <MenuList>
                        <MenuItem icon={<FaEye />}>
                          View Details
                        </MenuItem>
                        <MenuItem icon={<FaEdit />}>
                          Edit User
                        </MenuItem>
                        <MenuItem icon={<FaShieldAlt />}>
                          Manage Permissions
                        </MenuItem>
                        <MenuItem
                          icon={<FaTrash />}
                          color="red.500"
                          onClick={() => {
                            setSelectedUser(user);
                            onDeleteOpen();
                          }}
                        >
                          Delete User
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          </Table>
        </TableContainer>
      </CardBody>
    </Card>
  );

  const RecentActivity = () => (
    <Card>
      <CardHeader>
        <Heading size="md">Recent User Activity</Heading>
      </CardHeader>
      <CardBody>
        <VStack spacing={4}>
          {[
            { user: 'John Doe', action: 'Created new project "Web App"', time: '30 minutes ago', type: 'create' },
            { user: 'Jane Smith', action: 'Deployed infrastructure', time: '2 hours ago', type: 'deploy' },
            { user: 'Demo User', action: 'Updated user settings', time: '4 hours ago', type: 'update' },
            { user: 'Mike Wilson', action: 'Logged in', time: '1 day ago', type: 'login' },
          ].map((activity, index) => (
            <HStack key={index} w="full" p={3} borderRadius="md" bg="gray.50" justify="space-between">
              <HStack>
                <Avatar size="sm" name={activity.user} />
                <VStack align="start" spacing={0}>
                  <Text fontSize="sm" fontWeight="medium">{activity.user}</Text>
                  <Text fontSize="sm" color="gray.600">{activity.action}</Text>
                </VStack>
              </HStack>
              <Text fontSize="xs" color="gray.500">{activity.time}</Text>
            </HStack>
          ))}
        </VStack>
      </CardBody>
    </Card>
  );

  return (
    <Container maxW="7xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg">User Management</Heading>
              <Text color="gray.600">
                Manage users, roles, and permissions across the platform
              </Text>
            </VStack>
            <HStack>
              <Button leftIcon={<FaDownload />} size="sm" variant="outline">
                Export Users
              </Button>
              <Button leftIcon={<FaFilter />} size="sm" variant="outline">
                Advanced Filter
              </Button>
            </HStack>
          </HStack>
          
          <ComingSoonAlert />
        </Box>

        {/* User Statistics */}
        <UserStats />

        {/* Tabs */}
        <Tabs>
          <TabList>
            <Tab>All Users</Tab>
            <Tab>Recent Activity</Tab>
            <Tab>Permissions</Tab>
            <Tab>Audit Log</Tab>
          </TabList>

          <TabPanels>
            <TabPanel px={0}>
              <UserTable />
            </TabPanel>
            
            <TabPanel px={0}>
              <RecentActivity />
            </TabPanel>
            
            <TabPanel px={0}>
              <Card>
                <CardHeader>
                  <Heading size="md">Role & Permission Management</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4}>
                    <Text color="gray.600" textAlign="center">
                      Advanced role and permission management features will be available here.
                      This will include custom role creation, permission matrices, and access control.
                    </Text>
                    <Button variant="outline" size="sm">
                      Configure Permissions
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>
            
            <TabPanel px={0}>
              <Card>
                <CardHeader>
                  <Heading size="md">User Activity Audit Log</Heading>
                </CardHeader>
                <CardBody>
                  <VStack spacing={4}>
                    <Text color="gray.600" textAlign="center">
                      Comprehensive audit logging and user activity tracking will be displayed here.
                      This will include login history, action logs, and security events.
                    </Text>
                    <Button variant="outline" size="sm">
                      View Full Audit Log
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Create User Modal */}
        <Modal isOpen={isOpen} onClose={onClose}>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Create New User</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Username</FormLabel>
                  <Input
                    value={formData.username}
                    onChange={(e) => setFormData({...formData, username: e.target.value})}
                    placeholder="Enter username"
                  />
                </FormControl>
                
                <FormControl isRequired>
                  <FormLabel>Email</FormLabel>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    placeholder="Enter email address"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Full Name</FormLabel>
                  <Input
                    value={formData.fullName}
                    onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                    placeholder="Enter full name"
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Role</FormLabel>
                  <Select
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                  >
                    <option value="user">User</option>
                    <option value="admin">Administrator</option>
                  </Select>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Status</FormLabel>
                  <HStack>
                    <Switch
                      isChecked={formData.status === 'active'}
                      onChange={(e) => setFormData({...formData, status: e.target.checked ? 'active' : 'inactive'})}
                    />
                    <Text>{formData.status === 'active' ? 'Active' : 'Inactive'}</Text>
                  </HStack>
                </FormControl>
              </VStack>
            </ModalBody>
            
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                Cancel
              </Button>
              <Button colorScheme="blue" onClick={handleCreateUser}>
                Create User
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Delete Confirmation Modal */}
        <Modal isOpen={isDeleteOpen} onClose={onDeleteClose}>
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Delete User</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Text>
                Are you sure you want to delete user "{selectedUser?.fullName}"? 
                This action cannot be undone and will remove all associated projects and data.
              </Text>
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onDeleteClose}>
                Cancel
              </Button>
              <Button 
                colorScheme="red" 
                onClick={() => handleDeleteUser(selectedUser?.id)}
              >
                Delete
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Container>
  );
};

export default UserManagementPage;