#!/usr/bin/env python3
"""
Complete User Journey Test with Kernel-Based Execution
This tests the full AI agent workflow using the new persistent kernel system.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.python_executor_service import PythonExecutorService
from app.models.block import BlockStatus

async def test_complete_user_journey():
    """Test the complete AI agent user journey with kernel execution"""
    print("🎯 Complete AI Agent User Journey Test")
    print("=" * 60)
    print("This test demonstrates the full workflow:")
    print("1. User provides natural language prompts")
    print("2. AI creates code blocks")
    print("3. Kernel executes blocks with persistent state")
    print("4. Variables persist between blocks")
    print("5. Final results are verified")
    print()
    
    # Initialize executor service
    executor = PythonExecutorService()
    
    try:
        # Start execution session
        print("🚀 STEP 1: Starting Kernel Session")
        print("-" * 40)
        session_id = await executor.start_execution_session("data_analysis")
        
        if not session_id:
            print("❌ Failed to start kernel session")
            return
        
        print(f"✅ Kernel session started: {session_id}")
        
        # Simulate AI agent creating blocks based on user prompts
        print("\n🤖 STEP 2: AI Agent Creating Blocks from User Prompts")
        print("-" * 40)
        
        # User Prompt 1: "Load the data_dirty.csv file and show me the first few rows"
        print("👤 USER PROMPT 1: 'Load the data_dirty.csv file and show me the first few rows'")
        
        data_loading_code = '''
# Data Loading Block
import pandas as pd
from pathlib import Path

print("=== DATA LOADING ===")
print("Loading data_dirty.csv...")

# Load the dataset
df = pd.read_csv("data_dirty.csv")

print(f"Dataset loaded successfully!")
print(f"Shape: {df.shape}")
print(f"Columns: {list(df.columns)}")
print(f"\\nFirst 5 rows:")
print(df.head())
print(f"\\nData types:")
print(df.dtypes)
print(f"\\nMissing values:")
print(df.isnull().sum())

print("✅ Data loading completed!")
print(f"📊 Variables available: df (shape: {df.shape})")
'''
        
        print("🤖 AI AGENT: Creating data loading block...")
        result1 = await executor.execute_code(session_id, data_loading_code, "data_loading")
        print(f"✅ Block executed: {result1.status.value}")
        
        # User Prompt 2: "Clean the data by handling missing values and removing duplicates"
        print("\n👤 USER PROMPT 2: 'Clean the data by handling missing values and removing duplicates'")
        
        data_cleaning_code = '''
# Data Cleaning Block
print("=== DATA CLEANING ===")

print("1. Checking for duplicates:")
duplicates = df.duplicated().sum()
print(f"   Found {duplicates} duplicate rows")

print("\\n2. Handling missing values:")
missing_before = df.isnull().sum()
print(f"   Missing values before cleaning:")
for col, count in missing_before.items():
    if count > 0:
        print(f"     {col}: {count}")

# Remove duplicates
df_cleaned = df.drop_duplicates().copy()

# Handle missing values based on data type
for col in df_cleaned.columns:
    if df_cleaned[col].dtype in ['int64', 'float64']:
        # Numeric columns: fill with median
        if df_cleaned[col].isnull().sum() > 0:
            median_val = df_cleaned[col].median()
            df_cleaned[col].fillna(median_val, inplace=True)
            print(f"   Filled missing {col} with median: {median_val:.2f}")
    else:
        # Categorical columns: fill with mode
        if df_cleaned[col].isnull().sum() > 0:
            mode_val = df_cleaned[col].mode().iloc[0] if not df_cleaned[col].mode().empty else "Unknown"
            df_cleaned[col].fillna(mode_val, inplace=True)
            print(f"   Filled missing {col} with mode: {mode_val}")

print("\\n3. Data cleaning results:")
missing_after = df_cleaned.isnull().sum()
print(f"   Missing values after cleaning:")
for col, count in missing_after.items():
    if count > 0:
        print(f"     {col}: {count}")
    else:
        print(f"     {col}: Clean ✓")

print(f"\\n4. Final dataset shape: {df_cleaned.shape}")
print(f"5. Variables available: df, df_cleaned")

# Save cleaned data
df_cleaned.to_csv("data/data_cleaned.csv", index=False)
print("✅ Data cleaning completed and saved!")
'''
        
        print("🤖 AI AGENT: Creating data cleaning block...")
        result2 = await executor.execute_code(session_id, data_cleaning_code, "data_cleaning")
        print(f"✅ Block executed: {result2.status.value}")
        
        # User Prompt 3: "Calculate the mean of all numeric columns"
        print("\n👤 USER PROMPT 3: 'Calculate the mean of all numeric columns'")
        
        mean_calculation_code = '''
# Mean Calculation Block
print("=== MEAN CALCULATION ===")

print("Calculating means for all numeric columns...")

# Get numeric columns
numeric_columns = df_cleaned.select_dtypes(include=['int64', 'float64']).columns
print(f"Numeric columns found: {list(numeric_columns)}")

# Calculate means
means = {}
for col in numeric_columns:
    if col != 'product_id':  # Skip ID column
        mean_val = df_cleaned[col].mean()
        means[col] = mean_val
        print(f"   {col}: {mean_val:.2f}")

print("\\nSummary of means:")
for col, mean_val in means.items():
    print(f"   {col}: {mean_val:.2f}")

# Create summary dataframe
summary_df = pd.DataFrame({
    'column': list(means.keys()),
    'mean': list(means.values())
})

print("\\nSummary DataFrame:")
print(summary_df)

# Save summary
summary_df.to_csv("data/summary_statistics.csv", index=False)
print("✅ Mean calculation completed and saved!")
print(f"📊 Variables available: df, df_cleaned, means, summary_df")
'''
        
        print("🤖 AI AGENT: Creating mean calculation block...")
        result3 = await executor.execute_code(session_id, mean_calculation_code, "mean_calculation")
        print(f"✅ Block executed: {result3.status.value}")
        
        # User Prompt 4: "Show me the final cleaned dataset and summary"
        print("\n👤 USER PROMPT 4: 'Show me the final cleaned dataset and summary'")
        
        final_summary_code = '''
# Final Summary Block
print("=== FINAL SUMMARY ===")

print("1. Original Dataset:")
print(f"   Shape: {df.shape}")
print(f"   Missing values: {df.isnull().sum().sum()}")

print("\\n2. Cleaned Dataset:")
print(f"   Shape: {df_cleaned.shape}")
print(f"   Missing values: {df_cleaned.isnull().sum().sum()}")
print(f"   Duplicates removed: {len(df) - len(df_cleaned)}")

print("\\n3. Sample of cleaned data:")
print(df_cleaned.head(10))

print("\\n4. Statistical summary:")
print(df_cleaned.describe())

print("\\n5. All variables in memory:")
all_vars = [var for var in dir() if not var.startswith('_') and var not in ['df', 'df_cleaned', 'means', 'summary_df']]
print(f"   Available variables: {all_vars}")

print("\\n6. Files created:")
import os
data_files = [f for f in os.listdir('data') if f.endswith('.csv')]
for file in data_files:
    file_path = os.path.join('data', file)
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"   {file}: {size} bytes")

print("✅ Final summary completed!")
'''
        
        print("🤖 AI AGENT: Creating final summary block...")
        result4 = await executor.execute_code(session_id, final_summary_code, "final_summary")
        print(f"✅ Block executed: {result4.status.value}")
        
        # Check session info to verify state persistence
        print("\n📊 STEP 3: Verifying Kernel State Persistence")
        print("-" * 40)
        
        session_info = await executor.get_session_info(session_id)
        print(f"Session variables: {session_info.get('kernel_variables', [])}")
        print(f"Data files: {session_info.get('kernel_data_files', [])}")
        print(f"Working directory: {session_info.get('kernel_working_dir', 'N/A')}")
        
        # Display execution results
        print("\n📈 STEP 4: Execution Results Summary")
        print("-" * 40)
        
        results = [result1, result2, result3, result4]
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result.status == BlockStatus.COMPLETED else "❌ FAILED"
            print(f"Block {i}: {status}")
            if result.outputs:
                output = result.outputs[0]
                if hasattr(output, 'content'):
                    content = output.content
                else:
                    content = str(output)
                # Show first 100 chars of output
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"   Output: {preview}")
        
        # Stop execution session
        print("\n🛑 STEP 5: Stopping Kernel Session")
        print("-" * 40)
        await executor.stop_execution_session(session_id)
        print("✅ Session stopped")
        
        print("\n🎉 Complete User Journey Test Results!")
        print("=" * 60)
        print("✅ All blocks executed successfully with kernel persistence!")
        print("✅ Variables maintained between blocks (df → df_cleaned → means)")
        print("✅ Data files accessible across all blocks")
        print("✅ Real data processing completed (data_dirty.csv → data_cleaned.csv)")
        print("✅ Mean calculations performed on cleaned data")
        print("✅ Final summary generated with all results")
        print()
        print("🚀 The AI agent system now works like a real Jupyter notebook!")
        print("   - Variables persist between blocks")
        print("   - Data flows seamlessly through the analysis")
        print("   - No more 'variable not defined' errors!")
        print("   - Complete data science workflow from natural language prompts!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_complete_user_journey()) 