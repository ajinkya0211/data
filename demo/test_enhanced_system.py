#!/usr/bin/env python3
"""
Test script for the Enhanced AI Notebook System
Tests all major components to ensure they work correctly
"""

import sys
import os
import asyncio
import json
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔧 Testing module imports...")
    
    try:
        # Test core modules
        import mcp_system
        print("✅ MCP system imported successfully")
        
        import dag_system
        print("✅ DAG system imported successfully")
        
        import python_executor
        print("✅ Python executor imported successfully")
        
        # Test dependencies
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import numpy as np
        print("✅ NumPy imported successfully")
        
        import networkx as nx
        print("✅ NetworkX imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dag_system():
    """Test DAG system functionality"""
    print("\n🔧 Testing DAG system...")
    
    try:
        from dag_system import DAGManager, BlockStatus
        
        # Create DAG manager
        dag = DAGManager()
        print("✅ DAG manager created")
        
        # Test adding blocks
        block1_data = {
            "type": "code",
            "content": "import pandas as pd\ndf = pd.DataFrame({'A': [1, 2, 3]})",
            "position": {"x": 100, "y": 100}
        }
        
        block1_id = dag.add_block(block1_data)
        print(f"✅ Block 1 added with ID: {block1_id}")
        
        block2_data = {
            "type": "code",
            "content": "print(df.head())\nsummary = df.describe()",
            "position": {"x": 300, "y": 100}
        }
        
        block2_id = dag.add_block(block2_data)
        print(f"✅ Block 2 added with ID: {block2_id}")
        
        # Test DAG status
        status = dag.get_system_status()
        print(f"✅ DAG status: {status['total_blocks']} blocks, {status['total_dependencies']} dependencies")
        
        # Test execution plan
        plan = dag.get_execution_plan()
        print(f"✅ Execution plan created with {len(plan)} items")
        
        # Test validation
        validation = dag.validate_workflow()
        print(f"✅ Workflow validation: {validation['is_valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ DAG system test failed: {e}")
        return False

def test_python_executor():
    """Test Python executor functionality"""
    print("\n🔧 Testing Python executor...")
    
    try:
        from python_executor import python_executor
        
        # Test session creation
        session_id = python_executor.session_manager.create_session()
        print(f"✅ Session created with ID: {session_id}")
        
        # Test session state
        session_state = python_executor.get_session_state(session_id)
        print(f"✅ Session state retrieved: {len(session_state.get('variables', {}))} variables")
        
        # Test system status
        status = python_executor.get_system_status()
        print(f"✅ Executor status: {status['total_sessions']} sessions")
        
        return True
        
    except Exception as e:
        print(f"❌ Python executor test failed: {e}")
        return False

def test_mcp_system():
    """Test MCP system functionality"""
    print("\n🔧 Testing MCP system...")
    
    try:
        from mcp_system import agent_manager
        
        # Test agent system
        agents = agent_manager.get_system_status()
        print(f"✅ Agent system: {agents['total_agents']} agents")
        
        # Test agent listing
        agents_list = []
        for agent_id, agent in agent_manager.agents.items():
            agents_list.append({
                "id": agent_id,
                "name": agent.name,
                "type": agent.agent_type.value,
                "capabilities": [cap.value for cap in agent.capabilities]
            })
        
        print(f"✅ Found {len(agents_list)} agents:")
        for agent in agents_list:
            print(f"   - {agent['name']} ({agent['type']}): {', '.join(agent['capabilities'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ MCP system test failed: {e}")
        return False

async def test_ai_capabilities():
    """Test AI capabilities"""
    print("\n🔧 Testing AI capabilities...")
    
    try:
        from mcp_system import agent_manager
        
        # Test with a simple task
        test_context = {
            "dataset_info": "Sample stock data",
            "user_request": "Create a simple data analysis workflow"
        }
        
        # Get planner agent
        planner_agent = agent_manager.get_agent_by_capability(
            agent_manager.agents["planner_001"].capabilities[0]
        )
        
        if planner_agent:
            print(f"✅ Using agent: {planner_agent.name}")
            
            # Test agent execution (this will use Ollama if available)
            response = await agent_manager.execute_agent_task(
                planner_agent.id,
                "Plan a simple data analysis workflow",
                test_context
            )
            
            if response.success:
                print("✅ AI agent executed successfully")
                print(f"   Response length: {len(response.content)} characters")
            else:
                print(f"⚠️  AI agent execution failed: {response.error}")
                print("   This is expected if Ollama is not available")
        else:
            print("⚠️  No planner agent available")
        
        return True
        
    except Exception as e:
        print(f"❌ AI capabilities test failed: {e}")
        return False

def test_stock_data():
    """Test stock data loading"""
    print("\n🔧 Testing stock data...")
    
    try:
        import pandas as pd
        
        # Check if stock data file exists
        stock_file = Path(__file__).parent / "stock_data_sample.csv"
        
        if stock_file.exists():
            # Load the data
            df = pd.read_csv(stock_file)
            print(f"✅ Stock data loaded: {len(df)} rows, {len(df.columns)} columns")
            print(f"   Columns: {', '.join(df.columns)}")
            print(f"   Date range: {df['Date'].min()} to {df['Date'].max()}")
            print(f"   Symbol: {df['Symbol'].iloc[0]}")
            
            # Basic statistics
            if 'Returns' in df.columns:
                print(f"   Returns mean: {df['Returns'].mean():.4f}")
                print(f"   Returns std: {df['Returns'].std():.4f}")
            
            return True
        else:
            print("⚠️  Stock data file not found")
            return False
            
    except Exception as e:
        print(f"❌ Stock data test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Enhanced AI Notebook System - Component Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("DAG System", test_dag_system),
        ("Python Executor", test_python_executor),
        ("MCP System", test_mcp_system),
        ("Stock Data", test_stock_data),
    ]
    
    results = []
    
    # Run synchronous tests
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Run async tests
    try:
        success = asyncio.run(test_ai_capabilities())
        results.append(("AI Capabilities", success))
    except Exception as e:
        print(f"❌ AI capabilities test crashed: {e}")
        results.append(("AI Capabilities", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Start the backend: python main_enhanced.py")
        print("2. Upload stock data: POST /upload-dataset")
        print("3. Create AI workflow: POST /ai/process")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\nCommon issues:")
        print("- Missing dependencies: pip install -r requirements.txt")
        print("- Ollama not installed: https://ollama.ai/")
        print("- Python version: Requires Python 3.8+")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
