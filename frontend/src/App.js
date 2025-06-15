import React from 'react';
import { ChakraProvider, extendTheme } from '@chakra-ui/react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import ProjectsHomePage from './components/projects/ProjectsHomePage';
import QuestionnaireForm from './components/questionnaire/QuestionnaireForm';
import ArchitectureDashboard from './components/architecture/ArchitectureDashboard';
import { ArchitectureProvider } from './hooks/useArchitecture';

const theme = extendTheme({
  colors: {
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
    },
    awsBlue: {
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
    }
  },
  fonts: {
    heading: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
    body: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif',
  },
});

function App() {
  return (
    <ChakraProvider theme={theme}>
      <ArchitectureProvider>
        <Router>
          <Layout>
            <Routes>
              {/* Home page - shows saved projects */}
              <Route path="/" element={<ProjectsHomePage />} />
              
              {/* Create new architecture */}
              <Route path="/create" element={<QuestionnaireForm />} />
              
              {/* View project/architecture details */}
              <Route path="/project/:id" element={<ArchitectureDashboard />} />
              <Route path="/architecture/:id" element={<ArchitectureDashboard />} />
              
              {/* Legacy routes - you can remove these if not needed */}
              <Route path="/projects" element={<ProjectsHomePage />} />
              
              {/* Fallback route */}
              <Route path="*" element={<ProjectsHomePage />} />
            </Routes>
          </Layout>
        </Router>
      </ArchitectureProvider>
    </ChakraProvider>
  );
}

export default App;