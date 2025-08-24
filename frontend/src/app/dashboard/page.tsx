"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { 
  Brain, 
  Plus, 
  Upload, 
  MessageSquare, 
  Search,
  Bell,
  Settings,
  LogOut,
  Play,
  Clock,
  Database,
  Code,
  BarChart3,
  TrendingUp,
  Users,
  FileText,
  GitBranch,
  Zap
} from "lucide-react";
import Link from "next/link";

// Dummy data
const dummyProjects = [
  {
    id: "1",
    name: "Customer Analytics",
    description: "Customer behavior analysis and segmentation",
    type: "ML Model",
    status: "active",
    lastModified: "2 hours ago",
    blocks: 15,
    datasets: 3,
    executions: 24
  },
  {
    id: "2",
    name: "Data Pipeline",
    description: "ETL pipeline for sales data processing",
    type: "Data Pipeline",
    status: "stale",
    lastModified: "1 day ago",
    blocks: 8,
    datasets: 5,
    executions: 12
  },
  {
    id: "3",
    name: "EDA Analysis",
    description: "Exploratory data analysis for product data",
    type: "EDA Analysis",
    status: "active",
    lastModified: "3 hours ago",
    blocks: 12,
    datasets: 2,
    executions: 18
  },
  {
    id: "4",
    name: "BI Dashboard",
    description: "Business intelligence dashboard for KPIs",
    type: "BI Dashboard",
    status: "running",
    lastModified: "Running",
    blocks: 20,
    datasets: 8,
    executions: 45
  }
];

const recentActivity = [
  {
    id: "1",
    type: "execution",
    message: "Executed 'Data Cleaning' block in ML Model",
    time: "2 hours ago",
    icon: Play,
    color: "text-green-500"
  },
  {
    id: "2",
    type: "ai",
    message: "AI generated 'Feature Engineering' code",
    time: "4 hours ago",
    icon: Brain,
    color: "text-blue-500"
  },
  {
    id: "3",
    type: "import",
    message: "Imported 'customer_data.csv' dataset",
    time: "1 day ago",
    icon: Upload,
    color: "text-purple-500"
  },
  {
    id: "4",
    type: "project",
    message: "Created new project 'Customer Analytics'",
    time: "2 days ago",
    icon: FileText,
    color: "text-orange-500"
  }
];

const stats = [
  { label: "Projects", value: "12", icon: FileText, color: "text-blue-500" },
  { label: "Datasets", value: "8", icon: Database, color: "text-green-500" },
  { label: "Blocks", value: "156", icon: Code, color: "text-purple-500" },
  { label: "Success Rate", value: "89%", icon: TrendingUp, color: "text-orange-500" }
];

export default function DashboardPage() {
  const [searchQuery, setSearchQuery] = useState("");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "bg-green-500/10 text-green-500 border-green-500/20";
      case "stale": return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
      case "running": return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "error": return "bg-red-500/10 text-red-500 border-red-500/20";
      default: return "bg-muted text-muted-foreground border-border";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return "Active";
      case "stale": return "Stale";
      case "running": return "Running";
      case "error": return "Error";
      default: return "Unknown";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Top Navigation */}
      <nav className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-semibold">AI Notebook</span>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Search projects, datasets..."
                  className="pl-10 pr-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-ring focus:border-transparent w-64 bg-background text-foreground placeholder:text-muted-foreground"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              
              {/* Notifications */}
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center">
                  3
                </span>
              </Button>
              
              {/* User Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src="/avatars/01.png" alt="@user" />
                      <AvatarFallback>JD</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">John Doe</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        john.doe@example.com
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Users className="mr-2 h-4 w-4" />
                    <span>Team</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, John
          </h1>
          <p className="text-muted-foreground">
            Last active: 2 hours ago • Here's what's happening with your projects
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center">
                  <Plus className="w-6 h-6 text-blue-500" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">New Project</h3>
                  <p className="text-sm text-muted-foreground">Start a new data science project</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center">
                  <Upload className="w-6 h-6 text-green-500" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">Import Data</h3>
                  <p className="text-sm text-muted-foreground">Upload datasets for analysis</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/50 hover:border-border transition-colors cursor-pointer">
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-purple-500" />
                </div>
                <div>
                  <h3 className="font-semibold mb-1">AI Chat</h3>
                  <p className="text-sm text-muted-foreground">Get AI assistance for your work</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="border-border/50">
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Projects and Activity Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Projects Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">Your Projects (12)</h2>
              <Button variant="outline" size="sm">
                <Plus className="w-4 h-4 mr-2" />
                New Project
              </Button>
            </div>

            <div className="space-y-4">
              {dummyProjects.map((project) => (
                <Card key={project.id} className="border-border/50 hover:border-border transition-colors cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="font-semibold">{project.name}</h3>
                          <Badge className={getStatusColor(project.status)} variant="outline">
                            {getStatusIcon(project.status)} • {project.type}
                          </Badge>
                        </div>
                        <p className="text-muted-foreground mb-4">{project.description}</p>
                        
                        <div className="flex items-center space-x-6 text-sm text-muted-foreground">
                          <div className="flex items-center space-x-1">
                            <Code className="w-4 h-4" />
                            <span>{project.blocks} blocks</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Database className="w-4 h-4" />
                            <span>{project.datasets} datasets</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <Play className="w-4 h-4" />
                            <span>{project.executions} executions</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right">
                        <p className="text-sm text-muted-foreground mb-1">Last modified</p>
                        <p className="text-sm font-medium">{project.lastModified}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div>
            <h2 className="text-2xl font-bold mb-6">Recent Activity</h2>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <Card key={activity.id} className="border-border/50">
                  <CardContent className="p-4">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-muted rounded-lg flex items-center justify-center">
                        <activity.icon className={`w-4 h-4 ${activity.color}`} />
                      </div>
                      <div className="flex-1">
                        <p className="text-sm mb-1">{activity.message}</p>
                        <p className="text-xs text-muted-foreground flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {activity.time}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* AI Status */}
            <Card className="border-border/50 mt-6">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center space-x-2">
                  <Brain className="w-5 h-5 text-blue-500" />
                  <span>AI Status</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Ollama (Local)</span>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                    Online
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">OpenAI</span>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                    Available
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Gemini</span>
                  <Badge variant="secondary" className="bg-green-500/10 text-green-500">
                    Available
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
