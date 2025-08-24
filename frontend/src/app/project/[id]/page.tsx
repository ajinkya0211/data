"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { 
  Brain, 
  GitBranch, 
  Play, 
  Square, 
  Save, 
  Share2, 
  Download, 
  Settings,
  Plus,
  Search,
  Database,
  Code,
  BarChart3,
  MessageSquare,
  Upload,
  Eye,
  FileText,
  ChevronDown,
  ChevronRight,
  ChevronLeft,
  Clock,
  CheckCircle,
  AlertCircle,
  Loader2
} from "lucide-react";
import Link from "next/link";

// Dummy data
const dummyProject = {
  id: "1",
  name: "Customer Analytics",
  description: "Customer behavior analysis and segmentation using machine learning",
  lastModified: "2 hours ago",
  blocks: [
    {
      id: "1",
      title: "Data Loading",
      type: "code",
      content: `import pandas as pd
import numpy as np

# Load customer data
df = pd.read_csv('customer_data.csv')
print(f"Loaded {len(df)} rows")
print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB")`,
      status: "completed",
      output: "Loaded 10,000 rows\nMemory usage: 2.3 MB",
      executionTime: "15s"
    },
    {
      id: "2",
      title: "Data Exploration",
      type: "code",
      content: `# Display basic information
print("Dataset shape:", df.shape)
print("\\nColumn types:")
print(df.dtypes)
print("\\nFirst 5 rows:")
print(df.head())`,
      status: "completed",
      output: "Dataset shape: (10000, 15)\nColumn types:\nCustomerID int64\nAge int64\nIncome float64\n...\nFirst 5 rows:\n[Data table preview]",
      executionTime: "45s"
    },
    {
      id: "3",
      title: "Data Cleaning",
      type: "code",
      content: `# Handle missing values
print("Missing values per column:")
print(df.isnull().sum())

# Fill missing values
df['Age'].fillna(df['Age'].median(), inplace=True)
df['Income'].fillna(df['Income'].mean(), inplace=True)

print("\\nMissing values after cleaning:")
print(df.isnull().sum())`,
      status: "completed",
      output: "Missing values per column:\nAge: 150\nIncome: 75\n...\nMissing values after cleaning:\nAge: 0\nIncome: 0",
      executionTime: "1m 12s"
    },
    {
      id: "4",
      title: "Feature Engineering",
      type: "code",
      content: `# Create new features
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 25, 35, 50, 100], labels=['Young', 'Adult', 'Middle', 'Senior'])
df['IncomeCategory'] = pd.cut(df['Income'], bins=[0, 30000, 60000, 100000, float('inf')], labels=['Low', 'Medium', 'High', 'Very High'])

print("New features created:")
print(df[['AgeGroup', 'IncomeCategory']].value_counts())`,
      status: "stale",
      output: "New features created:\nAgeGroup: Young (2500), Adult (3000), Middle (3000), Senior (1500)\nIncomeCategory: Low (2000), Medium (3000), High (3000), Very High (2000)",
      executionTime: "38s"
    },
    {
      id: "5",
      title: "Model Training",
      type: "code",
      content: `from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Prepare features and target
X = df[['Age', 'Income', 'PurchaseFrequency']]
y = df['Churn']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.3f}")`,
      status: "running",
      output: "Training model with 8,000 samples...\nEpoch 1/10: Loss = 0.234\nEpoch 2/10: Loss = 0.198\nEpoch 3/10: Loss = 0.167",
      executionTime: "Running..."
    }
  ],
  datasets: [
    {
      id: "1",
      name: "customer_data.csv",
      size: "2.3 MB",
      rows: 10000,
      columns: 15,
      lastModified: "2 hours ago"
    },
    {
      id: "2",
      name: "product_catalog.json",
      size: "1.1 MB",
      rows: 5000,
      columns: 8,
      lastModified: "1 day ago"
    },
    {
      id: "3",
      name: "sales_transactions.parquet",
      size: "8.7 MB",
      rows: 25000,
      columns: 12,
      lastModified: "3 days ago"
    }
  ]
};

const aiSuggestions = [
  "Clean missing values in the dataset",
  "Create visualizations for age distribution",
  "Train a machine learning model for churn prediction",
  "Optimize pandas operations for better performance",
  "Add data validation and quality checks"
];

export default function ProjectWorkspacePage({ params }: { params: { id: string } }) {
  const [activeView, setActiveView] = useState("notebook");
  const [aiQuery, setAiQuery] = useState("");
  const [isExecuting, setIsExecuting] = useState(false);
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(true);

  const handleExecuteBlock = (blockId: string) => {
    setIsExecuting(true);
    // Simulate execution
    setTimeout(() => {
      setIsExecuting(false);
    }, 2000);
  };

  const handleExecuteAll = () => {
    setIsExecuting(true);
    // Simulate execution
    setTimeout(() => {
      setIsExecuting(false);
    }, 5000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="w-4 h-4 text-green-600" />;
      case "running": return <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />;
      case "stale": return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      case "error": return <AlertCircle className="w-4 h-4 text-red-600" />;
      default: return <Clock className="w-4 h-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-800";
      case "running": return "bg-blue-100 text-blue-800";
      case "stale": return "bg-yellow-100 text-yellow-800";
      case "error": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Project Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="text-gray-600 hover:text-gray-900">
                <Brain className="w-6 h-6" />
              </Link>
              <Separator orientation="vertical" className="h-6" />
              <div>
                <h1 className="text-xl font-semibold text-gray-900">{dummyProject.name}</h1>
                <p className="text-sm text-gray-500">Last modified: {dummyProject.lastModified}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button variant="outline" size="sm">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export
              </Button>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Settings
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* View Toggle and Controls */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <Tabs value={activeView} onValueChange={setActiveView} className="w-full">
              <TabsList className="grid w-full grid-cols-2 max-w-xs">
                <TabsTrigger value="notebook" className="flex items-center space-x-2">
                  <Code className="w-4 h-4" />
                  <span>Notebook</span>
                </TabsTrigger>
                <TabsTrigger value="dag" className="flex items-center space-x-2">
                  <GitBranch className="w-4 h-4" />
                  <span>DAG Workflow</span>
                </TabsTrigger>
              </TabsList>
            </Tabs>
            
            <div className="flex items-center space-x-3">
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                🟢 Kernel: Python 3.11
              </Badge>
              <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                ⚠️ 2 blocks stale
              </Badge>
              <Badge variant="secondary" className="bg-red-100 text-red-800">
                ❌ 1 error
              </Badge>
              
              <Button 
                onClick={handleExecuteAll}
                disabled={isExecuting}
                className="bg-green-600 hover:bg-green-700"
              >
                {isExecuting ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                {isExecuting ? "Running..." : "Run All"}
              </Button>
              
              <Button variant="outline">
                <Save className="w-4 h-4 mr-2" />
                Save
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex h-[calc(100vh-8rem)]">
        {/* Left Sidebar - Data Explorer */}
        {leftSidebarOpen && (
          <div className="w-80 bg-white border-r shadow-sm overflow-y-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900">Data Explorer</h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setLeftSidebarOpen(false)}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search datasets..."
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="p-4">
              <h4 className="font-medium text-gray-900 mb-3">Available Datasets ({dummyProject.datasets.length})</h4>
              <div className="space-y-3">
                {dummyProject.datasets.map((dataset) => (
                  <Card key={dataset.id} className="border-0 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900 text-sm mb-1">{dataset.name}</h5>
                          <div className="text-xs text-gray-500 space-y-1">
                            <div className="flex items-center space-x-1">
                              <Database className="w-3 h-3" />
                              <span>{dataset.rows.toLocaleString()} rows • {dataset.columns} columns</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <FileText className="w-3 h-3" />
                              <span>{dataset.size} • {dataset.lastModified}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-1">
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <Eye className="w-3 h-3" />
                          </Button>
                          <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                            <Plus className="w-3 h-3" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
              
              <Button variant="outline" className="w-full mt-4">
                <Upload className="w-4 h-4 mr-2" />
                Upload New Dataset
              </Button>
            </div>
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          <TabsContent value="notebook" className="flex-1 p-6 overflow-y-auto">
            <div className="space-y-6">
              {dummyProject.blocks.map((block) => (
                <Card key={block.id} className="border-0 shadow-lg">
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <h3 className="font-semibold text-gray-900">{block.title}</h3>
                        <Badge className={getStatusColor(block.status)}>
                          {getStatusIcon(block.status)} {block.status}
                        </Badge>
                        {block.executionTime !== "Running..." && (
                          <span className="text-sm text-gray-500">⏱️ {block.executionTime}</span>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleExecuteBlock(block.id)}
                          disabled={block.status === "running"}
                        >
                          {block.status === "running" ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Settings className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {/* Code Block */}
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-gray-100 text-sm overflow-x-auto">
                        <code>{block.content}</code>
                      </pre>
                    </div>
                    
                    {/* Output */}
                    {block.output && (
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-2">Output:</h4>
                        <pre className="text-gray-700 text-sm whitespace-pre-wrap">{block.output}</pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
              
              {/* Add New Block */}
              <Card className="border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors cursor-pointer">
                <CardContent className="p-6 text-center">
                  <Plus className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">Add new code block</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="dag" className="flex-1 p-6">
            <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 h-full flex items-center justify-center">
              <div className="text-center">
                <GitBranch className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">DAG Workflow View</h3>
                <p className="text-gray-600 mb-4">
                  Visual workflow editor with drag-and-drop interface
                </p>
                <Button variant="outline">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Workflow
                </Button>
              </div>
            </div>
          </TabsContent>
        </div>

        {/* Right Sidebar - AI Assistant */}
        {rightSidebarOpen && (
          <div className="w-80 bg-white border-l shadow-sm overflow-y-auto">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-semibold text-gray-900 flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-blue-600" />
                  <span>AI Assistant</span>
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setRightSidebarOpen(false)}
                >
                  <ChevronDown className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="relative">
                <MessageSquare className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Ask AI for help..."
                  value={aiQuery}
                  onChange={(e) => setAiQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="p-4">
              <h4 className="font-medium text-gray-900 mb-3">Quick Actions</h4>
              <div className="space-y-2">
                {aiSuggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    className="w-full justify-start text-left h-auto p-3"
                  >
                    <span className="text-sm">{suggestion}</span>
                  </Button>
                ))}
              </div>
              
              <Separator className="my-4" />
              
              <h4 className="font-medium text-gray-900 mb-3">Context</h4>
              <div className="space-y-3 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Database className="w-4 h-4" />
                  <span>3 datasets loaded</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Code className="w-4 h-4" />
                  <span>5 code blocks</span>
                </div>
                <div className="flex items-center space-x-2">
                  <BarChart3 className="w-4 h-4" />
                  <span>Python 3.11 kernel</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Clock className="w-4 h-4" />
                  <span>Last execution: 5 min ago</span>
                </div>
              </div>
              
              <Separator className="my-4" />
              
              <h4 className="font-medium text-gray-900 mb-3">Recent AI Interactions</h4>
              <div className="space-y-2 text-sm">
                <div className="p-2 bg-blue-50 rounded">
                  <p className="text-blue-900">"Added data validation" (2 min ago)</p>
                </div>
                <div className="p-2 bg-green-50 rounded">
                  <p className="text-green-900">"Created correlation plot" (15 min ago)</p>
                </div>
                <div className="p-2 bg-purple-50 rounded">
                  <p className="text-purple-900">"Optimized pandas operations" (1 hour ago)</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Sidebar Toggle Buttons */}
      {!leftSidebarOpen && (
        <button
          onClick={() => setLeftSidebarOpen(true)}
          className="fixed left-4 top-1/2 transform -translate-y-1/2 bg-white border rounded-lg p-2 shadow-lg hover:shadow-xl transition-shadow"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      )}
      
      {!rightSidebarOpen && (
        <button
          onClick={() => setRightSidebarOpen(true)}
          className="fixed right-4 top-1/2 transform -translate-y-1/2 bg-white border rounded-lg p-2 shadow-lg hover:shadow-xl transition-shadow"
        >
          <ChevronLeft className="w-4 h-4" />
        </button>
      )}
    </div>
  );
}
