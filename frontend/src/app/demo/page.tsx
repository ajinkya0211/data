"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Brain, 
  GitBranch, 
  Play, 
  Code, 
  Database, 
  BarChart3, 
  ArrowLeft,
  CheckCircle,
  Loader2,
  Sparkles,
  Zap,
  Users,
  Shield,
  Globe
} from "lucide-react";
import Link from "next/link";

export default function DemoPage() {
  const [activeDemo, setActiveDemo] = useState("overview");
  const [isExecuting, setIsExecuting] = useState(false);

  const handleExecuteDemo = () => {
    setIsExecuting(true);
    setTimeout(() => {
      setIsExecuting(false);
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">AI Notebook Demo</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth">
                <Button>Try It Live</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-16 pb-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="secondary" className="mb-6">
            🚀 Interactive Demo
          </Badge>
          
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            See AI Notebook System in Action
          </h1>
          
          <p className="text-xl text-gray-600 mb-8">
            Experience the power of AI-assisted data science with interactive demonstrations 
            of our key features. See how natural language becomes code, workflows become 
            visual, and collaboration becomes seamless.
          </p>
        </div>
      </section>

      {/* Demo Tabs */}
      <section className="px-4 sm:px-6 lg:px-8 pb-16">
        <div className="max-w-6xl mx-auto">
          <Tabs value={activeDemo} onValueChange={setActiveDemo} className="w-full">
            <TabsList className="grid w-full grid-cols-4 mb-8">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="ai-assistant">AI Assistant</TabsTrigger>
              <TabsTrigger value="dag-workflow">DAG Workflow</TabsTrigger>
              <TabsTrigger value="execution">Live Execution</TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <Card className="border-0 shadow-xl">
                  <CardHeader>
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                      <Brain className="w-6 h-6 text-blue-600" />
                    </div>
                    <CardTitle>Multi-AI Provider Support</CardTitle>
                    <CardDescription>
                      Choose from Ollama (local), OpenAI, or Gemini with automatic fallback
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                        <span className="text-sm font-medium">Ollama (Local)</span>
                        <Badge className="bg-green-100 text-green-800">✅ Online</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                        <span className="text-sm font-medium">OpenAI GPT-4</span>
                        <Badge className="bg-blue-100 text-blue-800">✅ Available</Badge>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                        <span className="text-sm font-medium">Google Gemini</span>
                        <Badge className="bg-purple-100 text-purple-800">✅ Available</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-xl">
                  <CardHeader>
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                      <GitBranch className="w-6 h-6 text-green-600" />
                    </div>
                    <CardTitle>Visual DAG Workflows</CardTitle>
                    <CardDescription>
                      Build complex data pipelines with drag-and-drop interface
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <GitBranch className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                      <p className="text-gray-600 text-sm">
                        Interactive workflow canvas with ReactFlow integration
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-xl">
                  <CardHeader>
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                      <Zap className="w-6 h-6 text-purple-600" />
                    </div>
                    <CardTitle>Real-time Execution</CardTitle>
                    <CardDescription>
                      Live monitoring and WebSocket-based collaboration
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Execution Status</span>
                        <Badge className="bg-green-100 text-green-800">🟢 Active</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">WebSocket</span>
                        <Badge className="bg-green-100 text-green-800">✅ Connected</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Collaboration</span>
                        <Badge className="bg-blue-100 text-blue-800">🔄 Live</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="border-0 shadow-xl">
                  <CardHeader>
                    <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
                      <Database className="w-6 h-6 text-orange-600" />
                    </div>
                    <CardTitle>Smart Data Profiling</CardTitle>
                    <CardDescription>
                      Automatic dataset understanding and quality scoring
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Data Quality Score</span>
                        <Badge className="bg-green-100 text-green-800">87%</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Schema Detection</span>
                        <Badge className="bg-green-100 text-green-800">✅ Auto</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Missing Values</span>
                        <Badge className="bg-yellow-100 text-yellow-800">⚠️ 3 datasets</Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* AI Assistant Tab */}
            <TabsContent value="ai-assistant" className="space-y-8">
              <Card className="border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Brain className="w-6 h-6 text-blue-600" />
                    <span>AI-Powered Code Generation</span>
                  </CardTitle>
                  <CardDescription>
                    See how natural language becomes executable Python code
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Example 1 */}
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Users className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700">User Request:</span>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-blue-900 font-medium">
                        "Load the customer dataset and show me the first 5 rows with basic statistics"
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Brain className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="h-px bg-blue-200 flex-1 mx-4"></div>
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Code className="w-4 h-4 text-green-600" />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Code className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700">AI Generated Code:</span>
                    </div>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-gray-100 text-sm">
                        <code>{`import pandas as pd

# Load customer dataset
df = pd.read_csv('customer_data.csv')

# Display first 5 rows
print("First 5 rows:")
print(df.head())

# Show basic statistics
print("\\nBasic statistics:")
print(df.describe())`}</code>
                      </pre>
                    </div>
                  </div>

                  {/* Example 2 */}
                  <div className="space-y-3 mt-8">
                    <div className="flex items-center space-x-2">
                      <Users className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700">User Request:</span>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4">
                      <p className="text-blue-900 font-medium">
                        "Create a visualization showing customer age distribution by income category"
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <Brain className="w-4 h-4 text-blue-600" />
                    </div>
                    <div className="h-px bg-blue-200 flex-1 mx-4"></div>
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Code className="w-4 h-4 text-green-600" />
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Code className="w-5 h-5 text-gray-400" />
                      <span className="text-sm font-medium text-gray-700">AI Generated Code:</span>
                    </div>
                    <div className="bg-gray-900 rounded-lg p-4">
                      <pre className="text-gray-100 text-sm">
                        <code>{`import matplotlib.pyplot as plt
import seaborn as sns

# Create age groups
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 25, 35, 50, 100], 
                        labels=['Young', 'Adult', 'Middle', 'Senior'])

# Create income categories
df['IncomeCategory'] = pd.cut(df['Income'], bins=[0, 30000, 60000, 100000, float('inf')], 
                              labels=['Low', 'Medium', 'High', 'Very High'])

# Create visualization
plt.figure(figsize=(12, 6))
sns.countplot(data=df, x='AgeGroup', hue='IncomeCategory')
plt.title('Customer Age Distribution by Income Category')
plt.xlabel('Age Group')
plt.ylabel('Count')
plt.legend(title='Income Category')
plt.show()`}</code>
                      </pre>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* DAG Workflow Tab */}
            <TabsContent value="dag-workflow" className="space-y-8">
              <Card className="border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <GitBranch className="w-6 h-6 text-green-600" />
                    <span>Visual Workflow Construction</span>
                  </CardTitle>
                  <CardDescription>
                    Build complex data pipelines with visual DAG editor
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-gray-50 rounded-lg p-8">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                      {/* Data Loading Node */}
                      <div className="bg-white rounded-lg p-4 border-2 border-blue-200 shadow-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Database className="w-5 h-5 text-blue-600" />
                          <span className="font-medium text-gray-900">Data Loading</span>
                        </div>
                        <p className="text-sm text-gray-600">Load customer dataset</p>
                        <Badge className="mt-2 bg-green-100 text-green-800">✅ Completed</Badge>
                      </div>

                      {/* Data Cleaning Node */}
                      <div className="bg-white rounded-lg p-4 border-2 border-green-200 shadow-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Code className="w-5 h-5 text-green-600" />
                          <span className="font-medium text-gray-900">Data Cleaning</span>
                        </div>
                        <p className="text-sm text-gray-600">Handle missing values</p>
                        <Badge className="mt-2 bg-green-100 text-green-800">✅ Completed</Badge>
                      </div>

                      {/* Feature Engineering Node */}
                      <div className="bg-white rounded-lg p-4 border-2 border-yellow-200 shadow-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <BarChart3 className="w-5 h-5 text-yellow-600" />
                          <span className="font-medium text-gray-900">Feature Engineering</span>
                        </div>
                        <p className="text-sm text-gray-600">Create new features</p>
                        <Badge className="mt-2 bg-yellow-100 text-yellow-800">⚠️ Stale</Badge>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Model Training Node */}
                      <div className="bg-white rounded-lg p-4 border-2 border-purple-200 shadow-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <Brain className="w-5 h-5 text-purple-600" />
                          <span className="font-medium text-gray-900">Model Training</span>
                        </div>
                        <p className="text-sm text-gray-600">Train ML model</p>
                        <Badge className="mt-2 bg-blue-100 text-blue-800">🔄 Running</Badge>
                      </div>

                      {/* Results Analysis Node */}
                      <div className="bg-white rounded-lg p-4 border-2 border-gray-200 shadow-lg opacity-50">
                        <div className="flex items-center space-x-2 mb-2">
                          <BarChart3 className="w-5 h-5 text-gray-600" />
                          <span className="font-medium text-gray-900">Results Analysis</span>
                        </div>
                        <p className="text-sm text-gray-600">Analyze model results</p>
                        <Badge className="mt-2 bg-gray-100 text-gray-800">⏳ Waiting</Badge>
                      </div>
                    </div>

                    {/* Connection Lines */}
                    <div className="relative mt-8">
                      <div className="absolute top-0 left-1/4 w-px h-8 bg-blue-300"></div>
                      <div className="absolute top-0 left-1/2 w-px h-8 bg-green-300"></div>
                      <div className="absolute top-0 left-3/4 w-px h-8 bg-yellow-300"></div>
                      <div className="absolute top-0 left-1/3 w-px h-8 bg-purple-300"></div>
                      <div className="absolute top-0 left-2/3 w-px h-8 bg-gray-300"></div>
                    </div>

                    <div className="text-center mt-6">
                      <p className="text-sm text-gray-600">
                        Drag and drop to rearrange • Click to edit • Visualize dependencies
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Live Execution Tab */}
            <TabsContent value="execution" className="space-y-8">
              <Card className="border-0 shadow-xl">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Play className="w-6 h-6 text-green-600" />
                    <span>Live Code Execution</span>
                  </CardTitle>
                  <CardDescription>
                    Experience real-time code execution with Jupyter kernel integration
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Execution Status */}
                  <div className="bg-gray-50 rounded-lg p-6">
                    <h3 className="font-semibold text-gray-900 mb-4">Execution Status</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Kernel Status</span>
                        <Badge className="bg-green-100 text-green-800">🟢 Python 3.11 Active</Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Memory Usage</span>
                        <span className="text-sm font-medium">2.3 GB / 8.0 GB</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Active Sessions</span>
                        <span className="text-sm font-medium">1</span>
                      </div>
                    </div>
                  </div>

                  {/* Demo Execution */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">Demo Execution</h3>
                      <Button 
                        onClick={handleExecuteDemo}
                        disabled={isExecuting}
                        className="bg-green-600 hover:bg-green-700"
                      >
                        {isExecuting ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            Executing...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4 mr-2" />
                            Run Demo
                          </>
                        )}
                      </Button>
                    </div>

                    {isExecuting && (
                      <div className="bg-gray-900 rounded-lg p-4">
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 text-green-400 animate-spin" />
                            <span className="text-green-400 text-sm">Executing: Data Loading</span>
                          </div>
                          <div className="text-gray-300 text-sm">
                            <p>Loading customer_data.csv...</p>
                            <p>Dataset loaded successfully: 10,000 rows, 15 columns</p>
                            <p>Memory usage: 2.3 MB</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Sample Output */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-medium text-gray-900 mb-2">Sample Output</h4>
                      <div className="bg-white rounded border p-3">
                        <pre className="text-sm text-gray-700">
{`Dataset loaded successfully!
Shape: (10000, 15)
Columns: ['CustomerID', 'Age', 'Income', 'PurchaseFrequency', 'Churn', ...]
Memory usage: 2.3 MB
Execution time: 1.2s`}
                        </pre>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-indigo-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to experience the future of data science?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of data scientists who are already building with AI assistance.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth">
              <Button size="lg" variant="secondary" className="text-lg px-8 py-6">
                <Sparkles className="w-5 h-5 mr-2" />
                Start Building Now
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 border-white text-white hover:bg-white hover:text-blue-600">
                <Users className="w-5 h-5 mr-2" />
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
