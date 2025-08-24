"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Brain, 
  Play, 
  Square, 
  RotateCcw,
  Download,
  Upload,
  Code,
  Database,
  BarChart3,
  MessageSquare,
  CheckCircle,
  AlertCircle,
  Clock,
  Zap
} from "lucide-react";

interface ExecutionResult {
  id: string;
  timestamp: string;
  command: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  output?: string;
  error?: string;
  executionTime?: number;
  codeGenerated?: string;
}

interface NotebookCell {
  id: string;
  type: 'code' | 'markdown' | 'output';
  content: string;
  executionCount?: number;
  status: 'idle' | 'running' | 'completed' | 'error';
  output?: string;
  error?: string;
}

export default function MinimalAIPage() {
  const [command, setCommand] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionHistory, setExecutionHistory] = useState<ExecutionResult[]>([]);
  const [notebookCells, setNotebookCells] = useState<NotebookCell[]>([]);
  const [activeTab, setActiveTab] = useState("interface");
  const [websocket, setWebsocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  
  const outputRef = useRef<HTMLDivElement>(null);

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    
    ws.onopen = () => {
      setConnectionStatus('connected');
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };
    
    ws.onclose = () => {
      setConnectionStatus('disconnected');
      console.log('WebSocket disconnected');
    };
    
    ws.onerror = (error) => {
      setConnectionStatus('disconnected');
      console.error('WebSocket error:', error);
    };
    
    setWebsocket(ws);
    
    return () => {
      ws.close();
    };
  }, []);

  const handleWebSocketMessage = (data: any) => {
    if (data.type === 'execution_update') {
      updateExecutionStatus(data);
    } else if (data.type === 'notebook_update') {
      updateNotebookCells(data);
    }
  };

  const updateExecutionStatus = (data: any) => {
    setExecutionHistory(prev => 
      prev.map(item => 
        item.id === data.execution_id 
          ? { ...item, ...data }
          : item
      )
    );
  };

  const updateNotebookCells = (data: any) => {
    if (data.cells) {
      setNotebookCells(data.cells);
    }
  };

  const executeCommand = async () => {
    if (!command.trim() || isExecuting) return;

    const executionId = `exec_${Date.now()}`;
    const newExecution: ExecutionResult = {
      id: executionId,
      timestamp: new Date().toISOString(),
      command: command,
      status: 'pending'
    };

    setExecutionHistory(prev => [newExecution, ...prev]);
    setIsExecuting(true);

    try {
      // Send command to backend via WebSocket
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'ai_command',
          command: command,
          execution_id: executionId
        }));
      }

      // Simulate backend processing (remove this in real implementation)
      setTimeout(() => {
        setExecutionHistory(prev => 
          prev.map(item => 
            item.id === executionId 
              ? { 
                  ...item, 
                  status: 'completed',
                  output: `Executed: ${command}\n\nGenerated code:\nimport pandas as pd\nimport numpy as np\n\n# Data processing code here\nprint("Command executed successfully")`,
                  executionTime: 2.5,
                  codeGenerated: `import pandas as pd\nimport numpy as np\n\n# Data processing code here\nprint("Command executed successfully")`
                }
              : item
          )
        );
        setIsExecuting(false);
      }, 2000);

    } catch (error) {
      setExecutionHistory(prev => 
        prev.map(item => 
          item.id === executionId 
            ? { ...item, status: 'error', error: error.message }
            : item
        )
      );
      setIsExecuting(false);
    }

    setCommand("");
  };

  const clearHistory = () => {
    setExecutionHistory([]);
    setNotebookCells([]);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'running': return <RotateCcw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
      case 'running': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'completed': return 'bg-green-500/10 text-green-500 border-green-500/20';
      case 'error': return 'bg-red-500/10 text-red-500 border-red-500/20';
      default: return 'bg-gray-500/10 text-gray-500 border-gray-500/20';
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">AI Notebook - Minimal Interface</h1>
              <p className="text-muted-foreground">Direct AI command execution with real-time results</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <Badge 
              variant="outline" 
              className={connectionStatus === 'connected' ? 'bg-green-500/10 text-green-500 border-green-500/20' : 'bg-red-500/10 text-red-500 border-red-500/20'}
            >
              {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
            </Badge>
            <Button variant="outline" size="sm" onClick={clearHistory}>
              <RotateCcw className="w-4 h-4 mr-2" />
              Clear
            </Button>
          </div>
        </div>

        {/* Main Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="interface">AI Interface</TabsTrigger>
            <TabsTrigger value="notebook">Notebook View</TabsTrigger>
            <TabsTrigger value="history">Execution History</TabsTrigger>
          </TabsList>

          {/* AI Interface Tab */}
          <TabsContent value="interface" className="space-y-6">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <MessageSquare className="w-5 h-5" />
                  <span>AI Command Interface</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex space-x-3">
                  <Input
                    placeholder="Enter your AI command (e.g., 'import data from data_dirty.csv and clean it')"
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && executeCommand()}
                    className="flex-1"
                    disabled={isExecuting}
                  />
                  <Button 
                    onClick={executeCommand} 
                    disabled={!command.trim() || isExecuting}
                    className="min-w-[120px]"
                  >
                    {isExecuting ? (
                      <>
                        <RotateCcw className="w-4 h-4 mr-2 animate-spin" />
                        Executing...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 mr-2" />
                        Execute
                      </>
                    )}
                  </Button>
                </div>
                
                <div className="text-sm text-muted-foreground">
                  <p>Example commands:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>"Import data from data_dirty.csv and show first 5 rows"</li>
                    <li>"Clean the dataset by removing duplicates and handling missing values"</li>
                    <li>"Create a visualization of the data distribution"</li>
                    <li>"Calculate summary statistics for all numeric columns"</li>
                  </ul>
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-500/10 rounded-lg flex items-center justify-center">
                      <Upload className="w-5 h-5 text-blue-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Import Data</h3>
                      <p className="text-sm text-muted-foreground">Load datasets for analysis</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center">
                      <Database className="w-5 h-5 text-green-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Data Analysis</h3>
                      <p className="text-sm text-muted-foreground">Explore and analyze data</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-purple-500/10 rounded-lg flex items-center justify-center">
                      <BarChart3 className="w-5 h-5 text-purple-500" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Visualization</h3>
                      <p className="text-sm text-muted-foreground">Create charts and plots</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Notebook View Tab */}
          <TabsContent value="notebook" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Code className="w-5 h-5" />
                  <span>Notebook Output</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {notebookCells.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Code className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No notebook cells yet. Execute a command to see results.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {notebookCells.map((cell, index) => (
                      <div key={cell.id} className="border border-border/50 rounded-lg p-4">
                        <div className="flex items-center space-x-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            {cell.type === 'code' ? 'Code' : cell.type === 'markdown' ? 'Markdown' : 'Output'}
                          </Badge>
                          {cell.executionCount && (
                            <span className="text-sm text-muted-foreground">
                              In [{cell.executionCount}]
                            </span>
                          )}
                          <Badge 
                            variant="outline" 
                            className={getStatusColor(cell.status)}
                          >
                            {cell.status}
                          </Badge>
                        </div>
                        
                        {cell.type === 'code' && (
                          <pre className="bg-muted p-3 rounded text-sm font-mono overflow-x-auto">
                            {cell.content}
                          </pre>
                        )}
                        
                        {cell.output && (
                          <div className="mt-3 p-3 bg-muted/50 rounded border-l-4 border-green-500">
                            <div className="text-sm font-semibold text-green-600 mb-2">Output:</div>
                            <pre className="text-sm whitespace-pre-wrap">{cell.output}</pre>
                          </div>
                        )}
                        
                        {cell.error && (
                          <div className="mt-3 p-3 bg-red-500/10 rounded border-l-4 border-red-500">
                            <div className="text-sm font-semibold text-red-600 mb-2">Error:</div>
                            <pre className="text-sm text-red-600 whitespace-pre-wrap">{cell.error}</pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Execution History Tab */}
          <TabsContent value="history" className="space-y-4">
            <Card className="border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Execution History</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {executionHistory.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">
                    <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>No commands executed yet. Start by entering a command above.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {executionHistory.map((execution) => (
                      <div key={execution.id} className="border border-border/50 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(execution.status)}
                            <Badge 
                              variant="outline" 
                              className={getStatusColor(execution.status)}
                            >
                              {execution.status}
                            </Badge>
                            {execution.executionTime && (
                              <span className="text-sm text-muted-foreground">
                                {execution.executionTime}s
                              </span>
                            )}
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {new Date(execution.timestamp).toLocaleTimeString()}
                          </span>
                        </div>
                        
                        <div className="mb-3">
                          <div className="text-sm font-semibold mb-1">Command:</div>
                          <div className="bg-muted p-2 rounded text-sm">
                            {execution.command}
                          </div>
                        </div>
                        
                        {execution.codeGenerated && (
                          <div className="mb-3">
                            <div className="text-sm font-semibold mb-1">Generated Code:</div>
                            <pre className="bg-muted p-3 rounded text-sm font-mono overflow-x-auto">
                              {execution.codeGenerated}
                            </pre>
                          </div>
                        )}
                        
                        {execution.output && (
                          <div className="mb-3">
                            <div className="text-sm font-semibold mb-1">Output:</div>
                            <pre className="bg-muted/50 p-3 rounded text-sm whitespace-pre-wrap">
                              {execution.output}
                            </pre>
                          </div>
                        )}
                        
                        {execution.error && (
                          <div className="mb-3">
                            <div className="text-sm font-semibold mb-1">Error:</div>
                            <div className="bg-red-500/10 p-3 rounded text-sm text-red-600 border-l-4 border-red-500">
                              {execution.error}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
