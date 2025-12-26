import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, GitBranch, Code, FileText, Clock } from 'lucide-react';
import { useNotebook } from '../contexts/NotebookContext';
import ReactFlow, { 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from 'react-flow-renderer';
import 'react-flow-renderer/dist/style.css';
import toast from 'react-hot-toast';

const DAGView = () => {
  const { dagData, getDAGData, isConnected } = useNotebook();
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Transform DAG data to React Flow format
  const transformDataToFlow = useCallback((data) => {
    if (!data) return;

    // Transform nodes
    const flowNodes = data.nodes.map((node, index) => ({
      id: node.id,
      type: 'customNode',
      position: { x: node.position.x, y: node.position.y },
      data: {
        ...node,
        label: `Block ${index + 1}`,
        onNodeClick: () => handleNodeClick(node)
      },
      style: getNodeStyle(node),
    }));

    // Transform edges
    const flowEdges = data.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed },
      style: getEdgeStyle(edge),
      label: edge.type.replace('_', ' ').toUpperCase(),
      labelStyle: { fontSize: 10, fill: '#c9d1d9' },
      data: edge,
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, []);

  // Load DAG data
  const loadDAGData = useCallback(async () => {
    if (!isConnected) return;
    
    setLoading(true);
    try {
      const data = await getDAGData();
      transformDataToFlow(data);
    } catch (error) {
      toast.error('Failed to load DAG data');
      console.error('Failed to load DAG data:', error);
    } finally {
      setLoading(false);
    }
  }, [getDAGData, isConnected, transformDataToFlow]);

  useEffect(() => {
    loadDAGData();
  }, [loadDAGData]);



  // Get node styling based on status and type
  const getNodeStyle = (node) => {
    const baseStyle = {
      padding: 16,
      borderRadius: 8,
      border: '2px solid',
      minWidth: 200,
      fontSize: 12,
    };

    // Status-based colors
    const statusColors = {
      'pending': '#6b7280',
      'running': '#f59e0b',
      'completed': '#10b981',
      'failed': '#ef4444',
      'skipped': '#8b5cf6',
    };

    const statusColor = statusColors[node.status] || '#6b7280';

    return {
      ...baseStyle,
      borderColor: statusColor,
      backgroundColor: '#161b22',
      color: '#c9d1d9',
    };
  };

  // Get edge styling based on dependency type
  const getEdgeStyle = (edge) => {
    const typeColors = {
      'variable_dependency': '#3b82f6',
      'function_dependency': '#10b981',
      'import_dependency': '#f59e0b',
      'data_flow': '#8b5cf6',
      'execution_order': '#6b7280',
    };

    return {
      stroke: typeColors[edge.type] || '#6b7280',
      strokeWidth: 2,
    };
  };

  // Handle node click
  const handleNodeClick = (node) => {
    setSelectedNode(node);
    setShowDetails(true);
  };

  // Custom node component
  const CustomNode = ({ data }) => {
    const getStatusIcon = () => {
      const icons = {
        'pending': <Clock className="w-4 h-4 text-gray-400" />,
        'running': <RefreshCw className="w-4 h-4 text-yellow-500 animate-spin" />,
        'completed': <Code className="w-4 h-4 text-green-500" />,
        'failed': <FileText className="w-4 h-4 text-red-500" />,
        'skipped': <GitBranch className="w-4 h-4 text-purple-500" />,
      };
      return icons[data.status] || icons.pending;
    };

    const getTypeIcon = () => {
      if (data.type === 'code') return <Code className="w-4 h-4" />;
      if (data.type === 'markdown') return <FileText className="w-4 h-4" />;
      return <GitBranch className="w-4 h-4" />;
    };

    return (
      <div className="custom-node">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="font-medium">{data.label}</span>
          </div>
          {getTypeIcon()}
        </div>

        {/* Content Preview */}
        <div className="text-xs text-gray-400 mb-2 line-clamp-2">
          {data.content_preview}
        </div>

        {/* Metadata */}
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-500">
            Dependencies: {data.dependencies_count}
          </span>
          <span className="text-gray-500">
            Order: {data.execution_order || 'N/A'}
          </span>
        </div>

        {/* Complexity Score */}
        {data.estimated_complexity && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500">Complexity:</span>
              <span className="text-blue-400">{data.estimated_complexity}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-1 mt-1">
              <div 
                className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                style={{ width: `${Math.min(data.estimated_complexity * 10, 100)}%` }}
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  // Node types
  const nodeTypes = {
    customNode: CustomNode,
  };

  // Handle edge connection
  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  if (!isConnected) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <div className="w-8 h-8 bg-red-500 rounded-full"></div>
          </div>
          <h2 className="text-xl font-semibold text-notebook-text mb-2">
            Backend Disconnected
          </h2>
          <p className="text-notebook-text/70">
            Please ensure the backend server is running
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-notebook-bg">
      {/* Header */}
      <div className="bg-notebook-surface border-b border-notebook-border px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-notebook-text">DAG Visualization</h1>
            <p className="text-notebook-text/70 text-sm mt-1">
              Interactive dependency graph with enhanced analysis
            </p>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={loadDAGData}
              disabled={loading}
              className="btn-primary"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
            
            {dagData && (
              <div className="flex items-center space-x-4 text-sm text-notebook-text/70">
                <div className="flex items-center space-x-2">
                  <GitBranch className="w-4 h-4" />
                  <span>{dagData.nodes?.length || 0} Blocks</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Code className="w-4 h-4" />
                  <span>{dagData.edges?.length || 0} Dependencies</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* DAG Content */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center bg-notebook-bg/80 z-10">
            <div className="text-center">
              <RefreshCw className="w-8 h-8 text-notebook-accent animate-spin mx-auto mb-2" />
              <p className="text-notebook-text">Loading DAG data...</p>
            </div>
          </div>
        ) : nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <GitBranch className="w-16 h-16 text-notebook-text/30 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-notebook-text mb-2">
                No DAG data available
              </h3>
              <p className="text-notebook-text/70 mb-4">
                Create some blocks in the notebook to see the dependency graph
              </p>
              <button
                onClick={loadDAGData}
                className="btn-primary"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </button>
            </div>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
            attributionPosition="bottom-left"
            className="bg-notebook-bg"
          >
            <Background color="#30363d" gap={20} />
            <Controls className="bg-notebook-surface border border-notebook-border rounded-lg" />
            <MiniMap 
              className="bg-notebook-surface border border-notebook-border rounded-lg"
              nodeColor="#58a6ff"
              maskColor="#0d1117"
            />
          </ReactFlow>
        )}
      </div>

      {/* Node Details Panel */}
      {showDetails && selectedNode && (
        <div className="absolute right-4 top-20 w-80 bg-notebook-surface border border-notebook-border rounded-lg shadow-lg max-h-96 overflow-y-auto">
          <div className="p-4 border-b border-notebook-border">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-notebook-text">
                Block Details
              </h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-notebook-text/70 hover:text-notebook-text"
              >
                ×
              </button>
            </div>
          </div>
          
          <div className="p-4 space-y-4">
            {/* Basic Info */}
            <div>
              <h4 className="text-sm font-medium text-notebook-text mb-2">Basic Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-notebook-text/70">Type:</span>
                  <span className="text-notebook-text">{selectedNode.type}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-notebook-text/70">Status:</span>
                  <span className={`px-2 py-1 rounded text-xs ${
                    selectedNode.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    selectedNode.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    selectedNode.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {selectedNode.status}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-notebook-text/70">Execution Order:</span>
                  <span className="text-notebook-text">{selectedNode.execution_order || 'N/A'}</span>
                </div>
              </div>
            </div>

            {/* Dependencies */}
            <div>
              <h4 className="text-sm font-medium text-notebook-text mb-2">Dependencies</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-notebook-text/70">Dependencies:</span>
                  <span className="text-notebook-text">{selectedNode.dependencies_count}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-notebook-text/70">Dependents:</span>
                  <span className="text-notebook-text">{selectedNode.dependents_count}</span>
                </div>
              </div>
            </div>

            {/* Enhanced Analysis */}
            {selectedNode.libraries_required && selectedNode.libraries_required.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-notebook-text mb-2">Libraries Required</h4>
                <div className="flex flex-wrap gap-1">
                  {selectedNode.libraries_required.map((lib, index) => (
                    <span key={index} className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                      {lib}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {selectedNode.files_read && selectedNode.files_read.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-notebook-text mb-2">Files Read</h4>
                <div className="space-y-1">
                  {selectedNode.files_read.map((file, index) => (
                    <div key={index} className="text-xs text-notebook-text/70 flex items-center space-x-2">
                      <FileText className="w-3 h-3" />
                      <span>{file}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedNode.execution_requirements && selectedNode.execution_requirements.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-notebook-text mb-2">Execution Requirements</h4>
                <div className="space-y-1">
                  {selectedNode.execution_requirements.map((req, index) => (
                    <div key={index} className="text-xs text-notebook-text/70 bg-notebook-bg p-2 rounded">
                      {req}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Content Preview */}
            <div>
              <h4 className="text-sm font-medium text-notebook-text mb-2">Content Preview</h4>
              <div className="bg-notebook-bg p-2 rounded text-xs font-mono text-notebook-text/80 max-h-24 overflow-y-auto">
                {selectedNode.content_preview}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DAGView;
