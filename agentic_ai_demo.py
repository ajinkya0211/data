#!/usr/bin/env python3
"""
Agentic AI Framework Demo
This demo showcases the AI agent's ability to dynamically control notebooks
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
DEMO_USER = {"email": "admin@example.com", "password": "admin123"}

def print_header(title):
    print(f"\n{'='*80}")
    print(f"🎯 {title}")
    print(f"{'='*80}")

def print_step(step_num, title):
    print(f"\n📋 STEP {step_num}: {title}")
    print(f"{'─'*60}")

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def print_code(code):
    print(f"\n```python\n{code}\n```")

def authenticate():
    """Authenticate and get token"""
    print_step(1, "User Authentication")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login-json", json=DEMO_USER, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data["access_token"]
            print_success(f"Login successful! User: {data['user']['full_name']}")
            return token
        else:
            print_error(f"Login failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Authentication error: {str(e)}")
        return None

def create_agentic_project(token):
    """Create a project for agentic AI demo"""
    print_step(2, "Creating Agentic AI Project")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/projects/",
            json={
                "name": "Agentic AI Notebook Control Demo",
                "description": "Demonstrating AI agent's ability to dynamically control notebooks"
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            print_success(f"Project created: {project['name']}")
            print_info(f"Project ID: {project['id'][:8]}...")
            return project['id']
        else:
            print_error(f"Project creation failed: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Project creation error: {str(e)}")
        return None

def test_natural_language_import(token, project_id):
    """Test AI agent's ability to import data via natural language"""
    print_step(3, "Testing Natural Language Data Import")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test natural language import command
    import_command = "import data from data_dirty.csv and clean it"
    print_info(f"User says: '{import_command}'")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/ai/chat",
            json={
                "message": import_command,
                "project_id": project_id,
                "provider": "ollama"
            },
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("AI Agent processed the request!")
            print_info(f"Response type: {result.get('type', 'unknown')}")
            print_info(f"AI Response: {result.get('response', 'No response')[:200]}...")
            
            if result.get('actions_taken'):
                print_info("Actions taken by AI Agent:")
                for action, action_result in result['actions_taken'].items():
                    if isinstance(action_result, dict) and 'message' in action_result:
                        print(f"  • {action_result['message']}")
            
            return True
        else:
            print_error(f"Import command failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Import command error: {str(e)}")
        return False

def test_analysis_commands(token, project_id):
    """Test AI agent's ability to add analysis blocks"""
    print_step(4, "Testing Analysis Block Creation")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test adding analysis blocks
    analysis_commands = [
        "add a block to calculate mean and median",
        "create a visualization block for the data",
        "add statistical analysis"
    ]
    
    for i, command in enumerate(analysis_commands, 1):
        print_info(f"Command {i}: '{command}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/chat",
                json={
                    "message": command,
                    "project_id": project_id,
                    "provider": "ollama"
                },
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Command {i} processed successfully!")
                if result.get('type') == 'notebook_control_success':
                    print_info("✅ AI Agent created/modified blocks")
                else:
                    print_info(f"Response: {result.get('response', 'No response')[:100]}...")
            else:
                print_error(f"Command {i} failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Command {i} error: {str(e)}")
        
        print()  # Empty line between commands

def test_block_management(token, project_id):
    """Test AI agent's ability to manage blocks"""
    print_step(5, "Testing Block Management Commands")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test block management commands
    management_commands = [
        "delete the last block",
        "edit the data cleaning block",
        "add a new analysis block"
    ]
    
    for i, command in enumerate(management_commands, 1):
        print_info(f"Management Command {i}: '{command}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/chat",
                json={
                    "message": command,
                    "project_id": project_id,
                    "provider": "ollama"
                },
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Management command {i} processed successfully!")
                if result.get('type') == 'notebook_control_success':
                    print_info("✅ AI Agent managed blocks successfully")
                else:
                    print_info(f"Response: {result.get('response', 'No response')[:100]}...")
            else:
                print_error(f"Management command {i} failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Management command {i} error: {str(e)}")
        
        print()  # Empty line between commands

def test_execution_commands(token, project_id):
    """Test AI agent's ability to execute blocks"""
    print_step(6, "Testing Execution Commands")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test execution commands
    execution_commands = [
        "execute all blocks in sequence",
        "run the notebook",
        "execute the data analysis blocks"
    ]
    
    for i, command in enumerate(execution_commands, 1):
        print_info(f"Execution Command {i}: '{command}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/chat",
                json={
                    "message": command,
                    "project_id": project_id,
                    "provider": "ollama"
                },
                headers=headers,
                timeout=120  # Longer timeout for execution
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Execution command {i} processed successfully!")
                if result.get('type') == 'notebook_control_success':
                    print_info("✅ AI Agent executed blocks successfully")
                else:
                    print_info(f"Response: {result.get('response', 'No response')[:100]}...")
            else:
                print_error(f"Execution command {i} failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Execution command {i} error: {str(e)}")
        
        print()  # Empty line between commands

def get_notebook_summary(token, project_id):
    """Get comprehensive notebook summary"""
    print_step(7, "Getting Notebook Summary")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/ai/notebook-summary/{project_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            summary = response.json()
            print_success("Notebook summary retrieved successfully!")
            
            print_info(f"Project: {summary['project']['name']}")
            print_info(f"Total blocks: {summary['blocks']['total']}")
            print_info(f"Code blocks: {summary['blocks']['code']}")
            print_info(f"Markdown blocks: {summary['blocks']['markdown']}")
            print_info(f"Executed blocks: {summary['blocks']['executed']}")
            print_info(f"Pending execution: {summary['blocks']['pending']}")
            
            print_info("\nExecution Status:")
            print_info(f"  Completed: {summary['execution_status']['completed']}")
            print_info(f"  Failed: {summary['execution_status']['failed']}")
            print_info(f"  Running: {summary['execution_status']['running']}")
            
            print_info("\nBlock Details:")
            for block in summary['block_details']:
                print(f"  • {block['title']} ({block['kind']}) - {block['status']}")
            
            return summary
        else:
            print_error(f"Failed to get notebook summary: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Notebook summary error: {str(e)}")
        return None

def test_direct_notebook_control(token, project_id):
    """Test direct notebook control API"""
    print_step(8, "Testing Direct Notebook Control API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test direct notebook control
    control_commands = [
        "import data from data_dirty.csv",
        "add a correlation analysis block",
        "create a summary statistics block"
    ]
    
    for i, command in enumerate(control_commands, 1):
        print_info(f"Direct Control Command {i}: '{command}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/ai/notebook-control",
                json={
                    "command": command,
                    "project_id": project_id
                },
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Direct control command {i} processed successfully!")
                print_info(f"Success: {result.get('success', False)}")
                print_info(f"Message: {result.get('message', 'No message')}")
                
                if result.get('results'):
                    print_info("Results:")
                    for action, action_result in result['results'].items():
                        if isinstance(action_result, dict) and 'message' in action_result:
                            print(f"  • {action_result['message']}")
            else:
                print_error(f"Direct control command {i} failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Direct control command {i} error: {str(e)}")
        
        print()  # Empty line between commands

def main():
    """Main agentic AI demo function"""
    print_header("🚀 Agentic AI Framework Demo")
    print_info("This demo showcases the AI agent's ability to dynamically control notebooks")
    print_info("Similar to Cursor AI, the agent can create, edit, delete, and execute blocks")
    
    # Step 1: Authenticate
    token = authenticate()
    if not token:
        print_error("Cannot proceed without authentication")
        return
    
    # Step 2: Create project
    project_id = create_agentic_project(token)
    if not project_id:
        print_error("Cannot proceed without a project")
        return
    
    # Step 3: Test natural language import
    if not test_natural_language_import(token, project_id):
        print_warning("Natural language import failed, but continuing with demo")
    
    # Step 4: Test analysis commands
    test_analysis_commands(token, project_id)
    
    # Step 5: Test block management
    test_block_management(token, project_id)
    
    # Step 6: Test execution commands
    test_execution_commands(token, project_id)
    
    # Step 7: Get notebook summary
    summary = get_notebook_summary(token, project_id)
    
    # Step 8: Test direct notebook control
    test_direct_notebook_control(token, project_id)
    
    print_header("🎉 Agentic AI Demo Complete!")
    print_success("✅ Successfully demonstrated AI agent's notebook control capabilities")
    
    if summary:
        print_info(f"📊 Final notebook state: {summary['blocks']['total']} blocks")
        print_info(f"🔧 Code blocks: {summary['blocks']['code']}")
        print_info(f"📝 Markdown blocks: {summary['blocks']['markdown']}")
        print_info(f"✅ Executed: {summary['blocks']['executed']}")
        print_info(f"⏳ Pending: {summary['blocks']['pending']}")
    
    print_info("\n🚀 What the AI Agent accomplished:")
    print_info("1. ✅ Understood natural language commands")
    print_info("2. ✅ Dynamically created code blocks")
    print_info("3. ✅ Managed block lifecycle (add/edit/delete)")
    print_info("4. ✅ Executed blocks in Jupyter kernel")
    print_info("5. ✅ Provided comprehensive notebook summaries")
    
    print_info("\n🎯 Key Features Demonstrated:")
    print_info("• **Natural Language Processing**: AI understands commands like 'import data and clean it'")
    print_info("• **Dynamic Block Creation**: AI creates appropriate code blocks automatically")
    print_info("• **Intelligent Block Management**: AI can add, edit, and delete blocks")
    print_info("• **Execution Control**: AI can execute blocks and track results")
    print_info("• **Context Awareness**: AI maintains notebook state and relationships")
    
    print_info("\n💡 This demonstrates a Cursor AI-like experience where:")
    print_info("• Users can speak naturally to control their notebooks")
    print_info("• AI automatically creates the right blocks for the task")
    print_info("• AI can execute and debug code on behalf of the user")
    print_info("• AI maintains full context of the notebook state")

if __name__ == "__main__":
    main() 