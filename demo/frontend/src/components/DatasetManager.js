import React, { useState } from 'react';
import { Upload, Download, Trash2, Eye, FileText, Database, Plus, Search, Filter } from 'lucide-react';
import { useNotebook } from '../contexts/NotebookContext';
import toast from 'react-hot-toast';

const DatasetManager = () => {
  const { datasets, uploadDataset, isConnected } = useNotebook();
  const [showUpload, setShowUpload] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [uploadForm, setUploadForm] = useState({
    name: '',
    description: '',
    file: null
  });

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadForm(prev => ({
        ...prev,
        file,
        name: file.name.replace(/\.[^/.]+$/, '') // Remove extension for default name
      }));
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    
    if (!uploadForm.file || !uploadForm.name.trim()) {
      toast.error('Please select a file and provide a name');
      return;
    }

    try {
      await uploadDataset(uploadForm.file, uploadForm.name.trim(), uploadForm.description.trim());
      setUploadForm({ name: '', description: '', file: null });
      setShowUpload(false);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleDownload = (dataset) => {
    // Create a download link for the dataset
    const link = document.createElement('a');
    link.href = `data:text/csv;charset=utf-8,${encodeURIComponent(dataset.content || '')}`;
    link.download = `${dataset.name}.csv`;
    link.click();
    toast.success('Download started');
  };

  const handleDelete = async (datasetId) => {
    if (window.confirm('Are you sure you want to delete this dataset?')) {
      try {
        // TODO: Implement delete API call
        toast.success('Dataset deleted successfully');
      } catch (error) {
        toast.error('Failed to delete dataset');
      }
    }
  };

  const filteredDatasets = datasets.filter(dataset => {
    const matchesSearch = dataset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         dataset.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || dataset.type === filterType;
    return matchesSearch && matchesFilter;
  });

  const getFileIcon = (filename) => {
    const ext = filename.split('.').pop()?.toLowerCase();
    if (ext === 'csv') return <FileText className="w-5 h-5 text-green-500" />;
    if (ext === 'json') return <FileText className="w-5 h-5 text-blue-500" />;
    if (ext === 'xlsx' || ext === 'xls') return <FileText className="w-5 h-5 text-orange-500" />;
    return <Database className="w-5 h-5 text-gray-500" />;
  };

  const getFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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
            <h1 className="text-2xl font-bold text-notebook-text">Dataset Manager</h1>
            <p className="text-notebook-text/70 text-sm mt-1">
              Upload, manage, and organize your datasets
            </p>
          </div>
          
          <button
            onClick={() => setShowUpload(true)}
            className="btn-primary"
          >
            <Plus className="w-4 h-4 mr-2" />
            Upload Dataset
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-notebook-surface border-b border-notebook-border px-6 py-4">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-notebook-text/50" />
              <input
                type="text"
                placeholder="Search datasets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field w-full pl-10"
              />
            </div>
          </div>

          {/* Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-notebook-text/50" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="input-field text-sm"
            >
              <option value="all">All Types</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
              <option value="excel">Excel</option>
            </select>
          </div>

          {/* Stats */}
          <div className="text-sm text-notebook-text/70">
            {filteredDatasets.length} of {datasets.length} datasets
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUpload && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-notebook-surface border border-notebook-border rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-notebook-text mb-4">Upload Dataset</h3>
            
            <form onSubmit={handleUpload} className="space-y-4">
              {/* File Input */}
              <div>
                <label className="block text-sm font-medium text-notebook-text mb-2">
                  Dataset File
                </label>
                <div className="border-2 border-dashed border-notebook-border rounded-lg p-4 text-center hover:border-notebook-accent transition-colors">
                  <input
                    type="file"
                    accept=".csv,.json,.xlsx,.xls"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <Upload className="w-8 h-8 text-notebook-accent mx-auto mb-2" />
                    <p className="text-notebook-text">
                      {uploadForm.file ? uploadForm.file.name : 'Click to select file'}
                    </p>
                    <p className="text-xs text-notebook-text/50 mt-1">
                      Supports CSV, JSON, Excel files
                    </p>
                  </label>
                </div>
              </div>

              {/* Name Input */}
              <div>
                <label className="block text-sm font-medium text-notebook-text mb-2">
                  Dataset Name
                </label>
                <input
                  type="text"
                  value={uploadForm.name}
                  onChange={(e) => setUploadForm(prev => ({ ...prev, name: e.target.value }))}
                  className="input-field w-full"
                  placeholder="Enter dataset name"
                  required
                />
              </div>

              {/* Description Input */}
              <div>
                <label className="block text-sm font-medium text-notebook-text mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm(prev => ({ ...prev, description: e.target.value }))}
                  className="input-field w-full"
                  placeholder="Describe your dataset"
                  rows={3}
                />
              </div>

              {/* Actions */}
              <div className="flex space-x-3 pt-4">
                <button
                  type="submit"
                  className="btn-primary flex-1"
                >
                  Upload Dataset
                </button>
                <button
                  type="button"
                  onClick={() => setShowUpload(false)}
                  className="btn-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Dataset List */}
      <div className="flex-1 overflow-y-auto p-6">
        {filteredDatasets.length === 0 ? (
          <div className="text-center py-12">
            <Database className="w-16 h-16 text-notebook-text/30 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-notebook-text mb-2">
              {datasets.length === 0 ? 'No datasets yet' : 'No datasets match your search'}
            </h3>
            <p className="text-notebook-text/70 mb-4">
              {datasets.length === 0 
                ? 'Upload your first dataset to get started'
                : 'Try adjusting your search terms or filters'
              }
            </p>
            {datasets.length === 0 && (
              <button
                onClick={() => setShowUpload(true)}
                className="btn-primary"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload Your First Dataset
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredDatasets.map((dataset) => (
              <div
                key={dataset.id}
                className="bg-notebook-surface border border-notebook-border rounded-lg p-4 hover:border-notebook-accent transition-colors"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    {getFileIcon(dataset.name)}
                    <div>
                      <h4 className="font-medium text-notebook-text truncate max-w-32">
                        {dataset.name}
                      </h4>
                      <p className="text-xs text-notebook-text/50">
                        {getFileSize(dataset.size || 0)}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-1">
                    <button
                      onClick={() => setSelectedDataset(dataset)}
                      className="p-1 text-notebook-text/70 hover:text-notebook-accent hover:bg-notebook-border rounded"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDownload(dataset)}
                      className="p-1 text-notebook-text/70 hover:text-green-400 hover:bg-green-500/10 rounded"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(dataset.id)}
                      className="p-1 text-notebook-text/70 hover:text-red-400 hover:bg-red-500/10 rounded"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                {dataset.description && (
                  <p className="text-sm text-notebook-text/70 mb-3 line-clamp-2">
                    {dataset.description}
                  </p>
                )}

                {/* Metadata */}
                <div className="flex items-center justify-between text-xs text-notebook-text/50">
                  <span>Uploaded {new Date(dataset.uploaded_at).toLocaleDateString()}</span>
                  <span className="px-2 py-1 bg-notebook-bg rounded">
                    {dataset.type || 'Unknown'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Dataset Details Modal */}
      {selectedDataset && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-notebook-surface border border-notebook-border rounded-lg p-6 w-full max-w-2xl mx-4 max-h-96 overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-notebook-text">
                Dataset Details: {selectedDataset.name}
              </h3>
              <button
                onClick={() => setSelectedDataset(null)}
                className="text-notebook-text/70 hover:text-notebook-text"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Basic Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-notebook-text/70">Type</label>
                  <p className="text-notebook-text">{selectedDataset.type || 'Unknown'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-notebook-text/70">Size</label>
                  <p className="text-notebook-text">{getFileSize(selectedDataset.size || 0)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-notebook-text/70">Uploaded</label>
                  <p className="text-notebook-text">
                    {new Date(selectedDataset.uploaded_at).toLocaleString()}
                  </p>
                </div>
                <div>
                  <label className="text-sm font-medium text-notebook-text/70">ID</label>
                  <p className="text-notebook-text font-mono text-xs">{selectedDataset.id}</p>
                </div>
              </div>

              {/* Description */}
              {selectedDataset.description && (
                <div>
                  <label className="text-sm font-medium text-notebook-text/70">Description</label>
                  <p className="text-notebook-text">{selectedDataset.description}</p>
                </div>
              )}

              {/* Preview */}
              <div>
                <label className="text-sm font-medium text-notebook-text/70 mb-2 block">
                  Preview
                </label>
                <div className="bg-notebook-bg border border-notebook-border rounded p-3 max-h-32 overflow-y-auto">
                  <pre className="text-xs text-notebook-text/80 font-mono">
                    {selectedDataset.content ? 
                      selectedDataset.content.substring(0, 500) + 
                      (selectedDataset.content.length > 500 ? '...' : '') :
                      'No preview available'
                    }
                  </pre>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-3 pt-4">
                <button
                  onClick={() => handleDownload(selectedDataset)}
                  className="btn-primary flex-1"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </button>
                <button
                  onClick={() => handleDelete(selectedDataset.id)}
                  className="btn-secondary flex-1 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                >
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetManager;
