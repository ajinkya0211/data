import React, { useState } from 'react';
import { Plus, Download, Upload } from 'lucide-react';
import { useNotebook } from '../contexts/NotebookContext';
import CodeBlock from './CodeBlock';
import MarkdownBlock from './MarkdownBlock';
import toast from 'react-hot-toast';

const Notebook = () => {
  const { 
    currentWorkflow, 
    blocks, 
    addBlock, 
    executeBlock,
    isConnected 
  } = useNotebook();
  
  const [blockType, setBlockType] = useState('code');
  const [showAddBlock, setShowAddBlock] = useState(false);

  const handleAddBlock = async (type, content) => {
    if (!currentWorkflow) {
      toast.error('Please create or select a workflow first');
      return;
    }

    try {
      const blockData = {
        type,
        content,
        position: { x: 100, y: 100 + (blocks.length * 50) }
      };
      
      await addBlock(currentWorkflow.id, blockData);
      setShowAddBlock(false);
    } catch (error) {
      console.error('Failed to add block:', error);
    }
  };

  const handleExecuteBlock = async (blockId) => {
    try {
      await executeBlock(blockId);
    } catch (error) {
      console.error('Failed to execute block:', error);
    }
  };

  const handleExportNotebook = () => {
    if (!currentWorkflow) {
      toast.error('No workflow to export');
      return;
    }

    const notebookData = {
      metadata: {
        name: currentWorkflow.name,
        description: currentWorkflow.description,
        created_at: new Date().toISOString(),
        version: '1.0.0'
      },
      blocks: blocks.map(block => ({
        id: block.id,
        type: block.type,
        content: block.content,
        position: block.position,
        status: block.status
      }))
    };

    const blob = new Blob([JSON.stringify(notebookData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentWorkflow.name}.ipynb`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast.success('Notebook exported successfully!');
  };

  const handleImportNotebook = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        // TODO: Implement import logic
        toast.success('Notebook imported successfully!');
      } catch (error) {
        toast.error('Invalid notebook file');
      }
    };
    reader.readAsText(file);
  };

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
            Please ensure the backend server is running on localhost:8000
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
            <h1 className="text-2xl font-bold text-notebook-text">
              {currentWorkflow ? currentWorkflow.name : 'Untitled Workflow'}
            </h1>
            {currentWorkflow && (
              <p className="text-notebook-text/70 text-sm mt-1">
                {currentWorkflow.description || 'No description'}
              </p>
            )}
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Import/Export */}
            <div className="flex items-center space-x-2">
              <label className="btn-secondary cursor-pointer">
                <Upload className="w-4 h-4 mr-2" />
                Import
                <input
                  type="file"
                  accept=".ipynb,.json"
                  onChange={handleImportNotebook}
                  className="hidden"
                />
              </label>
              <button
                onClick={handleExportNotebook}
                disabled={!currentWorkflow}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
            
            {/* Add Block Button */}
            <button
              onClick={() => setShowAddBlock(!showAddBlock)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Block
            </button>
          </div>
        </div>
      </div>

      {/* Add Block Panel */}
      {showAddBlock && (
        <div className="bg-notebook-surface border-b border-notebook-border px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm text-notebook-text">Block Type:</label>
              <select
                value={blockType}
                onChange={(e) => setBlockType(e.target.value)}
                className="input-field text-sm"
              >
                <option value="code">Code</option>
                <option value="markdown">Markdown</option>
              </select>
            </div>
            
            <button
              onClick={() => handleAddBlock(blockType, blockType === 'code' ? '# Your code here\nprint("Hello, World!")' : '# Your markdown here\n\nThis is a markdown block.')}
              className="btn-primary text-sm px-3 py-1"
            >
              Create Block
            </button>
            
            <button
              onClick={() => setShowAddBlock(false)}
              className="btn-secondary text-sm px-3 py-1"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Notebook Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {blocks.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-24 h-24 bg-notebook-surface border-2 border-dashed border-notebook-border rounded-lg flex items-center justify-center mx-auto mb-4">
              <Plus className="w-12 h-12 text-notebook-text/30" />
            </div>
            <h3 className="text-lg font-medium text-notebook-text mb-2">
              No blocks yet
            </h3>
            <p className="text-notebook-text/70 mb-4">
              Start building your workflow by adding code or markdown blocks
            </p>
            <button
              onClick={() => setShowAddBlock(true)}
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Block
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {blocks.map((block, index) => (
              <div key={block.id} className="relative group">
                {block.type === 'code' ? (
                  <CodeBlock
                    block={block}
                    onExecute={() => handleExecuteBlock(block.id)}
                    onDelete={() => {/* TODO: Implement delete */}}
                    onCopy={() => {
                      navigator.clipboard.writeText(block.content);
                      toast.success('Code copied to clipboard!');
                    }}
                  />
                ) : (
                  <MarkdownBlock
                    block={block}
                    onEdit={() => {/* TODO: Implement edit */}}
                    onDelete={() => {/* TODO: Implement delete */}}
                  />
                )}
                
                {/* Block Number */}
                <div className="absolute -left-8 top-4 w-6 h-6 bg-notebook-surface border border-notebook-border rounded-full flex items-center justify-center text-xs text-notebook-text/50 font-mono">
                  {index + 1}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Notebook;