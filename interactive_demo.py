#!/usr/bin/env python3
"""
AI Notebook System - Interactive PPOC Demo
==========================================

An interactive demonstration that allows you to manually test
different features of the PPOC system.

Usage:
    python interactive_demo.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
DEMO_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

class InteractiveDemo:
    def __init__(self):
        self.auth_token = None
        self.base_url = BASE_URL
        
    def print_header(self, title: str):
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_menu(self):
        """Display the main menu"""
        self.print_header("Interactive PPOC Demo Menu")
        print("1. 🔐 Test Authentication")
        print("2. 🤖 Test AI Chat")
        print("3. 📁 Test Project Management")
        print("4. 📊 Test Dataset Operations")
        print("5. 📈 Test Data Profiling")
        print("6. 💻 Test AI Code Generation")
        print("7. 🔍 Check System Status")
        print("8. 🚀 Run Quick Demo")
        print("0. ❌ Exit")
        print(f"{'='*60}")
    
    def authenticate(self):
        """Test authentication"""
        self.print_header("Authentication Test")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login-json",
                json=DEMO_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                print(f"✅ Login successful!")
                print(f"   User: {data['user']['full_name']}")
                print(f"   Role: {data['user']['role']}")
                print(f"   Token expires in: {data['expires_in']} seconds")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def test_ai_chat(self):
        """Test AI chat functionality"""
        self.print_header("AI Chat Test")
        
        if not self.auth_token:
            print("❌ No auth token available. Please authenticate first.")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Get user input
        message = input("Enter your message for AI: ")
        if not message:
            message = "Hello! Can you help me with Python programming?"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/chat",
                json={"message": message, "provider": "ollama"},
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response from {data['provider']} ({data['model']}):")
                print(f"{'='*40}")
                print(data['response'])
                print(f"{'='*40}")
            else:
                print(f"❌ Chat failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Chat error: {str(e)}")
    
    def test_project_management(self):
        """Test project management"""
        self.print_header("Project Management Test")
        
        if not self.auth_token:
            print("❌ No auth token available. Please authenticate first.")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("Choose an action:")
        print("1. Create a new project")
        print("2. List all projects")
        print("3. Get a specific project")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        try:
            if choice == "1":
                name = input("Enter project name: ")
                description = input("Enter project description: ")
                
                if not name:
                    name = "Test Project"
                if not description:
                    description = "A test project for demonstration"
                
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/",
                    json={"name": name, "description": description},
                    headers=headers
                )
                
                if response.status_code in [200, 201]:
                    project = response.json()
                    print(f"✅ Project created successfully!")
                    print(f"   ID: {project['id']}")
                    print(f"   Name: {project['name']}")
                    print(f"   Description: {project['description']}")
                else:
                    print(f"❌ Failed to create project: {response.status_code}")
            
            elif choice == "2":
                response = requests.get(f"{self.base_url}/api/v1/projects/", headers=headers)
                
                if response.status_code == 200:
                    projects = response.json()
                    if projects:
                        print(f"✅ Found {len(projects)} projects:")
                        for i, project in enumerate(projects, 1):
                            print(f"   {i}. {project['name']} - {project['description']}")
                    else:
                        print("ℹ️  No projects found")
                else:
                    print(f"❌ Failed to list projects: {response.status_code}")
            
            elif choice == "3":
                project_id = input("Enter project ID: ")
                if project_id:
                    response = requests.get(
                        f"{self.base_url}/api/v1/projects/{project_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        project = response.json()
                        print(f"✅ Project retrieved:")
                        print(f"   Name: {project['name']}")
                        print(f"   Description: {project['description']}")
                        print(f"   Version: {project['version']}")
                        print(f"   Created: {project['created_at']}")
                    else:
                        print(f"❌ Failed to retrieve project: {response.status_code}")
                else:
                    print("❌ No project ID provided")
            
            else:
                print("❌ Invalid choice")
                
        except Exception as e:
            print(f"❌ Project management error: {str(e)}")
    
    def test_dataset_operations(self):
        """Test dataset operations"""
        self.print_header("Dataset Operations Test")
        
        if not self.auth_token:
            print("❌ No auth token available. Please authenticate first.")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/datasets/", headers=headers)
            
            if response.status_code == 200:
                datasets = response.json()
                if datasets:
                    print(f"✅ Found {len(datasets)} datasets:")
                    for dataset in datasets:
                        print(f"   - {dataset['name']}: {dataset['source_type']}")
                else:
                    print("ℹ️  No datasets found (this is expected for a fresh system)")
                    print("   Dataset creation requires file upload functionality")
            else:
                print(f"❌ Failed to list datasets: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Dataset operations error: {str(e)}")
    
    def test_data_profiling(self):
        """Test data profiling"""
        self.print_header("Data Profiling Test")
        
        try:
            import os
            import pandas as pd
            
            sample_data_path = "data/data_dirty.csv"
            
            if os.path.exists(sample_data_path):
                print(f"✅ Sample dataset found: {sample_data_path}")
                
                df = pd.read_csv(sample_data_path)
                print(f"✅ CSV read successfully: {len(df)} rows, {len(df.columns)} columns")
                
                print(f"\n📊 Dataset Overview:")
                print(f"   Shape: {df.shape}")
                print(f"   Columns: {list(df.columns)}")
                
                print(f"\n📋 Sample data (first 3 rows):")
                print(df.head(3).to_string())
                
                # Show statistics for numeric columns
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    print(f"\n📈 Numeric column statistics:")
                    print(df[numeric_cols].describe().to_string())
                
            else:
                print(f"❌ Sample dataset not found: {sample_data_path}")
                print("   Data profiling requires sample data files")
                
        except ImportError:
            print("❌ pandas not available. Install with: pip install pandas")
        except Exception as e:
            print(f"❌ Data profiling error: {str(e)}")
    
    def test_ai_code_generation(self):
        """Test AI code generation"""
        self.print_header("AI Code Generation Test")
        
        if not self.auth_token:
            print("❌ No auth token available. Please authenticate first.")
            return
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        request = input("Enter your code generation request: ")
        if not request:
            request = "Create a function to calculate the factorial of a number"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/ai/generate-code",
                json={
                    "request": request,
                    "project_context": "Demo project",
                    "dataset_context": "Sample data",
                    "provider": "ollama"
                },
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Code generated successfully!")
                print(f"{'='*40}")
                print(data.get('code', 'No code generated'))
                print(f"{'='*40}")
            else:
                print(f"❌ Code generation failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Code generation error: {str(e)}")
    
    def check_system_status(self):
        """Check system status"""
        self.print_header("System Status Check")
        
        try:
            # Check backend health
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend: {data['status']} - {data['service']} v{data['version']}")
            else:
                print(f"❌ Backend health check failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot connect to backend: {str(e)}")
        
        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Ollama: {len(models)} models available")
                for model in models[:3]:
                    print(f"   - {model.get('name')}")
            else:
                print(f"❌ Ollama not accessible: {response.status_code}")
        except Exception as e:
            print(f"❌ Ollama not accessible: {str(e)}")
        
        # Check sample data
        import os
        sample_data_path = "data/data_dirty.csv"
        if os.path.exists(sample_data_path):
            print(f"✅ Sample data: {sample_data_path} available")
        else:
            print(f"⚠️  Sample data: {sample_data_path} not found")
    
    def run_quick_demo(self):
        """Run a quick demonstration of all features"""
        self.print_header("Quick Demo - All Features")
        
        print("🚀 Running quick demonstration...")
        
        # Authenticate
        if self.authenticate():
            print("✅ Authentication: PASS")
            
            # Test AI chat
            try:
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                response = requests.post(
                    f"{self.base_url}/api/v1/ai/chat",
                    json={"message": "Say hello!", "provider": "ollama"},
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ AI Chat: PASS")
                else:
                    print("❌ AI Chat: FAIL")
            except:
                print("❌ AI Chat: FAIL")
            
            # Test project creation
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/projects/",
                    json={"name": "Quick Demo Project", "description": "Demo"},
                    headers=headers
                )
                if response.status_code in [200, 201]:
                    print("✅ Project Creation: PASS")
                else:
                    print("❌ Project Creation: FAIL")
            except:
                print("❌ Project Creation: FAIL")
            
            # Test dataset listing
            try:
                response = requests.get(f"{self.base_url}/api/v1/datasets/", headers=headers)
                if response.status_code == 200:
                    print("✅ Dataset Operations: PASS")
                else:
                    print("❌ Dataset Operations: FAIL")
            except:
                print("❌ Dataset Operations: FAIL")
        
        print("\n🎯 Quick demo completed!")
    
    def run(self):
        """Main interactive loop"""
        while True:
            self.print_menu()
            choice = input("Enter your choice (0-8): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.authenticate()
            elif choice == "2":
                self.test_ai_chat()
            elif choice == "3":
                self.test_project_management()
            elif choice == "4":
                self.test_dataset_operations()
            elif choice == "5":
                self.test_data_profiling()
            elif choice == "6":
                self.test_ai_code_generation()
            elif choice == "7":
                self.check_system_status()
            elif choice == "8":
                self.run_quick_demo()
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    demo = InteractiveDemo()
    demo.run()

if __name__ == "__main__":
    main() 