import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://localhost:8000';

const NotebookContext = createContext();

const initialState = {
  workflows: [],
  currentWorkflow: null,
  blocks: [],
  datasets: [],
  dagData: null,
  isConnected: false,
  loading: false,
  error: null,
};

function notebookReducer(state, action) {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    
    case 'SET_CONNECTION_STATUS':
      return { ...state, isConnected: action.payload };
    
    case 'SET_WORKFLOWS':
      return { ...state, workflows: action.payload };
    
    case 'SET_CURRENT_WORKFLOW':
      return { ...state, currentWorkflow: action.payload };
    
    case 'SET_BLOCKS':
      return { ...state, blocks: action.payload };
    
    case 'SET_DATASETS':
      return { ...state, datasets: action.payload };
    
    case 'SET_DAG_DATA':
      return { ...state, dagData: action.payload };
    
    case 'ADD_BLOCK':
      return { ...state, blocks: [...state.blocks, action.payload] };
    
    case 'UPDATE_BLOCK':
      return {
        ...state,
        blocks: state.blocks.map(block =>
          block.id === action.payload.id ? action.payload : block
        ),
      };
    
    case 'REMOVE_BLOCK':
      return {
        ...state,
        blocks: state.blocks.filter(block => block.id !== action.payload),
      };
    
    case 'ADD_DATASET':
      return { ...state, datasets: [...state.datasets, action.payload] };
    
    default:
      return state;
  }
}

export function NotebookProvider({ children }) {
  const [state, dispatch] = useReducer(notebookReducer, initialState);

  // Initialize API connection
  useEffect(() => {
    checkConnection();
    loadInitialData();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/system/status`);
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: true });
    } catch (error) {
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: false });
      console.error('Backend connection failed:', error);
    }
  };

  const loadInitialData = useCallback(async () => {
    if (!state.isConnected) return;
    
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      
      // Load datasets
      const datasetsResponse = await axios.get(`${API_BASE_URL}/datasets`);
      dispatch({ type: 'SET_DATASETS', payload: datasetsResponse.data.datasets || [] });
      
      // Load workflows
      const workflowsResponse = await axios.get(`${API_BASE_URL}/workflows`);
      dispatch({ type: 'SET_WORKFLOWS', payload: workflowsResponse.data.workflows || [] });
      
    } catch (error) {
      console.error('Failed to load initial data:', error);
      dispatch({ type: 'SET_ERROR', payload: error.message });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }, [state.isConnected]);

  const createWorkflow = async (name, description) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/workflows`, {
        name,
        description,
        blocks: []
      });
      
      const newWorkflow = response.data.workflow;
      dispatch({ type: 'SET_WORKFLOWS', payload: [...state.workflows, newWorkflow] });
      dispatch({ type: 'SET_CURRENT_WORKFLOW', payload: newWorkflow });
      
      toast.success('Workflow created successfully!');
      return newWorkflow;
    } catch (error) {
      toast.error('Failed to create workflow');
      throw error;
    }
  };

  const addBlock = async (workflowId, blockData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/workflows/${workflowId}/blocks`, blockData);
      const newBlock = response.data.block;
      
      dispatch({ type: 'ADD_BLOCK', payload: newBlock });
      toast.success('Block added successfully!');
      return newBlock;
    } catch (error) {
      toast.error('Failed to add block');
      throw error;
    }
  };

  const executeBlock = async (blockId) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/blocks/${blockId}/execute`);
      const result = response.data.execution_result;
      
      if (result.success) {
        toast.success('Block executed successfully!');
      } else {
        toast.error(`Execution failed: ${result.error}`);
      }
      
      return result;
    } catch (error) {
      toast.error('Failed to execute block');
      throw error;
    }
  };

  const uploadDataset = async (file, name, description) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('name', name);
      formData.append('description', description);
      
      const response = await axios.post(`${API_BASE_URL}/datasets/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const newDataset = response.data.dataset;
      dispatch({ type: 'ADD_DATASET', payload: newDataset });
      toast.success('Dataset uploaded successfully!');
      return newDataset;
    } catch (error) {
      toast.error('Failed to upload dataset');
      throw error;
    }
  };

  const getDAGData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dag/visualization`);
      dispatch({ type: 'SET_DAG_DATA', payload: response.data.visualization_data });
      return response.data.visualization_data;
    } catch (error) {
      console.error('Failed to load DAG data:', error);
      throw error;
    }
  };

  const value = {
    ...state,
    createWorkflow,
    addBlock,
    executeBlock,
    uploadDataset,
    getDAGData,
    checkConnection,
  };

  return (
    <NotebookContext.Provider value={value}>
      {children}
    </NotebookContext.Provider>
  );
}

export function useNotebook() {
  const context = useContext(NotebookContext);
  if (!context) {
    throw new Error('useNotebook must be used within a NotebookProvider');
  }
  return context;
}
