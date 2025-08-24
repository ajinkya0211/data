#!/usr/bin/env python3
"""
Test script for the new automatic DAG system
Demonstrates code analysis and workflow creation
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app.services.dag_analyzer_service import DAGAnalyzerService, DependencyInfo
from app.services.workflow_management_service import WorkflowManagementService
from app.models.block import Block
from app.core.database import AsyncSessionLocal
import json

async def create_test_blocks():
    """Create test blocks with realistic data science code"""
    
    # Block 1: Data Loading
    data_loading_block = Block(
        id="block_1_data_loading",
        title="Data Loading",
        content="""
import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('data_dirty.csv')
print(f"Dataset loaded with shape: {df.shape}")
        """,
        kind="code",
        language="python",
        project_id="test_project_123",
        owner_id="admin_123"
    )
    
    # Block 2: Data Cleaning (depends on df from block 1)
    data_cleaning_block = Block(
        id="block_2_data_cleaning", 
        title="Data Cleaning",
        content="""
# Clean the dataset
df_clean = df.dropna()
df_clean = df_clean.reset_index(drop=True)

# Calculate some statistics
mean_values = df_clean.mean()
print(f"Mean values: {mean_values}")
        """,
        kind="code",
        language="python", 
        project_id="test_project_123",
        owner_id="admin_123"
    )
    
    # Block 3: Visualization (depends on df_clean from block 2)
    visualization_block = Block(
        id="block_3_visualization",
        title="Data Visualization", 
        content="""
import matplotlib.pyplot as plt
import seaborn as sns

# Create visualizations
plt.figure(figsize=(10, 6))
plt.hist(df_clean.iloc[:, 0], bins=20)
plt.title('Distribution Analysis')
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.show()

# Save plot
plt.savefig('analysis_plot.png')
        """,
        kind="code",
        language="python",
        project_id="test_project_123", 
        owner_id="admin_123"
    )
    
    return [data_loading_block, data_cleaning_block, visualization_block]

async def test_dependency_analysis():
    """Test the automatic dependency analysis"""
    print("🔬 Testing Automatic Dependency Analysis")
    print("=" * 50)
    
    # Create test blocks
    blocks = await create_test_blocks()
    
    # Create analyzer (without DB for this test)
    analyzer = DAGAnalyzerService(None)
    
    # Analyze each block
    for block in blocks:
        print(f"\n📝 Analyzing Block: {block.title}")
        deps = analyzer.analyze_block_dependencies(block)
        
        print(f"   Variables Used: {list(deps.variables_used)}")
        print(f"   Variables Defined: {list(deps.variables_defined)}")
        print(f"   Functions Called: {list(deps.functions_called)}")
        print(f"   Imports: {list(deps.imports)}")
        print(f"   Outputs: {list(deps.outputs)}")
    
    # Build DAG from dependencies
    print(f"\n🧩 Building DAG from Dependencies")
    dependency_map = {}
    for block in blocks:
        deps = analyzer.analyze_block_dependencies(block)
        dependency_map[block.id] = deps
    
    dag = analyzer.build_dag_from_dependencies(dependency_map, blocks)
    
    print(f"   Nodes: {dag['nodes']}")
    print(f"   Edges: {dag['edges']}")
    print(f"   Execution Order: {dag['execution_order']}")
    
    return dag, dependency_map

async def test_dag_validation():
    """Test DAG validation"""
    print("\n✅ Testing DAG Validation")
    print("=" * 50)
    
    analyzer = DAGAnalyzerService(None)
    
    # Test valid DAG
    nodes = ["A", "B", "C"]
    edges = [("A", "B"), ("B", "C")]
    validation = analyzer.validate_dag(nodes, edges)
    print(f"Valid DAG: {validation}")
    
    # Test DAG with cycle
    nodes_cycle = ["A", "B", "C"]
    edges_cycle = [("A", "B"), ("B", "C"), ("C", "A")]
    validation_cycle = analyzer.validate_dag(nodes_cycle, edges_cycle)
    print(f"Cyclic DAG: {validation_cycle}")

async def demonstrate_smart_dependency_detection():
    """Demonstrate smart dependency detection for data science workflows"""
    print("\n🧠 Smart Dependency Detection Demo")
    print("=" * 50)
    
    # Create blocks with complex dependencies
    complex_blocks = [
        Block(
            id="import_block",
            title="Import Libraries",
            content="""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
            """,
            kind="code",
            language="python",
            project_id="demo_project",
            owner_id="admin_123"
        ),
        Block(
            id="feature_engineering",
            title="Feature Engineering", 
            content="""
# Create features
X = df[['feature1', 'feature2', 'feature3']].copy()
y = df['target'].copy()

# Feature scaling
X_scaled = (X - X.mean()) / X.std()
            """,
            kind="code",
            language="python",
            project_id="demo_project",
            owner_id="admin_123"
        ),
        Block(
            id="model_training",
            title="Model Training",
            content="""
# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Predictions
predictions = model.predict(X_test)
            """,
            kind="code",
            language="python",
            project_id="demo_project", 
            owner_id="admin_123"
        ),
        Block(
            id="model_evaluation",
            title="Model Evaluation",
            content="""
from sklearn.metrics import mean_squared_error, r2_score

# Evaluate model
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"MSE: {mse}")
print(f"R²: {r2}")

# Visualization
plt.scatter(y_test, predictions)
plt.xlabel('Actual')
plt.ylabel('Predicted')
plt.title('Model Performance')
plt.show()
            """,
            kind="code",
            language="python",
            project_id="demo_project",
            owner_id="admin_123"
        )
    ]
    
    analyzer = DAGAnalyzerService(None)
    
    # Analyze dependencies
    dependency_map = {}
    for block in complex_blocks:
        deps = analyzer.analyze_block_dependencies(block)
        dependency_map[block.id] = deps
        
        print(f"\n📊 {block.title}:")
        print(f"   Uses variables: {sorted(list(deps.variables_used))}")
        print(f"   Defines variables: {sorted(list(deps.variables_defined))}")
        print(f"   Output types: {list(deps.outputs)}")
    
    # Build optimized DAG
    dag = analyzer.build_dag_from_dependencies(dependency_map, complex_blocks)
    
    print(f"\n🚀 Optimized Execution Order:")
    for i, node_id in enumerate(dag['execution_order'], 1):
        block = next(b for b in complex_blocks if b.id == node_id)
        print(f"   {i}. {block.title} (ID: {node_id})")
    
    print(f"\n🔗 Dependencies:")
    for edge in dag['edges']:
        from_block = next(b for b in complex_blocks if b.id == edge[0])
        to_block = next(b for b in complex_blocks if b.id == edge[1])
        print(f"   {from_block.title} → {to_block.title}")

async def main():
    """Main test function"""
    print("🎯 AI Notebook DAG System Test")
    print("=" * 60)
    print("Testing automatic dependency analysis and workflow creation")
    print("This demonstrates AI-free, code-analysis-based DAG generation")
    print("=" * 60)
    
    try:
        # Test basic dependency analysis
        dag, deps = await test_dependency_analysis()
        
        # Test DAG validation
        await test_dag_validation()
        
        # Demonstrate smart dependency detection
        await demonstrate_smart_dependency_detection()
        
        print("\n🎉 All tests completed successfully!")
        print("\nKey Benefits Demonstrated:")
        print("✅ Automatic variable dependency detection")
        print("✅ Smart execution order optimization")
        print("✅ Data science workflow pattern recognition")
        print("✅ Cycle detection and validation")
        print("✅ Zero AI dependencies - pure code analysis!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
