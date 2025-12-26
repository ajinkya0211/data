"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { Brain, Upload, Play, GitBranch, Code, Database, FileText, Loader2, CheckCircle, AlertCircle, Settings, BarChart3, Clock, AlertTriangle } from "lucide-react";
import { ReactFlow, Node, Edge, addEdge, Connection, useNodesState, useEdgesState, Background, Controls } from "reactflow";
import "reactflow/dist/style.css";

interface Dataset {
  id: string;
  name: string;
  rows: number;
  columns: string[];
  uploaded_at: string;
  file_size?: number;
  column_types?: Record<string, string>;
  sample_data?: any[];
}

interface Block {
  id: string;
  type: string;
  content: string;
  position: { x: number; y: number };
  output?: string;
  status?: string;
  execution_time?: number;
  error_message?: string;
  executed_at?: string;
}

interface Workflow {
  id: string;
  name: string;
  blocks: Block[];
  edges: any[];
  created_at: string;
  execution_status?: string;
  validation?: any;
  execution_plan?: string[];
}

interface AITool {
  name: string;
  description: string;
  examples: string[];
}

interface SystemStatus {
  metrics: {
    datasets_count: number;
    blocks_count: number;
    workflows_count: number;
    active_executions: number;
    completed_executions: number;
    failed_executions: number;
    python_sessions: number;
  };
  services: Record<string, string>;
  ai_model: string;
}

interface SessionState {
  variables: Record<string, any>;
  dataframes: string[];
  imports: string[];
  last_activity: string;
  execution_count: number;
}

interface ExecutionHistory {
  block_id: string;
  block_content: string;
  status: string;
  execution_time: number;
  executed_at: string;
  output: string;
  error_message: string | null;
}

export default function DemoPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [currentDataset, setCurrentDataset] = useState<Dataset | null>(null);
  const [prompt, setPrompt] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentWorkflow, setCurrentWorkflow] = useState<Workflow | null>(null);
  const [viewMode, setViewMode] = useState<"notebook" | "dag">("notebook");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [aiTools, setAiTools] = useState<Record<string, AITool>>({});
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [showSystemStatus, setShowSystemStatus] = useState(false);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [sessionState, setSessionState] = useState<SessionState | null>(null);
  const [executionHistory, setExecutionHistory] = useState<ExecutionHistory[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // WebSocket connection
  const wsRef = useRef<WebSocket | null>(null);
  const workflowWsRef = useRef<WebSocket | null>(null);

  // ReactFlow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  // Fetch AI tools and system status on component mount
  useEffect(() => {
    fetchAITools();
    fetchSystemStatus();
    fetchWorkflows();
    connectWebSocket();
    
    return () => {
      // Cleanup WebSocket connections
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (workflowWsRef.current) {
        workflowWsRef.current.close();
      }
    };
  }, []);

  // Connect to WebSocket for real-time updates
  const connectWebSocket = () => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      
      // Send ping to test connection
      ws.send(JSON.stringify({ type: 'ping' }));
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
    };
    
    wsRef.current = ws;
  };

  // Connect to workflow-specific WebSocket
  const connectWorkflowWebSocket = (workflowId: string) => {
    if (workflowWsRef.current) {
      workflowWsRef.current.close();
    }
    
    const ws = new WebSocket(`ws://localhost:8000/ws/workflow/${workflowId}`);
    
    ws.onopen = () => {
      console.log(`Workflow WebSocket connected for workflow: ${workflowId}`);
    };
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        handleWorkflowWebSocketMessage(data);
      } catch (error) {
        console.error('Error parsing workflow WebSocket message:', error);
      }
    };
    
    ws.onclose = () => {
      console.log(`Workflow WebSocket disconnected for workflow: ${workflowId}`);
    };
    
    wsRef.current = ws;
  };

  // Handle general WebSocket messages
  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'pong':
        console.log('WebSocket ping-pong successful');
        break;
      case 'system_metrics':
        // Update system metrics in real-time
        if (systemStatus) {
          setSystemStatus(prev => prev ? {
            ...prev,
            metrics: data
          } : null);
        }
        break;
      default:
        console.log('Received WebSocket message:', data);
    }
  };

  // Handle workflow-specific WebSocket messages
  const handleWorkflowWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'pong':
        console.log('Workflow WebSocket ping-pong successful');
        break;
      case 'workflow_status':
        // Update workflow status
        if (currentWorkflow && currentWorkflow.id === data.workflow_id) {
          setCurrentWorkflow(prev => prev ? {
            ...prev,
            execution_status: data.status
          } : null);
        }
        break;
      case 'execution_started':
        console.log('Execution started for workflow:', data.workflow_id);
        break;
      case 'execution_completed':
        console.log('Execution completed:', data.success ? 'Success' : 'Failed');
        break;
      case 'block_executed':
        // Update block execution status in real-time
        updateBlockExecutionStatus(data);
        break;
      case 'dag_updated':
        // Update DAG visualization in real-time
        updateDAGVisualization(data);
        break;
      default:
        console.log('Received workflow WebSocket message:', data);
    }
  };

  // Update block execution status
  const updateBlockExecutionStatus = (data: any) => {
    if (currentWorkflow) {
      setCurrentWorkflow(prev => {
        if (!prev) return prev;
        
        const updatedBlocks = prev.blocks.map(block => {
          if (block.id === data.block_id) {
            return {
              ...block,
              status: data.status,
              output: data.output,
              error_message: data.error_message,
              execution_time: data.execution_time,
              executed_at: data.executed_at
            };
          }
          return block;
        });
        
        return { ...prev, blocks: updatedBlocks };
      });
    }
  };

  // Update DAG visualization
  const updateDAGVisualization = (data: any) => {
    if (data.workflow_id === currentWorkflow?.id) {
      // Convert nodes to ReactFlow format
      const flowNodes: Node[] = data.nodes.map((node: any) => ({
        id: node.id,
        type: 'default',
        position: node.position,
        data: { 
          label: node.content.substring(0, 50) + '...',
          content: node.content,
          type: node.type,
          status: node.status
        },
        style: {
          background: node.status === 'completed' ? '#10b981' : 
                     node.status === 'failed' ? '#ef4444' : '#6b7280',
          color: 'white',
          border: '2px solid #374151',
          borderRadius: '8px',
          padding: '10px',
          minWidth: '200px'
        }
      }));
      
      // Convert edges to ReactFlow format
      const flowEdges: Edge[] = data.edges.map((edge: any) => ({
        id: edge.id,
        source: edge.source,
        target: edge.target,
        type: edge.type || 'default',
        style: { stroke: '#6b7280', strokeWidth: 2 }
      }));
      
      setNodes(flowNodes);
      setEdges(flowEdges);
    }
  };

  const fetchAITools = async () => {
    try {
      const response = await fetch('http://localhost:8000/ai/tools');
      const result = await response.json();
      if (result.success) {
        setAiTools(result.tools);
      }
    } catch (error) {
      console.error('Error fetching AI tools:', error);
    }
  };

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/system/status');
      const result = await response.json();
      if (result.success) {
        setSystemStatus(result);
      }
    } catch (error) {
      console.error('Error fetching system status:', error);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await fetch('http://localhost:8000/workflows');
      const result = await response.json();
      if (result.success) {
        setWorkflows(result.workflows);
      }
    } catch (error) {
      console.error('Error fetching workflows:', error);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      alert('Please upload a CSV file');
      return;
    }

    setUploadedFile(file);
    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload-dataset', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      
      if (result.success) {
        const newDataset: Dataset = {
          id: result.dataset_id,
          name: file.name,
          rows: result.dataset_info.rows,
          columns: result.dataset_info.columns,
          uploaded_at: new Date().toISOString(),
          file_size: result.dataset_info.file_size,
          column_types: result.dataset_info.column_types,
        };
        
        setDatasets([...datasets, newDataset]);
        setCurrentDataset(newDataset);
        alert('Dataset uploaded successfully!');
        
        // Refresh system status
        fetchSystemStatus();
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Error uploading dataset');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAISubmit = async () => {
    if (!prompt.trim() || !currentDataset) {
      alert('Please provide a prompt and select a dataset');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await fetch('http://localhost:8000/ai/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          dataset_id: currentDataset.id,
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        const newWorkflow: Workflow = {
          id: result.workflow_id,
          name: result.message,
          blocks: result.blocks,
          edges: result.dag_info?.edges || [],
          created_at: new Date().toISOString(),
          validation: result.validation,
          execution_plan: result.execution_plan,
        };

        setCurrentWorkflow(newWorkflow);
        
        // Add to workflows list
        setWorkflows(prev => [...prev, newWorkflow]);

        // Convert blocks to ReactFlow nodes
        const flowNodes: Node[] = result.blocks.map((block: Block) => ({
          id: block.id,
          type: 'default',
          position: block.position,
          data: { 
            label: block.content.substring(0, 50) + '...',
            content: block.content,
            type: block.type,
            status: block.status || 'pending'
          },
          style: {
            background: '#6b7280',
            color: 'white',
            border: '2px solid #374151',
            borderRadius: '8px',
            padding: '10px',
            minWidth: '200px'
          }
        }));
        
        // Convert edges to ReactFlow format
        const flowEdges: Edge[] = (result.dag_info?.edges || []).map((edge: any) => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type || 'default',
          style: { stroke: '#6b7280', strokeWidth: 2 }
        }));
        
        setNodes(flowNodes);
        setEdges(flowEdges);

        // Connect to workflow-specific WebSocket
        connectWorkflowWebSocket(result.workflow_id);

        // Fetch session state and execution history
        fetchWorkflowSession(result.workflow_id);
        fetchExecutionHistory(result.workflow_id);
        
        alert('AI workflow created successfully!');
        
        // Refresh system status
        fetchSystemStatus();
      }
    } catch (error) {
      console.error('AI processing error:', error);
      alert('Error processing AI request');
    } finally {
      setIsProcessing(false);
    }
  };

  // Fetch workflow session state
  const fetchWorkflowSession = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/workflows/${workflowId}/session`);
      const result = await response.json();
      if (result.success && result.session_state) {
        setSessionState(result.session_state);
      }
    } catch (error) {
      console.error('Error fetching workflow session:', error);
    }
  };

  // Fetch execution history
  const fetchExecutionHistory = async (workflowId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/workflows/${workflowId}/execution-history`);
      const result = await response.json();
      if (result.success) {
        setExecutionHistory(result.execution_history);
      }
    } catch (error) {
      console.error('Error fetching execution history:', error);
    }
  };

  // Execute a block
  const executeBlock = async (blockId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/blocks/${blockId}/execute`, {
        method: 'POST',
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Update the block in current workflow
        if (currentWorkflow) {
          setCurrentWorkflow(prev => {
            if (!prev) return prev;
            
            const updatedBlocks = prev.blocks.map(block => {
              if (block.id === blockId) {
                return {
                  ...block,
                  status: result.status,
                  output: result.output,
                  error_message: result.error_message,
                  execution_time: result.execution_time,
                  executed_at: result.executed_at
                };
              }
              return block;
            });
            
            return { ...prev, blocks: updatedBlocks };
          });
        }
        
        // Update session state
        if (result.session_state) {
          setSessionState(result.session_state);
        }
        
        // Refresh execution history
        if (currentWorkflow) {
          fetchExecutionHistory(currentWorkflow.id);
        }
        
        alert(`Block executed successfully! Status: ${result.status}`);
      } else {
        alert(`Block execution failed: ${result.error_message}`);
      }
    } catch (error) {
      console.error('Error executing block:', error);
      alert('Error executing block');
    }
  };

  // Add a new block
  const addNewBlock = async () => {
    if (!currentWorkflow) return;
    
    try {
      const newBlockData = {
        type: "code",
        content: "# New code block\nimport pandas as pd\n\n# Your code here\nprint('Hello from new block!')",
        position: { x: 100, y: 100 + (currentWorkflow.blocks.length * 150) }
      };
      
      const response = await fetch(`http://localhost:8000/workflows/${currentWorkflow.id}/blocks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newBlockData),
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Refresh the workflow to get the new block
        const workflowResponse = await fetch(`http://localhost:8000/workflows/${currentWorkflow.id}`);
        const workflowResult = await workflowResponse.json();
        
        if (workflowResult.success) {
          setCurrentWorkflow(workflowResult.workflow);
          
          // Update ReactFlow nodes
          const flowNodes: Node[] = workflowResult.workflow.blocks.map((block: Block) => ({
            id: block.id,
            type: 'default',
            position: block.position,
            data: { 
              label: block.content.substring(0, 50) + '...',
              content: block.content,
              type: block.type,
              status: block.status || 'pending'
            },
            style: {
              background: '#6b7280',
              color: 'white',
              border: '2px solid #374151',
              borderRadius: '8px',
              padding: '10px',
              minWidth: '200px'
            }
          }));
          
          setNodes(flowNodes);
        }
        
        alert('New block added successfully!');
      } else {
        alert('Error adding new block');
      }
    } catch (error) {
      console.error('Error adding new block:', error);
      alert('Error adding new block');
    }
  };

  // Edit block content
  const editBlock = async (blockId: string, newContent: string) => {
    try {
      const response = await fetch(`http://localhost:8000/blocks/${blockId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: newContent,
        }),
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Update the block in current workflow
        if (currentWorkflow) {
          setCurrentWorkflow(prev => {
            if (!prev) return prev;
            
            const updatedBlocks = prev.blocks.map(block => {
              if (block.id === blockId) {
                return { ...block, content: newContent };
              }
              return block;
            });
            
            return { ...prev, blocks: updatedBlocks };
          });
        }
        
        // Update ReactFlow nodes
        setNodes(prev => prev.map(node => 
          node.id === blockId 
            ? { ...node, data: { ...node.data, content: newContent, label: newContent.substring(0, 50) + '...' } }
            : node
        ));
        
        alert('Block updated successfully!');
      } else {
        alert('Error updating block');
      }
    } catch (error) {
      console.error('Error updating block:', error);
      alert('Error updating block');
    }
  };

  // Delete a block
  const deleteBlock = async (blockId: string) => {
    if (!confirm('Are you sure you want to delete this block?')) return;
    
    try {
      const response = await fetch(`http://localhost:8000/blocks/${blockId}`, {
        method: 'DELETE',
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Remove block from current workflow
        if (currentWorkflow) {
          setCurrentWorkflow(prev => {
            if (!prev) return prev;
            
            const updatedBlocks = prev.blocks.filter(block => block.id !== blockId);
            return { ...prev, blocks: updatedBlocks };
          });
        }
        
        // Remove from ReactFlow
        setNodes(prev => prev.filter(node => node.id !== blockId));
        setEdges(prev => prev.filter(edge => edge.source !== blockId && edge.target !== blockId));
        
        alert('Block deleted successfully!');
      } else {
        alert('Error deleting block');
      }
    } catch (error) {
      console.error('Error deleting block:', error);
      alert('Error deleting block');
    }
  };

  const executeWorkflow = async () => {
    if (!currentWorkflow) return;

    try {
      const response = await fetch(`http://localhost:8000/workflows/${currentWorkflow.id}/execute`, {
        method: 'POST',
      });

      const result = await response.json();
      
      if (result.success) {
        // Update all blocks with their outputs
        const updatedBlocks = currentWorkflow.blocks.map(block => {
          const executionResult = result.results.find((r: any) => r.block_id === block.id);
          return executionResult ? { 
            ...block, 
            output: executionResult.output, 
            status: executionResult.status,
            execution_time: executionResult.execution_time,
            error_message: executionResult.error_message
          } : block;
        });
        
        setCurrentWorkflow({
          ...currentWorkflow,
          blocks: updatedBlocks,
          execution_status: 'completed',
        });

        // Update ReactFlow nodes
        setNodes(prev => prev.map(node => {
          const executionResult = result.results.find((r: any) => r.block_id === node.id);
          return executionResult ? { ...node, data: { ...node.data, status: executionResult.status } } : node;
        }));
        
        // Refresh system status
        fetchSystemStatus();
      }
    } catch (error) {
      console.error('Workflow execution error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">AI Notebook Demo</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowSystemStatus(!showSystemStatus)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span>System Status</span>
              </button>
              <button
                onClick={() => setViewMode(viewMode === "notebook" ? "dag" : "notebook")}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                {viewMode === "notebook" ? (
                  <>
                    <GitBranch className="w-4 h-4" />
                    <span>DAG View</span>
                  </>
                ) : (
                  <>
                    <Code className="w-4 h-4" />
                    <span>Notebook View</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* System Status Panel */}
      {showSystemStatus && systemStatus && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">System Status</h2>
              <button
                onClick={() => setShowSystemStatus(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h3 className="font-semibold text-blue-800">Datasets</h3>
                <p className="text-2xl font-bold text-blue-600">{systemStatus.metrics.datasets_count}</p>
              </div>
              <div className="bg-green-50 p-4 rounded-lg">
                <h3 className="font-semibold text-green-800">Blocks</h3>
                <p className="text-2xl font-bold text-green-600">{systemStatus.metrics.blocks_count}</p>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <h3 className="font-semibold text-purple-800">Workflows</h3>
                <p className="text-2xl font-bold text-purple-600">{systemStatus.metrics.workflows_count}</p>
              </div>
              <div className="bg-orange-50 p-4 rounded-lg">
                <h3 className="font-semibold text-orange-800">Python Sessions</h3>
                <p className="text-2xl font-bold text-orange-600">{systemStatus.metrics.python_sessions}</p>
              </div>
            </div>
            
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Services Status</h3>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(systemStatus.services).map(([service, status]) => (
                  <div key={service} className="flex items-center space-x-2">
                    <div className={`w-2 h-2 rounded-full ${status === 'active' ? 'bg-green-500' : 'bg-red-500'}`} />
                    <span className="text-sm capitalize">{service.replace('_', ' ')}</span>
                    <span className={`text-xs px-2 py-1 rounded ${status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="mb-6">
              <h3 className="font-semibold mb-2">AI Model</h3>
              <p className="text-sm text-gray-600">{systemStatus.ai_model}</p>
            </div>
            
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Execution Metrics</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{systemStatus.metrics.completed_executions}</p>
                  <p className="text-sm text-gray-600">Completed</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{systemStatus.metrics.failed_executions}</p>
                  <p className="text-sm text-gray-600">Failed</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-600">{systemStatus.metrics.active_executions}</p>
                  <p className="text-sm text-gray-600">Active</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* WebSocket Connection Status */}
      <div className="fixed top-4 right-4 z-40">
        <div className={`flex items-center space-x-2 px-3 py-2 rounded-full text-sm font-medium ${
          isConnected 
            ? 'bg-green-100 text-green-800 border border-green-200' 
            : 'bg-red-100 text-red-800 border border-red-200'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Session State Panel */}
      {sessionState && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Database className="w-5 h-5 mr-2" />
            Session State
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Variables</h4>
              <div className="bg-gray-50 p-3 rounded text-sm">
                {Object.keys(sessionState.variables).length > 0 ? (
                  Object.entries(sessionState.variables).map(([key, value]) => (
                    <div key={key} className="mb-1">
                      <span className="font-mono text-blue-600">{key}</span>
                      <span className="text-gray-500"> = </span>
                      <span className="font-mono text-green-600">{String(value)}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-gray-500">No variables</span>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">DataFrames</h4>
              <div className="bg-gray-50 p-3 rounded text-sm">
                {sessionState.dataframes.length > 0 ? (
                  sessionState.dataframes.map((df, index) => (
                    <div key={index} className="mb-1">
                      <span className="font-mono text-purple-600">{df}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-gray-500">No dataframes</span>
                )}
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-700 mb-2">Imports</h4>
              <div className="bg-gray-50 p-3 rounded text-sm">
                {sessionState.imports.length > 0 ? (
                  sessionState.imports.map((imp, index) => (
                    <div key={index} className="mb-1">
                      <span className="font-mono text-orange-600">{imp}</span>
                    </div>
                  ))
                ) : (
                  <span className="text-gray-500">No imports</span>
                )}
              </div>
            </div>
          </div>
          
          <div className="mt-3 text-sm text-gray-500">
            Last activity: {new Date(sessionState.last_activity).toLocaleString()} | 
            Executions: {sessionState.execution_count}
          </div>
        </div>
      )}

      {/* Execution History Panel */}
      {executionHistory.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h3 className="text-lg font-semibold mb-3 flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Execution History
          </h3>
          
          <div className="space-y-3">
            {executionHistory.map((execution, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium text-gray-700">Block {execution.block_id.substring(0, 8)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      execution.status === 'completed' ? 'bg-green-100 text-green-800' :
                      execution.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {execution.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(execution.executed_at).toLocaleString()}
                  </div>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  {execution.block_content.substring(0, 100)}...
                </div>
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>Execution time: {execution.execution_time?.toFixed(3)}s</span>
                  {execution.error_message && (
                    <span className="text-red-600">Error: {execution.error_message}</span>
                  )}
                </div>
                
                {execution.output && (
                  <details className="mt-2">
                    <summary className="cursor-pointer text-sm font-medium text-blue-600 hover:text-blue-800">
                      View Output
                    </summary>
                    <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                      {execution.output}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex h-[calc(100vh-4rem)]">
        {/* AI Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 p-6 overflow-y-auto">
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Assistant</h2>
              
              {/* Dataset Upload */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  Upload Dataset (CSV)
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="mx-auto h-8 w-8 text-gray-400 mb-2" />
                    <p className="text-sm text-gray-600">
                      {isUploading ? (
                        <span className="flex items-center justify-center">
                          <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          Uploading...
                        </span>
                      ) : (
                        "Click to upload CSV file"
                      )}
                    </p>
                  </label>
                </div>
              </div>

              {/* Dataset Selection */}
              {datasets.length > 0 && (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Select Dataset
                  </label>
                  <select
                    value={currentDataset?.id || ""}
                    onChange={(e) => {
                      const dataset = datasets.find(d => d.id === e.target.value);
                      setCurrentDataset(dataset || null);
                    }}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Choose a dataset...</option>
                    {datasets.map((dataset) => (
                      <option key={dataset.id} value={dataset.id}>
                        {dataset.name} ({dataset.rows} rows, {dataset.columns} cols)
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* AI Tools Display */}
              {Object.keys(aiTools).length > 0 && (
                <div className="space-y-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Available AI Tools
                  </label>
                  <div className="space-y-2">
                    {Object.entries(aiTools).map(([key, tool]) => (
                      <div key={key} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Code className="w-4 h-4 text-blue-600" />
                          <span className="text-sm font-medium text-gray-900">{tool.name}</span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">{tool.description}</p>
                        <div className="text-xs text-gray-500">
                          Examples: {tool.examples.slice(0, 2).join(', ')}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* AI Prompt */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-700">
                  What would you like to do?
                </label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="e.g., Analyze the dataset, create visualizations, clean the data..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={4}
                />
                <button
                  onClick={handleAISubmit}
                  disabled={!prompt.trim() || !currentDataset || isProcessing}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Processing...</span>
                    </>
                  ) : (
                    <>
                      <Brain className="w-4 h-4" />
                      <span>Ask AI</span>
                    </>
                  )}
                </button>
              </div>

              {/* Current Workflow Info */}
              {currentWorkflow && (
                <div className="border-t pt-4">
                  <h3 className="text-sm font-medium text-gray-700 mb-2">Current Workflow</h3>
                  <p className="text-xs text-gray-600 mb-3">{currentWorkflow.name}</p>
                  
                  {/* Validation Status */}
                  {currentWorkflow.validation && (
                    <div className="mb-3 p-2 bg-gray-50 rounded text-xs">
                      <div className="flex items-center space-x-2 mb-1">
                        {currentWorkflow.validation.is_valid ? (
                          <CheckCircle className="w-3 h-3 text-green-600" />
                        ) : (
                          <AlertTriangle className="w-3 h-3 text-red-600" />
                        )}
                        <span className="font-medium">Validation:</span>
                        <span className={currentWorkflow.validation.is_valid ? "text-green-600" : "text-red-600"}>
                          {currentWorkflow.validation.is_valid ? "Valid" : "Invalid"}
                        </span>
                      </div>
                      {currentWorkflow.validation.error && (
                        <p className="text-red-600">{currentWorkflow.validation.error}</p>
                      )}
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <button
                      onClick={executeWorkflow}
                      className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors text-sm"
                    >
                      <Play className="w-4 h-4" />
                      <span>Execute All</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-hidden">
          {viewMode === "notebook" ? (
            /* Notebook View */
            <div className="h-full overflow-y-auto p-6">
              {currentWorkflow ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-2xl font-bold text-gray-900">Notebook</h2>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        {currentWorkflow.blocks.length} blocks
                      </span>
                      {currentWorkflow.execution_status && (
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          currentWorkflow.execution_status === 'completed' 
                            ? 'bg-green-100 text-green-800' 
                            : currentWorkflow.execution_status === 'running'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {currentWorkflow.execution_status}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {currentWorkflow.blocks.map((block, index) => (
                    <div key={block.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                      <div className="bg-gray-50 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <Code className="w-4 h-4 text-gray-600" />
                          <span className="text-sm font-medium text-gray-700">
                            Block {index + 1} - {block.type}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          {block.status === 'completed' && (
                            <CheckCircle className="w-4 h-4 text-green-600" />
                          )}
                          {block.status === 'failed' && (
                            <AlertTriangle className="w-4 h-4 text-red-600" />
                          )}
                          {block.status === 'pending' && (
                            <AlertCircle className="w-4 h-4 text-yellow-600" />
                          )}
                          {block.execution_time && (
                            <div className="flex items-center space-x-1 text-xs text-gray-500">
                              <Clock className="w-3 h-3" />
                              <span>{block.execution_time.toFixed(2)}s</span>
                            </div>
                          )}
                          <button
                            onClick={() => executeBlock(block.id)}
                            disabled={block.status === 'completed' || block.status === 'running'}
                            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
                          >
                            {block.status === 'completed' ? 'Completed' : block.status === 'running' ? 'Running' : 'Execute'}
                          </button>
                          <button
                            onClick={() => deleteBlock(block.id)}
                            className="px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                      
                      <div className="p-4">
                        <textarea
                          value={block.content}
                          onChange={(e) => {
                            // Update local state immediately for responsive editing
                            if (currentWorkflow) {
                              const updatedBlocks = currentWorkflow.blocks.map(b => 
                                b.id === block.id ? { ...b, content: e.target.value } : b
                              );
                              setCurrentWorkflow({ ...currentWorkflow, blocks: updatedBlocks });
                            }
                          }}
                          onBlur={(e) => editBlock(block.id, e.target.value)}
                          className="w-full h-32 p-3 border border-gray-300 rounded font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="Enter your Python code here..."
                        />
                        
                        {block.output && (
                          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
                            <div className="text-sm font-medium text-green-800 mb-2">Output:</div>
                            <div className="text-sm text-green-700 whitespace-pre-wrap">{block.output}</div>
                          </div>
                        )}
                        
                        {block.error_message && (
                          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
                            <div className="text-sm font-medium text-red-800 mb-2">Error:</div>
                            <div className="text-sm text-red-700">{block.error_message}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {/* Add New Block Button */}
                  <div className="text-center">
                    <button
                      onClick={addNewBlock}
                      className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center space-x-2 mx-auto"
                    >
                      <Code className="w-5 h-5" />
                      <span>Add New Block</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="h-full flex items-center justify-center">
                  <div className="text-center">
                    <Brain className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Workflow Yet</h3>
                    <p className="text-gray-500">
                      Upload a dataset and ask the AI to create a workflow for you.
                    </p>
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* DAG View */
            <div className="h-full">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                fitView
              >
                <Background />
                <Controls />
              </ReactFlow>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
