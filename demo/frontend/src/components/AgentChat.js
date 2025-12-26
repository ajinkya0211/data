import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Code, MessageSquare, Settings, RefreshCw, ChevronDown, ChevronRight, X, ChevronLeft } from 'lucide-react';
import { useNotebook } from '../contexts/NotebookContext';
import toast from 'react-hot-toast';
import axios from 'axios';

const AgentChat = () => {
  const { isConnected, currentWorkflow, addBlock } = useNotebook();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('planner');
  const [showSettings, setShowSettings] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [showQuickActions, setShowQuickActions] = useState(false);
  const messagesEndRef = useRef(null);

  const agents = [
    { id: 'planner', name: 'Planner', description: 'Strategic workflow planning', icon: Sparkles, color: 'text-blue-500' },
    { id: 'executor', name: 'Executor', description: 'Code execution & implementation', icon: Code, color: 'text-green-500' },
    { id: 'analyzer', name: 'Analyzer', description: 'Data analysis & insights', icon: MessageSquare, color: 'text-purple-500' },
    { id: 'visualizer', name: 'Visualizer', description: 'Charts & visualizations', icon: Bot, color: 'text-orange-500' },
    { id: 'debugger', name: 'Debugger', description: 'Error detection & fixes', icon: RefreshCw, color: 'text-red-500' },
    { id: 'optimizer', name: 'Optimizer', description: 'Performance optimization', icon: Settings, color: 'text-yellow-500' },
  ];

  const quickActions = [
    "Create a data analysis block",
    "Add error handling to this code",
    "Generate a visualization",
    "Optimize this function",
    "Debug this issue",
    "Explain this code",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Add welcome message
  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: 'welcome',
          type: 'agent',
          content: `Hi! I'm your AI coding assistant. I can help you with:

• **Code Generation** - Create Python blocks
• **Debugging** - Fix errors and issues  
• **Optimization** - Improve performance
• **Analysis** - Data insights & visualizations

What would you like to work on?`,
          timestamp: new Date(),
          agent: 'assistant'
        }
      ]);
    }
  }, [messages.length]);

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send message to AI agent
      const response = await axios.post('http://localhost:8000/ai/process', {
        message: input,
        agent_type: selectedAgent,
        workflow_id: currentWorkflow?.id,
        context: {
          current_workflow: currentWorkflow,
          selected_agent: selectedAgent,
        }
      });

      const aiResponse = {
        id: (Date.now() + 1).toString(),
        content: response.data.response,
        timestamp: new Date(),
        agent: selectedAgent,
        suggestions: response.data.suggestions || [],
        code_blocks: response.data.code_blocks || [],
      };

      setMessages(prev => [...prev, aiResponse]);

      // If AI generated code blocks, offer to add them
      if (response.data.code_blocks && response.data.code_blocks.length > 0) {
        toast.success(`AI generated ${response.data.code_blocks.length} code blocks!`);
      }

    } catch (error) {
      console.error('Failed to get AI response:', error);
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: `Sorry, I encountered an error: ${error.message}. Please try again or check if the backend is running.`,
        timestamp: new Date(),
        agent: 'error',
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const addCodeBlock = async (code, description) => {
    if (!currentWorkflow) {
      toast.error('Please create or select a workflow first');
      return;
    }

    try {
      await addBlock(currentWorkflow.id, {
        type: 'code',
        content: code,
        position: { x: 100, y: 100 }
      });
      toast.success('Code block added to workflow!');
    } catch (error) {
      toast.error('Failed to add code block');
    }
  };

  const handleQuickAction = (action) => {
    setInput(action);
    setShowQuickActions(false);
  };

  const renderMessage = (message) => {
    const isAgent = message.type === 'agent' || message.agent;
    const agentInfo = agents.find(a => a.id === message.agent);

    return (
      <div
        key={message.id}
        className={`flex ${isAgent ? 'justify-start' : 'justify-end'} mb-3`}
      >
        <div className={`flex max-w-full ${isAgent ? 'flex-row' : 'flex-row-reverse'}`}>
          {/* Avatar */}
          <div className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center ${
            isAgent 
              ? 'bg-primary-600 text-white' 
              : 'bg-notebook-accent text-notebook-bg'
          }`}>
            {isAgent ? (
              agentInfo ? <agentInfo.icon className="w-3 h-3" /> : <Bot className="w-3 h-3" />
            ) : (
              <User className="w-3 h-3" />
            )}
          </div>

          {/* Message Content */}
          <div className={`mx-2 ${isAgent ? 'text-left' : 'text-right'} max-w-[calc(100%-2rem)]`}>
            {/* Agent Name */}
            {isAgent && agentInfo && (
              <div className="flex items-center space-x-2 mb-1">
                <span className={`text-xs font-medium ${agentInfo.color}`}>
                  {agentInfo.name}
                </span>
              </div>
            )}

            {/* Message Text */}
            <div className={`rounded-lg px-3 py-2 text-xs ${
              isAgent 
                ? 'bg-cursor-chat border border-notebook-border' 
                : 'bg-primary-600 text-white'
            }`}>
              <div className="whitespace-pre-wrap">
                {message.content}
              </div>
            </div>

            {/* Code Blocks */}
            {message.code_blocks && message.code_blocks.length > 0 && (
              <div className="mt-2 space-y-2">
                {message.code_blocks.map((block, index) => (
                  <div key={index} className="bg-notebook-bg border border-notebook-border rounded p-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-medium text-notebook-text">
                        Code Block {index + 1}
                      </span>
                      <button
                        onClick={() => addCodeBlock(block.code, block.description)}
                        className="btn-primary text-xs px-2 py-1"
                      >
                        Add
                      </button>
                    </div>
                    <pre className="text-xs text-notebook-text/80 bg-notebook-surface p-2 rounded overflow-x-auto">
                      <code>{block.code}</code>
                    </pre>
                  </div>
                ))}
              </div>
            )}

            {/* Suggestions */}
            {message.suggestions && message.suggestions.length > 0 && (
              <div className="mt-2">
                <p className="text-xs text-notebook-text/60 mb-1">Suggestions:</p>
                <div className="flex flex-wrap gap-1">
                  {message.suggestions.map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => setInput(suggestion)}
                      className="text-xs bg-notebook-surface border border-notebook-border rounded px-2 py-1 text-notebook-accent hover:bg-notebook-border transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  if (!isConnected) {
    return (
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="text-center">
          <div className="w-8 h-8 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
          </div>
          <p className="text-xs text-notebook-text/70">
            Backend disconnected
          </p>
        </div>
      </div>
    );
  }

  if (isCollapsed) {
    return (
      <div className="flex-1 flex flex-col">
        {/* Collapsed Header */}
        <div className="p-3 border-b border-notebook-border">
          <button
            onClick={() => setIsCollapsed(false)}
            className="w-full flex items-center justify-center space-x-2 text-notebook-text hover:text-notebook-accent transition-colors"
          >
            <Bot className="w-5 h-5" />
            <span className="text-sm font-medium">AI Assistant</span>
            <ChevronLeft className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-notebook-border">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Bot className="w-5 h-5 text-primary-500" />
            <h3 className="text-sm font-semibold text-notebook-text">AI Assistant</h3>
          </div>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setShowQuickActions(!showQuickActions)}
              className="p-1 text-notebook-text/70 hover:text-notebook-accent hover:bg-notebook-border rounded transition-colors"
              title="Quick actions"
            >
              <Sparkles className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-1 text-notebook-text/70 hover:text-notebook-accent hover:bg-notebook-border rounded transition-colors"
              title="Settings"
            >
              <Settings className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsCollapsed(true)}
              className="p-1 text-notebook-text/70 hover:text-notebook-accent hover:bg-notebook-border rounded transition-colors"
              title="Collapse"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Agent Selection */}
        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="w-full input-field text-xs"
        >
          {agents.map(agent => (
            <option key={agent.id} value={agent.id}>
              {agent.name}
            </option>
          ))}
        </select>

        {/* Quick Actions */}
        {showQuickActions && (
          <div className="mt-3 p-2 bg-notebook-bg rounded border border-notebook-border">
            <p className="text-xs text-notebook-text/60 mb-2">Quick Actions:</p>
            <div className="space-y-1">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickAction(action)}
                  className="w-full text-left text-xs text-notebook-accent hover:text-notebook-text hover:bg-notebook-border p-1 rounded transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-3 p-2 bg-notebook-bg rounded border border-notebook-border">
            <h4 className="text-xs font-medium text-notebook-text mb-2">Agent Capabilities</h4>
            <div className="space-y-2">
              {agents.map(agent => (
                <div
                  key={agent.id}
                  className={`p-2 rounded text-xs cursor-pointer transition-colors ${
                    selectedAgent === agent.id
                      ? 'bg-primary-500/20 border border-primary-500/30'
                      : 'hover:bg-notebook-border'
                  }`}
                  onClick={() => setSelectedAgent(agent.id)}
                >
                  <div className="flex items-center space-x-2">
                    <agent.icon className={`w-3 h-3 ${agent.color}`} />
                    <span className="font-medium text-notebook-text">{agent.name}</span>
                  </div>
                  <p className="text-notebook-text/70 mt-1">{agent.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.map(renderMessage)}
        
        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex max-w-full">
              <div className="flex-shrink-0 w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                <Bot className="w-3 h-3 text-white" />
              </div>
              <div className="mx-2">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-xs font-medium text-blue-500">
                    {agents.find(a => a.id === selectedAgent)?.name || 'AI'}
                  </span>
                </div>
                <div className="bg-cursor-chat border border-notebook-border rounded-lg px-3 py-2">
                  <div className="flex items-center space-x-2">
                    <RefreshCw className="w-3 h-3 text-notebook-accent animate-spin" />
                    <span className="text-xs text-notebook-text">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-notebook-border">
        <div className="flex items-end space-x-2">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Ask ${agents.find(a => a.id === selectedAgent)?.name || 'AI'}...`}
              className="input-field w-full resize-none text-xs"
              rows={2}
              style={{ minHeight: '60px', maxHeight: '120px' }}
            />
          </div>
          
          <button
            onClick={handleSendMessage}
            disabled={!input.trim() || isLoading}
            className="btn-primary p-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex items-center justify-between mt-2">
          <p className="text-xs text-notebook-text/50">
            Enter to send
          </p>
          <p className="text-xs text-notebook-text/50">
            {agents.find(a => a.id === selectedAgent)?.name}
          </p>
        </div>
      </div>
    </div>
  );
};

export default AgentChat;
