import React, { useState, useRef } from 'react';
import { Play, Trash2, Copy, CheckCircle, XCircle, Clock, AlertCircle, Info } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { useNotebook } from '../contexts/NotebookContext';

const CodeBlock = ({ block, onExecute, onDelete, onCopy }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);
  const [output, setOutput] = useState(block.output || '');
  const [error, setError] = useState(block.error || '');
  const [executionTime, setExecutionTime] = useState(block.execution_time || 0);
  const [variables, setVariables] = useState(block.variables_defined || {});
  const [imports, setImports] = useState(block.imports_added || []);
  const [executionCount, setExecutionCount] = useState(block.execution_count || 0);
  
  const editorRef = useRef(null);
  const { executeBlock } = useNotebook();

  const handleExecute = async () => {
    if (!block.content.trim()) {
      setError('Cannot execute empty code cell');
      return;
    }

    setIsExecuting(true);
    setError('');
    setOutput('');
    
    try {
      const result = await executeBlock(block.id);
      
      if (result.success) {
        setOutput(result.output || '');
        setVariables(result.variables_defined || {});
        setImports(result.imports_added || []);
        setExecutionTime(result.execution_time || 0);
        setExecutionCount(prev => prev + 1);
      } else {
        setError(result.error || 'Execution failed');
      }
    } catch (err) {
      setError(err.message || 'Execution failed');
    } finally {
      setIsExecuting(false);
    }
  };

  const getStatusIcon = () => {
    if (isExecuting) return <Clock className="w-4 h-4 text-yellow-500 animate-spin" />;
    if (error) return <XCircle className="w-4 h-4 text-red-500" />;
    if (output || executionCount > 0) return <CheckCircle className="w-4 h-4 text-green-500" />;
    return <Info className="w-4 h-4 text-notebook-text/50" />;
  };

  const getStatusColor = () => {
    if (isExecuting) return 'border-yellow-500';
    if (error) return 'border-red-500';
    if (output || executionCount > 0) return 'border-green-500';
    return 'border-notebook-border';
  };

  const getExecutionInfo = () => {
    if (isExecuting) return 'Executing...';
    if (error) return 'Error';
    if (executionCount > 0) return `Executed ${executionCount} time${executionCount > 1 ? 's' : ''}`;
    return 'Not executed';
  };

  return (
    <div className={`notebook-block ${getStatusColor()} border-l-4 border-l-current`}>
      {/* Google Colab-style Cell Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-notebook-border/30">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-sm font-medium text-notebook-text">
              Code Cell
            </span>
            {executionCount > 0 && (
              <span className="text-xs text-notebook-text/50 font-mono">
                [{executionCount}]
              </span>
            )}
          </div>
          
          {/* Execution Info */}
          <div className="flex items-center space-x-2 text-xs text-notebook-text/60">
            <span>{getExecutionInfo()}</span>
            {executionTime > 0 && (
              <>
                <span>•</span>
                <span>{executionTime.toFixed(3)}s</span>
              </>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={onCopy}
            className="p-1 text-notebook-text/70 hover:text-notebook-text hover:bg-notebook-border rounded transition-colors"
            title="Copy code"
          >
            <Copy className="w-4 h-4" />
          </button>
          
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className="p-1 text-notebook-text/70 hover:text-green-400 hover:bg-green-500/10 rounded transition-colors disabled:opacity-50"
            title="Run cell"
          >
            <Play className="w-4 h-4" />
          </button>
          
          <button
            onClick={onDelete}
            className="p-1 text-notebook-text/70 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
            title="Delete cell"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Code Editor - Google Colab Style */}
      <div className="mb-3">
        <Editor
          height="200px"
          defaultLanguage="python"
          defaultValue={block.content}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: 'JetBrains Mono, Fira Code, monospace',
            lineNumbers: 'on',
            roundedSelection: false,
            scrollBeyondLastLine: false,
            automaticLayout: true,
            wordWrap: 'on',
            folding: true,
            showFoldingControls: 'always',
            renderLineHighlight: 'all',
            selectOnLineNumbers: true,
            glyphMargin: true,
          }}
          onMount={(editor) => {
            editorRef.current = editor;
          }}
        />
      </div>

      {/* Execution Results - Google Colab Style */}
      {(output || error || Object.keys(variables).length > 0 || imports.length > 0) && (
        <div className="border-t border-notebook-border/30 pt-3">
          {/* Variables */}
          {Object.keys(variables).length > 0 && (
            <div className="mb-3">
              <h4 className="text-sm font-medium text-notebook-text mb-2 flex items-center space-x-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span>Variables Defined</span>
              </h4>
              <div className="bg-notebook-bg border border-notebook-border/30 rounded p-3 font-mono text-xs">
                {Object.entries(variables).map(([key, value]) => (
                  <div key={key} className="text-notebook-accent mb-1">
                    <span className="text-green-400">{key}</span>
                    <span className="text-notebook-text"> = </span>
                    <span className="text-blue-400">{JSON.stringify(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Imports */}
          {imports.length > 0 && (
            <div className="mb-3">
              <h4 className="text-sm font-medium text-notebook-text mb-2 flex items-center space-x-2">
                <Info className="w-4 h-4 text-blue-500" />
                <span>Imports Added</span>
              </h4>
              <div className="bg-notebook-bg border border-notebook-border/30 rounded p-3 font-mono text-xs">
                {imports.map((imp, index) => (
                  <div key={index} className="text-notebook-accent">
                    {imp}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Output */}
          {output && (
            <div className="mb-3">
              <h4 className="text-sm font-medium text-notebook-text mb-2 flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Output</span>
              </h4>
              <div className="bg-notebook-bg border border-notebook-border/30 rounded p-3 font-mono text-xs text-notebook-text whitespace-pre-wrap">
                {output}
              </div>
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="mb-3">
              <h4 className="text-sm font-medium text-red-400 mb-2 flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 text-red-500" />
                <span>Error</span>
              </h4>
              <div className="bg-red-500/10 border border-red-500/20 rounded p-3 font-mono text-xs text-red-400 whitespace-pre-wrap">
                {error}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Cell Footer - Google Colab Style */}
      <div className="mt-3 pt-2 border-t border-notebook-border/20">
        <div className="flex items-center justify-between text-xs text-notebook-text/50">
          <span>Python 3 • Data Science</span>
          <span>Last executed: {executionCount > 0 ? 'Just now' : 'Never'}</span>
        </div>
      </div>
    </div>
  );
};

export default CodeBlock;
