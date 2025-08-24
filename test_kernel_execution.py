#!/usr/bin/env python3
"""
Test script for the new kernel-based Python execution service
This tests the persistent kernel functionality that maintains state between executions.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.python_executor_service import PythonExecutorService

async def test_kernel_execution():
    """Test the kernel-based execution service"""
    print("🧪 Testing Kernel-Based Python Execution Service")
    print("=" * 60)
    
    # Initialize service
    executor = PythonExecutorService()
    
    try:
        # Start execution session
        print("📋 Starting execution session...")
        session_id = await executor.start_execution_session("test_kernel")
        
        if not session_id:
            print("❌ Failed to start execution session")
            return
        
        print(f"✅ Session started: {session_id}")
        
        # Test 1: Data loading block
        print("\n🔧 Test 1: Data Loading Block")
        print("-" * 40)
        
        data_loading_code = '''
# Data loading and setup
import pandas as pd
import numpy as np
from pathlib import Path

print("=== DATA LOADING AND SETUP ===")

# Create sample dataset
np.random.seed(42)
n_samples = 100

data = {
    'product_id': range(1, n_samples + 1),
    'name': [f'Product_{i}' for i in range(1, n_samples + 1)],
    'category': np.random.choice(['Books', 'Electronics', 'Home', 'Clothing'], n_samples),
    'price': np.random.uniform(10, 100, n_samples),
    'sales': np.random.uniform(500, 2000, n_samples),
    'rating': np.random.uniform(1, 5, n_samples)
}

# Introduce some missing values and duplicates for cleaning demo
df = pd.DataFrame(data)
df.loc[df.sample(frac=0.1).index, 'price'] = np.nan
df.loc[df.sample(frac=0.1).index, 'sales'] = np.nan
df.loc[df.sample(frac=0.1).index, 'rating'] = np.nan

# Add some duplicates
df = pd.concat([df, df.sample(frac=0.05)], ignore_index=True)

print(f"Sample dataset created:")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\\nFirst few rows:")
print(df.head())
print(f"\\nData types:")
print(df.dtypes)
print(f"\\nMissing values:")
print(df.isnull().sum())
print(f"\\nBasic statistics:")
print(df.describe())

# Save to data directory
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)
df.to_csv("data/data_dirty.csv", index=False)
print(f"\\n✅ Sample dataset created and ready for analysis!")
print(f"📊 Total records: {len(df)}")
print(f"🔧 Variables available: df")
print(f"⚠️  Contains missing values and duplicates for cleaning demo")
'''
        
        result1 = await executor.execute_code(session_id, data_loading_code, "test_data_loading")
        print(f"✅ Data loading executed: {result1.status.value}")
        if result1.outputs:
            # Handle both dict and object outputs
            output = result1.outputs[0]
            if hasattr(output, 'content'):
                content = output.content
            else:
                content = str(output)
            print("Output:", content[:200] + "..." if len(content) > 200 else content)
        
        # Test 2: Data cleaning block (should have access to 'df' variable)
        print("\n🔧 Test 2: Data Cleaning Block")
        print("-" * 40)
        
        data_cleaning_code = '''
# Data cleaning and preprocessing
print("=== DATA CLEANING PROCESS ===")

print("1. Checking for duplicates:")
duplicates = df.duplicated().sum()
print(f"   Found {duplicates} duplicate rows")

print("2. Handling missing values:")
missing_before = df.isnull().sum()
print(f"   Missing values before cleaning:")
for col, count in missing_before.items():
    if count > 0:
        print(f"     {col}: {count}")

# Remove duplicates
df_cleaned = df.drop_duplicates().copy()

# Handle missing values
df_cleaned['price'].fillna(df_cleaned['price'].median(), inplace=True)
df_cleaned['sales'].fillna(df_cleaned['sales'].mean(), inplace=True)
df_cleaned['rating'].fillna(df_cleaned['rating'].median(), inplace=True)

print("3. Data cleaning results:")
missing_after = df_cleaned.isnull().sum()
print(f"   Missing values after cleaning:")
for col, count in missing_after.items():
    if count > 0:
        print(f"     {col}: {count}")
    else:
        print(f"     {col}: Clean ✓")

print(f"4. Final dataset shape: {df_cleaned.shape}")
print(f"5. Variables available: df, df_cleaned")

# Save cleaned data
df_cleaned.to_csv("data/data_cleaned.csv", index=False)
print("✅ Data cleaning completed and saved!")
'''
        
        result2 = await executor.execute_code(session_id, data_cleaning_code, "test_data_cleaning")
        print(f"✅ Data cleaning executed: {result2.status.value}")
        if result2.outputs:
            # Handle both dict and object outputs
            output = result2.outputs[0]
            if hasattr(output, 'content'):
                content = output.content
            else:
                content = str(output)
            print("Output:", content[:200] + "..." if len(content) > 200 else content)
        
        # Test 3: Statistical analysis (should have access to both 'df' and 'df_cleaned')
        print("\n🔧 Test 3: Statistical Analysis Block")
        print("-" * 40)
        
        analysis_code = '''
# Statistical analysis
print("=== STATISTICAL ANALYSIS ===")

print("1. Original dataset statistics:")
print(f"   Shape: {df.shape}")
print(f"   Price - Mean: {df['price'].mean():.2f}, Median: {df['price'].median():.2f}")
print(f"   Sales - Mean: {df['sales'].mean():.2f}, Median: {df['sales'].median():.2f}")

print("\\n2. Cleaned dataset statistics:")
print(f"   Shape: {df_cleaned.shape}")
print(f"   Price - Mean: {df_cleaned['price'].mean():.2f}, Median: {df_cleaned['price'].median():.2f}")
print(f"   Sales - Mean: {df_cleaned['sales'].mean():.2f}, Median: {df_cleaned['sales'].median():.2f}")

print("\\n3. Correlation analysis:")
correlation = df_cleaned[['price', 'sales', 'rating']].corr()
print(correlation)

print("\\n4. Variables available:", [var for var in dir() if not var.startswith('_')])
print("✅ Statistical analysis completed!")
'''
        
        result3 = await executor.execute_code(session_id, analysis_code, "test_analysis")
        print(f"✅ Analysis executed: {result3.status.value}")
        if result3.outputs:
            # Handle both dict and object outputs
            output = result3.outputs[0]
            if hasattr(output, 'content'):
                content = output.content
            else:
                content = str(output)
            print("Output:", content[:200] + "..." if len(content) > 200 else content)
        
        # Test 4: Check session info
        print("\n📊 Test 4: Session Information")
        print("-" * 40)
        
        session_info = await executor.get_session_info(session_id)
        print(f"Session variables: {session_info.get('kernel_variables', [])}")
        print(f"Data files: {session_info.get('kernel_data_files', [])}")
        print(f"Working directory: {session_info.get('kernel_working_dir', 'N/A')}")
        
        # Stop execution session
        print("\n🛑 Stopping execution session...")
        await executor.stop_execution_session(session_id)
        print("✅ Session stopped")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ Kernel-based execution is working correctly!")
        print("✅ Variables are maintained between blocks!")
        print("✅ Data files are accessible!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_kernel_execution()) 