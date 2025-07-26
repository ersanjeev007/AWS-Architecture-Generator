import React from 'react';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import ProtectedRoute from './components/auth/ProtectedRoute';
import LoginPage from './components/auth/LoginPage';
import RegisterPage from './components/auth/RegisterPage';
import ProjectsHomePage from './components/projects/ProjectsHomePage';
import QuestionnaireForm from './components/questionnaire/QuestionnaireForm';
import ArchitectureDashboard from './components/architecture/ArchitectureDashboard';
import CostAnalysisPage from './components/cost/CostAnalysisPage';
import SecurityDashboard from './components/security/SecurityDashboard';
import AnalyticsPage from './components/analytics/AnalyticsPage';
import UserManagementPage from './components/admin/UserManagementPage';
import SettingsPage from './components/settings/SettingsPage';
import InfrastructureImportWizard from './components/import/InfrastructureImportWizard';
import ProductionArchitectureWorkflow from './components/production/ProductionArchitectureWorkflow';
import AWSAccountManager from './components/aws/AWSAccountManager';
import { ArchitectureProvider } from './hooks/useArchitecture';
import { AuthProvider } from './hooks/useAuth';

const theme = extendTheme({
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  colors: {
    brand: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1',
    },
    aws: {
      50: '#fff5e6',
      100: '#ffe0b3',
      200: '#ffcc80',
      300: '#ffb74d',
      400: '#ffa726',
      500: '#ff9800',
      600: '#f57c00',
      700: '#ef6c00',
      800: '#e65100',
      900: '#bf360c',
    }
  },
  fonts: {
    heading: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  },
  styles: {
    global: {
      body: {
        bg: 'gray.50',
      },
    },
  },
  components: {
    Button: {
      defaultProps: {
        colorScheme: 'blue',
      },
    },
    Card: {
      baseStyle: {
        container: {
          bg: 'white',
          shadow: 'sm',
          borderRadius: 'lg',
          border: '1px',
          borderColor: 'gray.100',
        }
      }
    }
  }
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <AuthProvider>
        <ArchitectureProvider>
          <Router>
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected routes */}
              <Route path="/" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProjectsHomePage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/architectures" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProjectsHomePage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/create" element={
                <ProtectedRoute>
                  <MainLayout>
                    <QuestionnaireForm />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/project/:id" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ArchitectureDashboard />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/architecture/:id" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ArchitectureDashboard />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              
              <Route path="/cost-analysis" element={
                <ProtectedRoute>
                  <MainLayout>
                    <CostAnalysisPage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/security" element={
                <ProtectedRoute>
                  <MainLayout>
                    <SecurityDashboard />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/analytics" element={
                <ProtectedRoute>
                  <MainLayout>
                    <AnalyticsPage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/users" element={
                <ProtectedRoute requireAdmin={true}>
                  <MainLayout>
                    <UserManagementPage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/settings" element={
                <ProtectedRoute>
                  <MainLayout>
                    <SettingsPage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/import" element={
                <ProtectedRoute>
                  <MainLayout>
                    <InfrastructureImportWizard />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/production" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProductionArchitectureWorkflow />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              <Route path="/manage-aws-accounts" element={
                <ProtectedRoute>
                  <MainLayout>
                    <AWSAccountManager />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              {/* Legacy routes */}
              <Route path="/projects" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProjectsHomePage />
                  </MainLayout>
                </ProtectedRoute>
              } />
              
              {/* Fallback route */}
              <Route path="*" element={
                <ProtectedRoute>
                  <MainLayout>
                    <ProjectsHomePage />
                  </MainLayout>
                </ProtectedRoute>
              } />
            </Routes>
          </Router>
        </ArchitectureProvider>
      </AuthProvider>
    </ChakraProvider>
  );
}

export default App;