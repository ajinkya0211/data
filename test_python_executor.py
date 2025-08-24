#!/usr/bin/env python3
"""
Test Python Executor Service
This script tests the Python executor service directly to ensure it works.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_python_executor():
    """Test the Python executor service"""
    try:
        from app.services.python_executor_service import PythonExecutorService
        
        print("🚀 Testing Python Executor Service")
        print("=" * 50)
        
        # Create executor service
        executor = PythonExecutorService()
        
        # Test 1: Start execution session
        print("\n📋 Test 1: Starting execution session...")
        session_id = await executor.start_execution_session("python3")
        if session_id:
            print(f"✅ Session started: {session_id}")
        else:
            print("❌ Failed to start session")
            return
        
        # Test 2: Execute simple code
        print("\n📋 Test 2: Executing simple Python code...")
        simple_code = '''
import pandas as pd
import numpy as np

print("Hello from Python executor!")
print("Testing basic imports...")

# Create some test data
data = {'A': [1, 2, 3, 4, 5], 'B': [10, 20, 30, 40, 50]}
df = pd.DataFrame(data)

print("DataFrame created:")
print(df)

print("Basic statistics:")
print(f"Mean of A: {df['A'].mean()}")
print(f"Mean of B: {df['B'].mean()}")

print("✅ Simple code execution completed!")
'''
        
        result = await executor.execute_code(session_id, simple_code, "test_block")
        
        if result:
            print(f"✅ Code execution completed!")
            print(f"   Status: {result.status}")
            print(f"   Execution time: {result.execution_time_ms}ms")
            print(f"   Outputs: {len(result.outputs)}")
            
            if result.outputs:
                print("\n📊 Outputs:")
                for i, output in enumerate(result.outputs):
                    print(f"   Output {i+1}:")
                    print(f"     Type: {output.get('type', 'unknown')}")
                    print(f"     Content: {output.get('content', '')[:200]}...")
        else:
            print("❌ Code execution failed")
        
        # Test 3: Execute data analysis code
        print("\n📋 Test 3: Executing data analysis code...")
        analysis_code = '''
import pandas as pd
import numpy as np

print("=== DATA ANALYSIS TEST ===")

# Create sample data similar to data_dirty.csv
np.random.seed(42)
n_samples = 100

data = {
    'product_id': range(1, n_samples + 1),
    'name': [f'Product_{i}' for i in range(1, n_samples + 1)],
    'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], n_samples),
    'price': np.random.normal(50, 20, n_samples),
    'sales': np.random.normal(1000, 300, n_samples),
    'rating': np.random.uniform(1, 5, n_samples)
}

df = pd.DataFrame(data)

print("Dataset Overview:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print("\\nFirst few rows:")
print(df.head())

print("\\nData types:")
print(df.dtypes)

print("\\nMissing values:")
print(df.isnull().sum())

print("\\nBasic statistics:")
print(df.describe())

print("\\nCategory distribution:")
print(df['category'].value_counts())

print("\\nPrice analysis:")
print(f"Mean price: ${df['price'].mean():.2f}")
print(f"Median price: ${df['price'].median():.2f}")
print(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")

print("\\nSales analysis:")
print(f"Mean sales: ${df['sales'].mean():.2f}")
print(f"Median sales: ${df['sales'].median():.2f}")
print(f"Sales range: ${df['sales'].min():.2f} - ${df['sales'].max():.2f}")

print("\\nRating analysis:")
print(f"Mean rating: {df['rating'].mean():.2f}")
print(f"Rating distribution:")
print(df['rating'].value_counts().sort_index())

print("\\n✅ Data analysis completed successfully!")
'''
        
        result2 = await executor.execute_code(session_id, analysis_code, "test_analysis_block")
        
        if result2:
            print(f"✅ Data analysis execution completed!")
            print(f"   Status: {result2.status}")
            print(f"   Execution time: {result2.execution_time_ms}ms")
            print(f"   Outputs: {len(result2.outputs)}")
            
            if result2.outputs:
                print("\n📊 Analysis Outputs:")
                for i, output in enumerate(result2.outputs):
                    print(f"   Output {i+1}:")
                    print(f"     Type: {output.get('type', 'unknown')}")
                    content = output.get('content', '')
                    if len(content) > 500:
                        print(f"     Content: {content[:500]}...")
                        print(f"     ... (truncated, total length: {len(content)})")
                    else:
                        print(f"     Content: {content}")
        else:
            print("❌ Data analysis execution failed")
        
        # Test 4: Stop session
        print("\n📋 Test 4: Stopping execution session...")
        success = await executor.stop_execution_session(session_id)
        if success:
            print("✅ Session stopped successfully")
        else:
            print("❌ Failed to stop session")
        
        print("\n🎉 Python Executor Service Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_python_executor()) 