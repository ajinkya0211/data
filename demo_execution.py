#!/usr/bin/env python3
"""
Demo script for testing cell execution functionality
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"
DEMO_USER = {
    "email": "admin@example.com",
    "password": "admin123"
}

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def print_error(message):
    print(f"❌ {message}")

def authenticate():
    """Authenticate and get token"""
    print_header("Authentication")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login-json",
            json=DEMO_USER,
            timeout=10
        )
        
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

def create_test_project(token):
    """Create a test project for execution demo"""
    print_header("Creating Test Project")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/projects/",
            json={
                "name": "Execution Demo Project",
                "description": "Project to test cell execution functionality"
            },
            headers=headers
        )
        
        if response.status_code in [200, 201]:
            project = response.json()
            print_success(f"Project created: {project['name']}")
            return project['id']
        else:
            print_error(f"Project creation failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_error(f"Project creation error: {str(e)}")
        return None

def create_test_blocks(token, project_id):
    """Create test code blocks for execution"""
    print_header("Creating Test Code Blocks")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    blocks = [
        {
            "title": "Simple Math",
            "kind": "code",
            "language": "python",
            "content": "print('Hello from Python!')\nx = 5\ny = 10\nresult = x + y\nprint(f'{x} + {y} = {result}')",
            "project_id": project_id
        },
        {
            "title": "Data Analysis",
            "kind": "code",
            "language": "python",
            "content": "import pandas as pd\nimport numpy as np\n\n# Create sample data\ndata = pd.DataFrame({\n    'A': np.random.randn(10),\n    'B': np.random.randn(10),\n    'C': np.random.randn(10)\n})\n\nprint('Data shape:', data.shape)\nprint('\\nFirst few rows:')\nprint(data.head())\nprint('\\nSummary statistics:')\nprint(data.describe())",
            "project_id": project_id
        },
        {
            "title": "Error Demo",
            "kind": "code",
            "language": "python",
            "content": "print('This will cause an error')\nundefined_variable\nprint('This will not execute')",
            "project_id": project_id
        }
    ]
    
    created_blocks = []
    
    for block_data in blocks:
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/blocks/",
                json=block_data,
                headers=headers
            )
            
            if response.status_code in [200, 201]:
                block = response.json()
                created_blocks.append(block)
                print_success(f"Block created: {block['title']} (ID: {block['id'][:8]}...)")
            else:
                print_error(f"Block creation failed: {response.status_code}")
                
        except Exception as e:
            print_error(f"Block creation error: {str(e)}")
    
    return created_blocks

def test_cell_execution(token, blocks):
    """Test executing individual code blocks"""
    print_header("Testing Cell Execution")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    for block in blocks:
        if block['kind'] == 'code':
            print_info(f"Executing block: {block['title']}")
            
            try:
                response = requests.post(
                    f"{BASE_URL}/api/v1/blocks/{block['id']}/execute",
                    json={"block_ids": [block['id']]},
                    headers=headers,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print_success(f"Execution successful!")
                    print(f"   Status: {result['status']}")
                    print(f"   Execution time: {result.get('execution_time_ms', 'N/A')}ms")
                    
                    if result.get('outputs'):
                        print(f"   Outputs: {len(result['outputs'])} artifacts")
                        for output in result['outputs']:
                            print(f"     - {output['name']}: {output['content'][:100]}...")
                    
                    if result.get('error'):
                        print_warning(f"   Error: {result['error']}")
                        
                else:
                    print_error(f"Execution failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
            except Exception as e:
                print_error(f"Execution error: {str(e)}")
            
            print()  # Empty line between blocks

def test_multiple_execution(token, blocks):
    """Test executing multiple blocks in sequence"""
    print_header("Testing Multiple Block Execution")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get IDs of code blocks
    code_block_ids = [block['id'] for block in blocks if block['kind'] == 'code']
    
    if len(code_block_ids) < 2:
        print_warning("Need at least 2 code blocks for multiple execution test")
        return
    
    print_info(f"Executing {len(code_block_ids)} blocks in sequence")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/blocks/execute-multiple",
            json={"block_ids": code_block_ids},
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Multiple execution successful!")
            print(f"   Kernel ID: {result['kernel_id']}")
            print(f"   Results: {len(result['results'])} blocks executed")
            
            for i, block_result in enumerate(result['results']):
                print(f"   Block {i+1}: {block_result['status']}")
                if block_result.get('error'):
                    print(f"     Error: {block_result['error']}")
                    
        else:
            print_error(f"Multiple execution failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print_error(f"Multiple execution error: {str(e)}")

def test_kernel_management(token):
    """Test kernel management endpoints"""
    print_header("Testing Kernel Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # List kernels
        response = requests.get(f"{BASE_URL}/api/v1/blocks/kernels", headers=headers)
        
        if response.status_code == 200:
            kernels = response.json()
            print_success(f"Found {len(kernels)} kernels")
            
            for kernel in kernels:
                print(f"   - Kernel {kernel['id'][:8]}...: {kernel.get('name', 'Unknown')}")
                print(f"     Status: {kernel.get('execution_state', 'Unknown')}")
                
                # Stop kernel if it's running
                if kernel.get('execution_state') == 'busy':
                    print_info(f"   Stopping busy kernel {kernel['id'][:8]}...")
                    stop_response = requests.post(
                        f"{BASE_URL}/api/v1/blocks/kernels/{kernel['id']}/stop",
                        headers=headers
                    )
                    
                    if stop_response.status_code == 200:
                        print_success("   Kernel stopped successfully")
                    else:
                        print_error(f"   Failed to stop kernel: {stop_response.status_code}")
        else:
            print_error(f"Failed to list kernels: {response.status_code}")
            
    except Exception as e:
        print_error(f"Kernel management error: {str(e)}")

def main():
    """Main demo function"""
    print_header("🚀 Cell Execution Demo")
    print_info("This demo tests the new cell execution functionality")
    print_info("Make sure the backend is running and Jupyter is accessible")
    
    # Authenticate
    token = authenticate()
    if not token:
        print_error("Cannot proceed without authentication")
        return
    
    # Create test project
    project_id = create_test_project(token)
    if not project_id:
        print_error("Cannot proceed without a project")
        return
    
    # Create test blocks
    blocks = create_test_blocks(token, project_id)
    if not blocks:
        print_error("Cannot proceed without test blocks")
        return
    
    # Test individual execution
    test_cell_execution(token, blocks)
    
    # Test multiple execution
    test_multiple_execution(token, blocks)
    
    # Test kernel management
    test_kernel_management(token)
    
    print_header("🎯 Demo Summary")
    print_success("Cell execution demo completed!")
    print_info("Check the backend logs for detailed execution information")
    print_info("The LLM now has access to execution outputs for better context")

if __name__ == "__main__":
    main() 