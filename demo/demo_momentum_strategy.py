#!/usr/bin/env python3
"""
Demo: Momentum Trading Strategy with Enhanced AI Notebook System
This script demonstrates how to use the enhanced system to create and execute
a momentum trading strategy workflow using AI agents.
"""

import asyncio
import json
import requests
import time
from pathlib import Path
import pandas as pd

class EnhancedNotebookDemo:
    """Demo class for the Enhanced AI Notebook System"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.dataset_id = None
        self.workflow_id = None
        
    def check_server(self):
        """Check if the server is running"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is running")
                print(f"   Status: {response.json()['status']}")
                print(f"   Version: {response.json()['version']}")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
            return False
    
    def upload_stock_data(self):
        """Upload the stock data sample"""
        print("\n📊 Uploading stock data...")
        
        stock_file = Path(__file__).parent / "stock_data_sample.csv"
        
        if not stock_file.exists():
            print("❌ Stock data file not found. Please ensure stock_data_sample.csv exists.")
            return False
        
        try:
            with open(stock_file, 'rb') as f:
                files = {'file': ('stock_data_sample.csv', f, 'text/csv')}
                response = requests.post(f"{self.base_url}/upload-dataset", files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.dataset_id = data['dataset_id']
                print(f"✅ Dataset uploaded successfully")
                print(f"   Dataset ID: {self.dataset_id}")
                print(f"   Rows: {data['dataset_info']['rows']}")
                print(f"   Columns: {len(data['dataset_info']['columns'])}")
                return True
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def create_momentum_strategy_workflow(self):
        """Create a momentum strategy workflow using AI"""
        print("\n🤖 Creating momentum strategy workflow with AI...")
        
        if not self.dataset_id:
            print("❌ No dataset ID available. Upload data first.")
            return False
        
        prompt = """
        Create a comprehensive momentum trading strategy workflow for this stock data. 
        The workflow should include:
        
        1. Data loading and preprocessing
        2. Momentum indicator calculation (5-day and 20-day momentum)
        3. Trading signal generation based on momentum crossovers
        4. Position sizing and risk management
        5. Backtesting framework with performance metrics
        6. Visualization of results including:
           - Price and momentum charts
           - Trading signals
           - Performance metrics
           - Drawdown analysis
        
        Make sure to include proper error handling, data validation, and clear documentation.
        Use pandas for data manipulation, matplotlib/seaborn for visualization, and numpy for calculations.
        """
        
        try:
            payload = {
                "prompt": prompt,
                "dataset_id": self.dataset_id
            }
            
            response = requests.post(
                f"{self.base_url}/ai/process",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.workflow_id = data['workflow_id']
                
                print(f"✅ AI workflow created successfully")
                print(f"   Workflow ID: {self.workflow_id}")
                print(f"   Blocks generated: {len(data['blocks'])}")
                print(f"   DAG nodes: {len(data['dag_info']['nodes'])}")
                print(f"   DAG edges: {len(data['dag_info']['edges'])}")
                
                # Show execution plan
                if data['execution_plan']:
                    print(f"\n📋 Execution Plan:")
                    for i, plan_item in enumerate(data['execution_plan']):
                        print(f"   {i+1}. Block {plan_item['block_id'][:8]}... ({plan_item['block_type']})")
                
                # Show agent responses
                if data.get('agent_responses'):
                    print(f"\n🤖 AI Agent Responses:")
                    for agent in data['agent_responses']:
                        print(f"   - {agent['agent_type']}: {agent['content'][:100]}...")
                
                return True
            else:
                print(f"❌ Workflow creation failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Workflow creation error: {e}")
            return False
    
    def get_workflow_details(self):
        """Get detailed workflow information"""
        print("\n📋 Getting workflow details...")
        
        if not self.workflow_id:
            print("❌ No workflow ID available.")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/workflows/{self.workflow_id}")
            
            if response.status_code == 200:
                data = response.json()
                workflow = data['workflow']
                
                print(f"✅ Workflow details retrieved")
                print(f"   Name: {workflow['name']}")
                print(f"   Status: {workflow['execution_status']}")
                print(f"   Created: {workflow['created_at']}")
                
                # Show blocks
                print(f"\n📦 Workflow Blocks:")
                for i, block in enumerate(workflow['blocks']):
                    print(f"   {i+1}. {block['type']} block at ({block['position']['x']}, {block['position']['y']})")
                    print(f"      Content preview: {block['content'][:80]}...")
                
                # Show DAG info
                if workflow.get('dag_info'):
                    dag = workflow['dag_info']
                    print(f"\n🔄 DAG Information:")
                    print(f"   Nodes: {len(dag['nodes'])}")
                    print(f"   Edges: {len(dag['edges'])}")
                    print(f"   Execution order: {len(dag['execution_order'])} blocks")
                
                return True
            else:
                print(f"❌ Failed to get workflow details: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting workflow details: {e}")
            return False
    
    def execute_workflow(self):
        """Execute the entire workflow"""
        print("\n▶️  Executing workflow...")
        
        if not self.workflow_id:
            print("❌ No workflow ID available.")
            return False
        
        try:
            response = requests.post(f"{self.base_url}/workflows/{self.workflow_id}/execute")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Workflow execution completed")
                print(f"   Results: {len(data['results'])} blocks executed")
                print(f"   Execution plan: {len(data['execution_plan'])} items")
                
                # Show execution results
                print(f"\n📊 Execution Results:")
                for i, result in enumerate(data['results']):
                    status = "✅" if result['execution_result']['success'] else "❌"
                    print(f"   {i+1}. {status} Block {result['block_id'][:8]}...")
                    print(f"      Time: {result['execution_result']['execution_time']:.2f}s")
                    
                    if not result['execution_result']['success']:
                        print(f"      Error: {result['execution_result']['error']}")
                
                return True
            else:
                print(f"❌ Workflow execution failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Workflow execution error: {e}")
            return False
    
    def get_system_status(self):
        """Get overall system status"""
        print("\n🔍 Getting system status...")
        
        try:
            response = requests.get(f"{self.base_url}/system/status")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ System status retrieved")
                print(f"   Status: {data['status']}")
                print(f"   Timestamp: {data['timestamp']}")
                
                # Show component status
                components = data['components']
                print(f"\n🔧 Component Status:")
                print(f"   MCP System: {components['mcp_system']['ollama_available']}")
                print(f"   DAG System: {components['dag_system']['total_blocks']} blocks")
                print(f"   Python Executor: {components['python_executor']['active_sessions']} sessions")
                
                # Show metrics
                metrics = data['metrics']
                print(f"\n📈 System Metrics:")
                print(f"   Datasets: {metrics['datasets_count']}")
                print(f"   Workflows: {metrics['workflows_count']}")
                print(f"   Active Sessions: {metrics['active_sessions']}")
                print(f"   Total Blocks: {metrics['total_blocks']}")
                
                return True
            else:
                print(f"❌ Failed to get system status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting system status: {e}")
            return False
    
    def run_demo(self):
        """Run the complete demo"""
        print("🚀 Enhanced AI Notebook System - Momentum Strategy Demo")
        print("=" * 70)
        
        # Check server
        if not self.check_server():
            return False
        
        # Get system status
        self.get_system_status()
        
        # Upload data
        if not self.upload_stock_data():
            return False
        
        # Create workflow
        if not self.create_momentum_strategy_workflow():
            return False
        
        # Get workflow details
        self.get_workflow_details()
        
        # Execute workflow
        if not self.execute_workflow():
            return False
        
        # Final status
        print("\n" + "=" * 70)
        print("🎉 Demo completed successfully!")
        print("\nNext steps:")
        print(f"1. View workflow: http://localhost:8000/workflows/{self.workflow_id}")
        print(f"2. API docs: http://localhost:8000/docs")
        print(f"3. System status: http://localhost:8000/system/status")
        print("\nThe AI has created a complete momentum trading strategy workflow!")
        print("You can now:")
        print("- Modify the generated blocks")
        print("- Add new analysis blocks")
        print("- Execute individual blocks")
        print("- View the DAG visualization")
        print("- Monitor real-time execution")
        
        return True

def main():
    """Main demo function"""
    demo = EnhancedNotebookDemo()
    
    try:
        success = demo.run_demo()
        if success:
            print("\n✅ Demo completed successfully!")
        else:
            print("\n❌ Demo failed. Check the output above for details.")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()
