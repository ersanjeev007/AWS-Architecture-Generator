import React, { createContext, useContext, useReducer } from 'react';
import { architectureService } from '../services/architectureService';

const initialState = {
  currentArchitecture: null,
  architectures: {},
  loading: false,
  error: null
};

const ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_ARCHITECTURE: 'SET_ARCHITECTURE',
  CLEAR_ERROR: 'CLEAR_ERROR',
  RESET_STATE: 'RESET_STATE'
};

const architectureReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload, error: null };
    
    case ACTIONS.SET_ERROR:
      return { ...state, error: action.payload, loading: false };
    
    case ACTIONS.SET_ARCHITECTURE:
      return {
        ...state,
        currentArchitecture: action.payload,
        architectures: {
          ...state.architectures,
          [action.payload.id]: action.payload
        },
        loading: false,
        error: null
      };
    
    case ACTIONS.CLEAR_ERROR:
      return { ...state, error: null };
    
    case ACTIONS.RESET_STATE:
      return initialState;
    
    default:
      return state;
  }
};

const ArchitectureContext = createContext();

export const ArchitectureProvider = ({ children }) => {
  const [state, dispatch] = useReducer(architectureReducer, initialState);

  const generateArchitecture = async (questionnaireData) => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    
    try {
      const architecture = await architectureService.generateArchitecture(questionnaireData);
      dispatch({ type: ACTIONS.SET_ARCHITECTURE, payload: architecture });
      return architecture;
    } catch (error) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  };

  const getArchitecture = async (architectureId) => {
    if (state.architectures[architectureId]) {
      dispatch({ 
        type: ACTIONS.SET_ARCHITECTURE, 
        payload: state.architectures[architectureId] 
      });
      return state.architectures[architectureId];
    }

    dispatch({ type: ACTIONS.SET_LOADING, payload: true });
    
    try {
      const architecture = await architectureService.getArchitecture(architectureId);
      dispatch({ type: ACTIONS.SET_ARCHITECTURE, payload: architecture });
      return architecture;
    } catch (error) {
      dispatch({ type: ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: ACTIONS.CLEAR_ERROR });
  };

  const resetState = () => {
    dispatch({ type: ACTIONS.RESET_STATE });
  };

  const value = {
    ...state,
    generateArchitecture,
    getArchitecture,
    clearError,
    resetState
  };

  return (
    <ArchitectureContext.Provider value={value}>
      {children}
    </ArchitectureContext.Provider>
  );
};

export const useArchitecture = () => {
  const context = useContext(ArchitectureContext);
  if (!context) {
    throw new Error('useArchitecture must be used within an ArchitectureProvider');
  }
  return context;
};