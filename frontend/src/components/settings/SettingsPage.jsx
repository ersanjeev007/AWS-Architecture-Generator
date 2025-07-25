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
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Switch,
  Textarea,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Divider,
  Badge,
  Icon,
  useColorModeValue,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  List,
  ListItem,
  ListIcon,
} from '@chakra-ui/react';
import {
  FaCog,
  FaUser,
  FaShieldAlt,
  FaCloud,
  FaBell,
  FaPalette,
  FaDatabase,
  FaKey,
  FaDownload,
  FaUpload,
  FaSave,
  FaUndo,
  FaCheckCircle,
  FaExclamationTriangle,
  FaServer,
  FaGlobe,
  FaLock,
  FaEye,
} from 'react-icons/fa';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    profile: {
      fullName: 'Demo User',
      email: 'demo@example.com',
      username: 'demo',
      timezone: 'UTC',
      language: 'en',
    },
    preferences: {
      defaultRegion: 'us-east-1',
      defaultInstanceType: 't3.micro',
      autoSave: true,
      darkMode: false,
      compactView: false,
      showCosts: true,
      enableNotifications: true,
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 7,
      passwordExpiration: 90,
      loginAlerts: true,
      apiAccess: false,
    },
    platform: {
      autoBackup: true,
      backupFrequency: 'daily',
      maxProjects: 50,
      enableLogging: true,
      logLevel: 'info',
      cacheTimeout: 3600,
    }
  });

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const InfoAlert = () => (
    <Alert status="info" borderRadius="lg" mb={6}>
      <AlertIcon />
      <Box>
        <AlertTitle>Advanced Settings</AlertTitle>
        <AlertDescription>
          Configure platform settings, integrations, and preferences. All changes are saved automatically and applied immediately.
        </AlertDescription>
      </Box>
    </Alert>
  );

  const handleSaveSettings = (section) => {
    toast({
      title: 'Settings saved successfully',
      description: `${section} settings have been updated.`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const handleResetSettings = (section) => {
    toast({
      title: 'Settings reset',
      description: `${section} settings have been reset to defaults.`,
      status: 'info',
      duration: 3000,
      isClosable: true,
    });
  };

  const ProfileSettings = () => (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <HStack>
            <Icon as={FaUser} color="blue.500" />
            <Heading size="md">Profile Settings</Heading>
          </HStack>
          <Badge colorScheme="green">Demo Account</Badge>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl>
              <FormLabel>Full Name</FormLabel>
              <Input
                value={settings.profile.fullName}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, fullName: e.target.value }
                })}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Username</FormLabel>
              <Input
                value={settings.profile.username}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, username: e.target.value }
                })}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Email Address</FormLabel>
              <Input
                type="email"
                value={settings.profile.email}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, email: e.target.value }
                })}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Timezone</FormLabel>
              <Select
                value={settings.profile.timezone}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, timezone: e.target.value }
                })}
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
                <option value="Asia/Tokyo">Tokyo</option>
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel>Language</FormLabel>
              <Select
                value={settings.profile.language}
                onChange={(e) => setSettings({
                  ...settings,
                  profile: { ...settings.profile, language: e.target.value }
                })}
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
                <option value="ja">Japanese</option>
              </Select>
            </FormControl>
          </SimpleGrid>
          
          <HStack w="full" justify="flex-end" spacing={4}>
            <Button variant="outline" onClick={() => handleResetSettings('Profile')}>
              Reset
            </Button>
            <Button colorScheme="blue" onClick={() => handleSaveSettings('Profile')}>
              Save Changes
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const PreferencesSettings = () => (
    <Card>
      <CardHeader>
        <HStack>
          <Icon as={FaCog} color="green.500" />
          <Heading size="md">Platform Preferences</Heading>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl>
              <FormLabel>Default AWS Region</FormLabel>
              <Select
                value={settings.preferences.defaultRegion}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, defaultRegion: e.target.value }
                })}
              >
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">Europe (Ireland)</option>
                <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel>Default Instance Type</FormLabel>
              <Select
                value={settings.preferences.defaultInstanceType}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, defaultInstanceType: e.target.value }
                })}
              >
                <option value="t3.micro">t3.micro</option>
                <option value="t3.small">t3.small</option>
                <option value="t3.medium">t3.medium</option>
                <option value="m5.large">m5.large</option>
              </Select>
            </FormControl>
          </SimpleGrid>
          
          <Divider />
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Auto-save Projects</FormLabel>
              <Switch
                isChecked={settings.preferences.autoSave}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, autoSave: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Dark Mode</FormLabel>
              <Switch
                isChecked={settings.preferences.darkMode}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, darkMode: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Compact View</FormLabel>
              <Switch
                isChecked={settings.preferences.compactView}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, compactView: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Show Cost Estimates</FormLabel>
              <Switch
                isChecked={settings.preferences.showCosts}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, showCosts: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Enable Notifications</FormLabel>
              <Switch
                isChecked={settings.preferences.enableNotifications}
                onChange={(e) => setSettings({
                  ...settings,
                  preferences: { ...settings.preferences, enableNotifications: e.target.checked }
                })}
              />
            </FormControl>
          </SimpleGrid>
          
          <HStack w="full" justify="flex-end" spacing={4}>
            <Button variant="outline" onClick={() => handleResetSettings('Preferences')}>
              Reset
            </Button>
            <Button colorScheme="green" onClick={() => handleSaveSettings('Preferences')}>
              Save Changes
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const SecuritySettings = () => (
    <Card>
      <CardHeader>
        <HStack>
          <Icon as={FaShieldAlt} color="red.500" />
          <Heading size="md">Security Settings</Heading>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Two-Factor Authentication</FormLabel>
              <Switch
                isChecked={settings.security.twoFactorAuth}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, twoFactorAuth: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Login Alerts</FormLabel>
              <Switch
                isChecked={settings.security.loginAlerts}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, loginAlerts: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>API Access</FormLabel>
              <Switch
                isChecked={settings.security.apiAccess}
                onChange={(e) => setSettings({
                  ...settings,
                  security: { ...settings.security, apiAccess: e.target.checked }
                })}
              />
            </FormControl>
          </SimpleGrid>
          
          <Divider />
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl>
              <FormLabel>Session Timeout (days)</FormLabel>
              <NumberInput
                value={settings.security.sessionTimeout}
                min={1}
                max={30}
                onChange={(value) => setSettings({
                  ...settings,
                  security: { ...settings.security, sessionTimeout: parseInt(value) }
                })}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
            
            <FormControl>
              <FormLabel>Password Expiration (days)</FormLabel>
              <NumberInput
                value={settings.security.passwordExpiration}
                min={30}
                max={365}
                step={30}
                onChange={(value) => setSettings({
                  ...settings,
                  security: { ...settings.security, passwordExpiration: parseInt(value) }
                })}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
          </SimpleGrid>
          
          <Alert status="warning" borderRadius="md">
            <AlertIcon />
            <Text fontSize="sm">
              Changes to security settings will take effect after your next login.
            </Text>
          </Alert>
          
          <HStack w="full" justify="flex-end" spacing={4}>
            <Button variant="outline" onClick={() => handleResetSettings('Security')}>
              Reset
            </Button>
            <Button colorScheme="red" onClick={() => handleSaveSettings('Security')}>
              Save Changes
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const PlatformSettings = () => (
    <Card>
      <CardHeader>
        <HStack>
          <Icon as={FaServer} color="purple.500" />
          <Heading size="md">Platform Configuration</Heading>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6}>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <FormControl display="flex" alignItems="center">
              <FormLabel mb={0}>Auto Backup</FormLabel>
              <Switch
                isChecked={settings.platform.autoBackup}
                onChange={(e) => setSettings({
                  ...settings,
                  platform: { ...settings.platform, autoBackup: e.target.checked }
                })}
              />
            </FormControl>
            
            <FormControl>
              <FormLabel>Backup Frequency</FormLabel>
              <Select
                value={settings.platform.backupFrequency}
                onChange={(e) => setSettings({
                  ...settings,
                  platform: { ...settings.platform, backupFrequency: e.target.value }
                })}
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </Select>
            </FormControl>
            
            <FormControl>
              <FormLabel>Max Projects per User</FormLabel>
              <NumberInput
                value={settings.platform.maxProjects}
                min={1}
                max={100}
                onChange={(value) => setSettings({
                  ...settings,
                  platform: { ...settings.platform, maxProjects: parseInt(value) }
                })}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>
            
            <FormControl>
              <FormLabel>Log Level</FormLabel>
              <Select
                value={settings.platform.logLevel}
                onChange={(e) => setSettings({
                  ...settings,
                  platform: { ...settings.platform, logLevel: e.target.value }
                })}
              >
                <option value="debug">Debug</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
              </Select>
            </FormControl>
          </SimpleGrid>
          
          <FormControl>
            <FormLabel>Cache Timeout (seconds): {settings.platform.cacheTimeout}</FormLabel>
            <Slider
              value={settings.platform.cacheTimeout}
              min={300}
              max={86400}
              step={300}
              onChange={(value) => setSettings({
                ...settings,
                platform: { ...settings.platform, cacheTimeout: value }
              })}
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb />
            </Slider>
            <HStack justify="space-between" fontSize="sm" color="gray.500">
              <Text>5 min</Text>
              <Text>24 hours</Text>
            </HStack>
          </FormControl>
          
          <HStack w="full" justify="flex-end" spacing={4}>
            <Button variant="outline" onClick={() => handleResetSettings('Platform')}>
              Reset
            </Button>
            <Button colorScheme="purple" onClick={() => handleSaveSettings('Platform')}>
              Save Changes
            </Button>
          </HStack>
        </VStack>
      </CardBody>
    </Card>
  );

  const DataManagement = () => (
    <Card>
      <CardHeader>
        <HStack>
          <Icon as={FaDatabase} color="orange.500" />
          <Heading size="md">Data Management</Heading>
        </HStack>
      </CardHeader>
      <CardBody>
        <VStack spacing={6}>
          <Alert status="info" borderRadius="md">
            <AlertIcon />
            <Box>
              <Text fontWeight="bold">Data Export & Import</Text>
              <Text fontSize="sm">
                Backup your projects and settings, or restore from a previous backup.
              </Text>
            </Box>
          </Alert>
          
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={6} w="full">
            <Card variant="outline">
              <CardBody>
                <VStack spacing={4}>
                  <Icon as={FaDownload} boxSize={8} color="blue.500" />
                  <Text fontWeight="bold">Export Data</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Download all your projects, settings, and user data
                  </Text>
                  <Button colorScheme="blue" size="sm" w="full">
                    Export All Data
                  </Button>
                </VStack>
              </CardBody>
            </Card>
            
            <Card variant="outline">
              <CardBody>
                <VStack spacing={4}>
                  <Icon as={FaUpload} boxSize={8} color="green.500" />
                  <Text fontWeight="bold">Import Data</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Restore from a previously exported backup file
                  </Text>
                  <Button colorScheme="green" size="sm" w="full">
                    Import Backup
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          </SimpleGrid>
          
          <Divider />
          
          <Alert status="warning" borderRadius="md">
            <AlertIcon />
            <Box>
              <Text fontWeight="bold">Danger Zone</Text>
              <Text fontSize="sm">
                Irreversible actions that will permanently delete your data.
              </Text>
            </Box>
          </Alert>
          
          <HStack w="full" justify="center" spacing={4}>
            <Button colorScheme="red" variant="outline">
              Delete All Projects
            </Button>
            <Button colorScheme="red">
              Delete Account
            </Button>
          </HStack>
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
              <Heading size="lg">Settings</Heading>
              <Text color="gray.600">
                Configure your account, preferences, and platform settings
              </Text>
            </VStack>
            <HStack>
              <Button leftIcon={<FaUndo />} size="sm" variant="outline">
                Reset All
              </Button>
              <Button leftIcon={<FaSave />} size="sm" colorScheme="blue">
                Save All Changes
              </Button>
            </HStack>
          </HStack>
          
          <InfoAlert />
        </Box>

        {/* Settings Tabs */}
        <Tabs>
          <TabList>
            <Tab>Profile</Tab>
            <Tab>Preferences</Tab>
            <Tab>Security</Tab>
            <Tab>Platform</Tab>
            <Tab>Data</Tab>
          </TabList>

          <TabPanels>
            <TabPanel px={0}>
              <ProfileSettings />
            </TabPanel>
            
            <TabPanel px={0}>
              <PreferencesSettings />
            </TabPanel>
            
            <TabPanel px={0}>
              <SecuritySettings />
            </TabPanel>
            
            <TabPanel px={0}>
              <PlatformSettings />
            </TabPanel>
            
            <TabPanel px={0}>
              <DataManagement />
            </TabPanel>
          </TabPanels>
        </Tabs>

        {/* Future Features Preview */}
        <Card bg="gradient-to-r" bgGradient="linear(to-r, teal.50, cyan.50)">
          <CardBody>
            <VStack spacing={4}>
              <Heading size="md" textAlign="center">Advanced Configuration</Heading>
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6} w="full">
                <VStack>
                  <Icon as={FaCloud} size="2em" color="teal.500" />
                  <Text fontWeight="bold">Cloud Integrations</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Connect with multiple cloud providers and third-party services
                  </Text>
                </VStack>
                <VStack>
                  <Icon as={FaKey} size="2em" color="cyan.500" />
                  <Text fontWeight="bold">API Management</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Generate and manage API keys for programmatic access
                  </Text>
                </VStack>
                <VStack>
                  <Icon as={FaBell} size="2em" color="purple.500" />
                  <Text fontWeight="bold">Advanced Notifications</Text>
                  <Text fontSize="sm" textAlign="center" color="gray.600">
                    Customize alerts, webhooks, and notification channels
                  </Text>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

export default SettingsPage;