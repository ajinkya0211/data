import React, { useState } from 'react';
import { Edit2, Trash2, CheckCircle, Save, X, Type } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MarkdownBlock = ({ block, onEdit, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(block.content);

  const handleSave = () => {
    onEdit(block.id, content);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setContent(block.content);
    setIsEditing(false);
  };

  return (
    <div className="notebook-block border-l-4 border-l-blue-500">
      {/* Google Colab-style Text Cell Header */}
      <div className="flex items-center justify-between mb-3 pb-2 border-b border-notebook-border/30">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Type className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-notebook-text">
              Text Cell
            </span>
          </div>
          
          {/* Cell Info */}
          <div className="flex items-center space-x-2 text-xs text-notebook-text/60">
            <span>Markdown</span>
            <span>•</span>
            <span>{content.split('\n').length} lines</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="p-1 text-green-400 hover:text-green-300 hover:bg-green-500/10 rounded transition-colors"
                title="Save changes"
              >
                <Save className="w-4 h-4" />
              </button>
              <button
                onClick={handleCancel}
                className="p-1 text-notebook-text/70 hover:text-notebook-text hover:bg-notebook-border rounded transition-colors"
                title="Cancel editing"
              >
                <X className="w-4 h-4" />
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="p-1 text-notebook-text/70 hover:text-notebook-text hover:bg-notebook-border rounded transition-colors"
                title="Edit text"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={onDelete}
                className="p-1 text-notebook-text/70 hover:text-red-400 hover:bg-red-500/10 rounded transition-colors"
                title="Delete cell"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Content - Google Colab Style */}
      <div className="mb-3">
        {isEditing ? (
          <div className="space-y-3">
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full h-32 input-field font-mono text-sm resize-none border-2 border-blue-500/30 focus:border-blue-500"
              placeholder="Enter your markdown content..."
            />
            <div className="text-xs text-notebook-text/50">
              💡 Use markdown syntax: **bold**, *italic*, `code`, [links](url), etc.
            </div>
          </div>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              className="text-notebook-text"
              components={{
                h1: ({node, ...props}) => <h1 className="text-xl font-bold text-notebook-text mb-3" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-lg font-bold text-notebook-text mb-2" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-base font-bold text-notebook-text mb-2" {...props} />,
                p: ({node, ...props}) => <p className="text-notebook-text mb-2 leading-relaxed" {...props} />,
                code: ({node, inline, ...props}) => 
                  inline ? 
                    <code className="bg-notebook-bg px-1 py-0.5 rounded text-sm font-mono text-orange-400" {...props} /> :
                    <code className="block bg-notebook-bg p-3 rounded text-sm font-mono text-notebook-text border border-notebook-border/30" {...props} />,
                pre: ({node, ...props}) => <pre className="bg-notebook-bg p-3 rounded text-sm font-mono text-notebook-text border border-notebook-border/30 overflow-x-auto" {...props} />,
                blockquote: ({node, ...props}) => <blockquote className="border-l-4 border-blue-500 pl-4 italic text-notebook-text/80" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc list-inside text-notebook-text mb-2" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal list-inside text-notebook-text mb-2" {...props} />,
                li: ({node, ...props}) => <li className="text-notebook-text mb-1" {...props} />,
                a: ({node, ...props}) => <a className="text-blue-400 hover:text-blue-300 underline" {...props} />,
                strong: ({node, ...props}) => <strong className="font-bold text-notebook-text" {...props} />,
                em: ({node, ...props}) => <em className="italic text-notebook-text" {...props} />,
              }}
            >
              {content}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Cell Footer - Google Colab Style */}
      <div className="mt-3 pt-2 border-t border-notebook-border/20">
        <div className="flex items-center justify-between text-xs text-notebook-text/50">
          <span>Markdown • Rich Text</span>
          <span>Last edited: {isEditing ? 'Editing...' : 'Just now'}</span>
        </div>
      </div>
    </div>
  );
};

export default MarkdownBlock;
