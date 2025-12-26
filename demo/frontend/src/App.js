import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Sidebar from './components/Sidebar';
import Notebook from './components/Notebook';
import DAGView from './components/DAGView';
import AgentChat from './components/AgentChat';
import DatasetManager from './components/DatasetManager';
import { NotebookProvider } from './contexts/NotebookContext';

function App() {
  return (
    <NotebookProvider>
      <Router>
        <div className="flex h-screen bg-notebook-bg">
          {/* Left Sidebar - Navigation */}
          <Sidebar />
          
          {/* Main Content Area */}
          <main className="flex-1 flex flex-col overflow-hidden">
            <Routes>
              <Route path="/" element={<Notebook />} />
              <Route path="/dag" element={<DAGView />} />
              <Route path="/datasets" element={<DatasetManager />} />
            </Routes>
          </main>

          {/* Right Sidebar - AI Chat (Always Visible) */}
          <div className="w-80 bg-notebook-surface border-l border-notebook-border flex flex-col">
            <AgentChat />
          </div>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#161b22',
              color: '#c9d1d9',
              border: '1px solid #30363d',
            },
          }}
        />
      </Router>
    </NotebookProvider>
  );
}

export default App;
