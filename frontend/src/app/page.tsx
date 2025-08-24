"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Brain, 
  GitBranch, 
  Zap, 
  Database, 
  Code, 
  BarChart3, 
  Users, 
  ArrowRight,
  Play,
  Sparkles,
  Shield,
  Globe,
  Search,
  Github
} from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
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
              <div className="hidden md:flex items-center space-x-6 text-sm">
                <Link href="/demo" className="text-muted-foreground hover:text-foreground transition-colors">
                  Examples
                </Link>
                <Link href="/dashboard" className="text-muted-foreground hover:text-foreground transition-colors">
                  Dashboard
                </Link>
                <Link href="/minimal" className="text-muted-foreground hover:text-foreground transition-colors">
                  Minimal AI
                </Link>
                <Link href="/auth" className="text-muted-foreground hover:text-foreground transition-colors">
                  Sign In
                </Link>
              </div>
              <Link href="/auth">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <Badge variant="secondary" className="mb-8 px-3 py-1 text-xs">
            Multi-AI Provider Support
          </Badge>
          
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
            Transform Data Science with
            <span className="bg-gradient-to-r from-blue-500 to-indigo-500 bg-clip-text text-transparent">
              {" "}AI-Powered Notebooks
            </span>
          </h1>
          
          <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto leading-relaxed">
            Enterprise-grade AI notebook system with visual workflows, real-time collaboration, 
            and multi-provider AI support for modern data science teams.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth">
              <Button size="lg" className="text-lg px-8 py-6">
                <Play className="w-5 h-5 mr-2" />
                Get Started
              </Button>
            </Link>
            <Link href="/demo">
              <Button variant="outline" size="lg" className="text-lg px-8 py-6">
                <Sparkles className="w-5 h-5 mr-2" />
                View Demo
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">
              Enterprise Features
            </h2>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Built for professional data science teams with enterprise-grade capabilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Brain className="w-6 h-6 text-blue-500" />
                </div>
                <CardTitle>Multi-AI Providers</CardTitle>
                <CardDescription>
                  Ollama, OpenAI, and Gemini integration with automatic fallback and provider switching.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-green-500/10 rounded-lg flex items-center justify-center mb-4">
                  <GitBranch className="w-6 h-6 text-green-500" />
                </div>
                <CardTitle>Visual DAG Editor</CardTitle>
                <CardDescription>
                  Build complex data pipelines with ReactFlow-based canvas and dependency management.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Database className="w-6 h-6 text-purple-500" />
                </div>
                <CardTitle>Data Profiling</CardTitle>
                <CardDescription>
                  Automatic dataset understanding, schema detection, and quality assessment.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-orange-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Code className="w-6 h-6 text-orange-500" />
                </div>
                <CardTitle>Jupyter Integration</CardTitle>
                <CardDescription>
                  Full Python kernel support with persistent state and output capture.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-red-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-red-500" />
                </div>
                <CardTitle>Real-time Collaboration</CardTitle>
                <CardDescription>
                  WebSocket-based live updates and team collaboration features.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <div className="w-12 h-12 bg-indigo-500/10 rounded-lg flex items-center justify-center mb-4">
                  <Shield className="w-6 h-6 text-indigo-500" />
                </div>
                <CardTitle>Enterprise Security</CardTitle>
                <CardDescription>
                  JWT authentication, role-based access control, and secure data handling.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-blue-500 mb-2">1000+</div>
              <div className="text-muted-foreground">Active Projects</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-green-500 mb-2">500+</div>
              <div className="text-muted-foreground">Datasets</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-500 mb-2">50+</div>
              <div className="text-muted-foreground">AI Models</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-500 mb-2">99.9%</div>
              <div className="text-muted-foreground">Uptime</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-muted/20">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to transform your workflow?
          </h2>
          <p className="text-xl text-muted-foreground mb-8">
            Join professional data science teams building the future with AI.
          </p>
          <Link href="/auth">
            <Button size="lg" className="text-lg px-8 py-6">
              Start Building
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <Brain className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-semibold">AI Notebook</span>
              </div>
              <p className="text-muted-foreground">
                Enterprise-grade AI notebook system for modern data science teams.
              </p>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>Features</li>
                <li>Documentation</li>
                <li>API</li>
                <li>Pricing</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>About</li>
                <li>Blog</li>
                <li>Careers</li>
                <li>Contact</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-4">Support</h3>
              <ul className="space-y-2 text-muted-foreground">
                <li>Help Center</li>
                <li>Community</li>
                <li>Status</li>
                <li>Security</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-border/40 mt-8 pt-8 text-center text-muted-foreground">
            <p>&copy; 2024 AI Notebook System. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
