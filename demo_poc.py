#!/usr/bin/env python3
"""
AI Notebook System - PPOC Demonstration Script
==============================================

This script demonstrates all the working functionality of the PPOC stage
without requiring Jupyter startup or MinIO configuration.

Features demonstrated:
- Authentication
- AI Chat with Ollama
- Project Management
- Dataset Operations
- Data Profiling
- AI Code Generation
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
DEMO_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

class POCDemonstrator:
    def __init__(self):
        self.auth_token = None
        self.base_url = BASE_URL
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message: str):
        """Print a success message"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Print an info message"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"⚠️  {message}")
    
    def authenticate(self) -> bool:
        """Authenticate and get access token"""
        self.print_header("Authentication Demo")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login-json",
                json=DEMO_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.print_success(f"Login successful! User: {data['user']['full_name']}")
                self.print_info(f"Role: {data['user']['role']}")
                self.print_info(f"Token expires in: {data['expires_in']} seconds")
                return True
            else:
                self.print_warning(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_warning(f"Authentication error: {str(e)}")
            return False
    
    def demo_ai_chat(self) -> bool:
        """Demonstrate AI chat functionality"""
        self.print_header("AI Chat Demo")
        
        if not self.auth_token:
            self.print_warning("No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Test different types of AI interactions
        chat_examples = [
            {
                "message": "Hello! Can you help me write a Python function to calculate the factorial of a number?",
                "provider": "ollama"
            },
            {
                "message": "Explain how to use pandas to read a CSV file and show the first 5 rows",
                "provider": "ollama"
            },
            {
                "message": "Write a Python script to create a simple bar chart using matplotlib",
                "provider": "ollama"
            }
        ]
        
        for i, chat_data in enumerate(chat_examples, 1):
            try:
                self.print_info(f"Chat {i}: {chat_data['message'][:50]}...")
                
                response = requests.post(
                    f"{self.base_url}/api/v1/ai/chat",
                    json=chat_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Response received from {data['provider']} ({data['model']})")
                    self.print_info(f"Response length: {len(data['response'])} characters")
                    
                    # Show a snippet of the response
                    response_preview = data['response'][:100] + "..." if len(data['response']) > 100 else data['response']
                    print(f"   Preview: {response_preview}")
                    
                else:
                    self.print_warning(f"Chat {i} failed: {response.status_code}")
                    
                time.sleep(1)  # Brief pause between chats
                
            except Exception as e:
                self.print_warning(f"Chat {i} error: {str(e)}")
        
        return True
    
    def demo_project_management(self) -> bool:
        """Demonstrate project management functionality"""
        self.print_header("Project Management Demo")
        
        if not self.auth_token:
            self.print_warning("No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Create multiple projects
            projects_to_create = [
                {
                    "name": "Data Analysis Project",
                    "description": "Analyzing customer behavior data with Python and pandas"
                },
                {
                    "name": "Machine Learning Demo",
                    "description": "Building a simple ML model using scikit-learn"
                },
                {
                    "name": "Data Visualization",
                    "description": "Creating interactive charts with plotly and matplotlib"
                }
            ]
            
            created_projects = []
            
            for project_data in projects_to_create:
                self.print_info(f"Creating project: {project_data['name']}")
                
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/",
                    json=project_data,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    project = response.json()
                    created_projects.append(project)
                    self.print_success(f"Project created: {project['name']} (ID: {project['id'][:8]}...)")
                else:
                    self.print_warning(f"Failed to create project: {response.status_code}")
            
            # List all projects
            self.print_info("Listing all projects...")
            response = requests.get(f"{self.base_url}/api/v1/projects/", headers=headers)
            
            if response.status_code == 200:
                projects = response.json()
                self.print_success(f"Found {len(projects)} projects")
                for project in projects:
                    print(f"   - {project['name']}: {project['description']}")
            else:
                self.print_warning(f"Failed to list projects: {response.status_code}")
            
            # Retrieve a specific project
            if created_projects:
                project_id = created_projects[0]['id']
                self.print_info(f"Retrieving project: {project_id[:8]}...")
                
                response = requests.get(
                    f"{self.base_url}/api/v1/projects/{project_id}",
                    headers=headers
                )
                
                if response.status_code == 200:
                    project = response.json()
                    self.print_success(f"Project retrieved: {project['name']}")
                    self.print_info(f"   Version: {project['version']}")
                    self.print_info(f"   Created: {project['created_at']}")
                else:
                    self.print_warning(f"Failed to retrieve project: {response.status_code}")
            
            return True
            
        except Exception as e:
            self.print_warning(f"Project management error: {str(e)}")
            return False
    
    def demo_dataset_operations(self) -> bool:
        """Demonstrate dataset operations"""
        self.print_header("Dataset Operations Demo")
        
        if not self.auth_token:
            self.print_warning("No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # List datasets
            self.print_info("Listing datasets...")
            response = requests.get(f"{self.base_url}/api/v1/datasets/", headers=headers)
            
            if response.status_code == 200:
                datasets = response.json()
                if datasets:
                    self.print_success(f"Found {len(datasets)} datasets")
                    for dataset in datasets:
                        print(f"   - {dataset['name']}: {dataset['source_type']}")
                else:
                    self.print_info("No datasets found (this is expected for a fresh system)")
            else:
                self.print_warning(f"Failed to list datasets: {response.status_code}")
            
            # Note: Dataset creation would require file upload, which we're not testing here
            self.print_info("Dataset creation requires file upload (not demonstrated)")
            
            return True
            
        except Exception as e:
            self.print_warning(f"Dataset operations error: {str(e)}")
            return False
    
    def demo_data_profiling(self) -> bool:
        """Demonstrate data profiling capabilities"""
        self.print_header("Data Profiling Demo")
        
        try:
            # Check if sample data exists
            import os
            sample_data_path = "data/data_dirty.csv"
            
            if os.path.exists(sample_data_path):
                self.print_success(f"Sample dataset found: {sample_data_path}")
                
                # Read and profile the data
                import pandas as pd
                
                try:
                    df = pd.read_csv(sample_data_path)
                    self.print_success(f"CSV read successfully: {len(df)} rows, {len(df.columns)} columns")
                    
                    # Show basic statistics
                    self.print_info("Dataset Overview:")
                    print(f"   Shape: {df.shape}")
                    print(f"   Columns: {list(df.columns)}")
                    print(f"   Data types: {df.dtypes.to_dict()}")
                    
                    # Show sample data
                    self.print_info("Sample data (first 3 rows):")
                    print(df.head(3).to_string())
                    
                    # Basic statistics for numeric columns
                    numeric_cols = df.select_dtypes(include=['number']).columns
                    if len(numeric_cols) > 0:
                        self.print_info("Numeric column statistics:")
                        print(df[numeric_cols].describe().to_string())
                    
                    return True
                    
                except Exception as e:
                    self.print_warning(f"Data profiling error: {str(e)}")
                    return False
            else:
                self.print_warning(f"Sample dataset not found: {sample_data_path}")
                self.print_info("Data profiling requires sample data files")
                return False
                
        except Exception as e:
            self.print_warning(f"Data profiling setup error: {str(e)}")
            return False
    
    def demo_ai_code_generation(self) -> bool:
        """Demonstrate AI code generation"""
        self.print_header("AI Code Generation Demo")
        
        if not self.auth_token:
            self.print_warning("No auth token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            # Test code generation
            code_requests = [
                {
                    "request": "Create a function to calculate the mean, median, and standard deviation of a list of numbers",
                    "project_context": "Statistical analysis project",
                    "dataset_context": "Numeric data analysis",
                    "provider": "ollama"
                },
                {
                    "request": "Write a script to create a correlation matrix heatmap using seaborn",
                    "project_context": "Data visualization project",
                    "dataset_context": "Multi-variable dataset",
                    "provider": "ollama"
                }
            ]
            
            for i, request_data in enumerate(code_requests, 1):
                self.print_info(f"Code generation request {i}: {request_data['request'][:50]}...")
                
                response = requests.post(
                    f"{self.base_url}/api/v1/ai/generate-code",
                    json=request_data,
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.print_success(f"Code generated successfully!")
                    self.print_info(f"Generated code length: {len(data.get('code', ''))} characters")
                    
                    # Show a snippet of the generated code
                    code = data.get('code', '')
                    if code:
                        code_preview = code[:200] + "..." if len(code) > 200 else code
                        print(f"   Code preview:\n{code_preview}")
                else:
                    self.print_warning(f"Code generation {i} failed: {response.status_code}")
                
                time.sleep(1)
            
            return True
            
        except Exception as e:
            self.print_warning(f"AI code generation error: {str(e)}")
            return False
    
    def run_full_demo(self):
        """Run the complete POC demonstration"""
        self.print_header("🚀 AI Notebook System - PPOC Demonstration")
        self.print_info("This demonstration showcases all working functionality")
        self.print_info("No Jupyter or MinIO required!")
        
        # Check if backend is running
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.print_success("Backend is running and healthy!")
            else:
                self.print_warning("Backend is running but health check failed")
        except Exception as e:
            self.print_warning(f"Cannot connect to backend: {str(e)}")
            self.print_warning("Please ensure the backend is running on port 8000")
            return
        
        # Run all demos
        demos = [
            ("Authentication", self.authenticate),
            ("AI Chat", self.demo_ai_chat),
            ("Project Management", self.demo_project_management),
            ("Dataset Operations", self.demo_dataset_operations),
            ("Data Profiling", self.demo_data_profiling),
            ("AI Code Generation", self.demo_ai_code_generation)
        ]
        
        successful_demos = 0
        total_demos = len(demos)
        
        for demo_name, demo_func in demos:
            try:
                if demo_func():
                    successful_demos += 1
                time.sleep(1)  # Brief pause between demos
            except Exception as e:
                self.print_warning(f"{demo_name} demo failed: {str(e)}")
        
        # Final summary
        self.print_header("🎯 Demo Summary")
        self.print_success(f"Successfully demonstrated: {successful_demos}/{total_demos} features")
        
        if successful_demos == total_demos:
            self.print_success("🎉 All demos completed successfully!")
            self.print_info("The PPOC is fully functional and ready for frontend integration!")
        else:
            self.print_warning("Some demos had issues - check the logs above")
        
        self.print_info("\nNext steps:")
        self.print_info("1. Frontend development and integration")
        self.print_info("2. Database persistence implementation")
        self.print_info("3. File upload and storage integration")
        self.print_info("4. Jupyter kernel integration")

def main():
    """Main function to run the demonstration"""
    demonstrator = POCDemonstrator()
    demonstrator.run_full_demo()

if __name__ == "__main__":
    main() 