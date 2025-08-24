"""
AI Agent Service for Dynamic Notebook Control
This service provides agentic capabilities similar to Cursor AI for notebook management
"""

import asyncio
import json
import re
from typing import Dict, Any, List, Optional, Tuple
import structlog
from datetime import datetime
import uuid

from app.models.block import Block, BlockCreate, BlockUpdate, BlockKind, BlockLanguage, BlockStatus
from app.models.project import Project
from app.services.block_service import BlockService
from app.services.project_service import ProjectService
from app.services.python_executor_service import PythonExecutorService
from app.services.ai_provider_service import AIProviderService

logger = structlog.get_logger()

class AIAgentService:
    """AI Agent for dynamic notebook control and block management"""
    
    def __init__(self):
        self.block_service = None  # Will be set per request
        self.project_service = None  # Will be set per request
        self.python_executor = PythonExecutorService()
        self.ai_provider_service = AIProviderService()
        
    async def process_natural_language_request(
        self, 
        user_request: str, 
        project_id: str, 
        user_id: str,
        db_session
    ) -> Dict[str, Any]:
        """
        Process natural language request and execute appropriate actions
        Examples:
        - "import data from data_dirty.csv and clean it"
        - "add a block to calculate mean and median"
        - "delete the last block and recreate it"
        - "execute all blocks in sequence"
        """
        try:
            # Initialize services
            self.block_service = BlockService(db_session)
            self.project_service = ProjectService(db_session)
            
            # Parse the request
            parsed_request = await self._parse_request(user_request)
            
            # Execute the requested actions
            results = await self._execute_request(parsed_request, project_id, user_id)
            
            return {
                "success": True,
                "request": user_request,
                "parsed_actions": parsed_request,
                "results": results,
                "message": f"Successfully processed: {user_request}"
            }
            
        except Exception as e:
            logger.error("Failed to process AI agent request", error=str(e), request=user_request)
            return {
                "success": False,
                "request": user_request,
                "error": str(e),
                "message": f"Failed to process request: {str(e)}"
            }
    
    async def _parse_request(self, user_request: str) -> Dict[str, Any]:
        """Parse natural language request into structured actions"""
        request_lower = user_request.lower()
        
        actions = {
            "import_data": False,
            "clean_data": False,
            "add_blocks": [],
            "delete_blocks": [],
            "edit_blocks": [],
            "execute_blocks": False,
            "analyze_data": False,
            "visualize_data": False
        }
        
        # Detect import operations
        if any(keyword in request_lower for keyword in ["import", "load", "read", "open"]):
            actions["import_data"] = True
            # Extract dataset name
            dataset_match = re.search(r'from\s+(\w+\.\w+)', request_lower)
            if dataset_match:
                actions["dataset_name"] = dataset_match.group(1)
        
        # Detect cleaning operations
        if any(keyword in request_lower for keyword in ["clean", "preprocess", "handle missing", "remove duplicates"]):
            actions["clean_data"] = True
        
        # Detect analysis operations
        if any(keyword in request_lower for keyword in ["analyze", "calculate", "mean", "median", "statistics"]):
            actions["analyze_data"] = True
        
        # Detect visualization operations
        if any(keyword in request_lower for keyword in ["plot", "chart", "visualize", "graph"]):
            actions["visualize_data"] = True
        
        # Detect execution operations
        if any(keyword in request_lower for keyword in ["execute", "run", "execute all", "run all"]):
            actions["execute_blocks"] = True
        
        # Detect block management operations
        if "add" in request_lower and "block" in request_lower:
            actions["add_blocks"].append("new_block")
        
        if "delete" in request_lower and "block" in request_lower:
            actions["delete_blocks"].append("last_block")
        
        if "edit" in request_lower and "block" in request_lower:
            actions["edit_blocks"].append("modify_block")
        
        return actions
    
    async def _execute_request(self, parsed_request: Dict[str, Any], project_id: str, user_id: str) -> Dict[str, Any]:
        """Execute the parsed request actions"""
        results = {}
        
        try:
            # Get existing project and blocks
            project = await self.project_service.get_project(project_id, user_id)
            existing_blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            # Execute import operations
            if parsed_request.get("import_data"):
                import_result = await self._handle_data_import(
                    parsed_request.get("dataset_name", "data_dirty.csv"),
                    project_id, 
                    user_id
                )
                results["import"] = import_result
            
            # Execute cleaning operations
            if parsed_request.get("clean_data"):
                clean_result = await self._handle_data_cleaning(project_id, user_id)
                results["cleaning"] = clean_result
            
            # Execute analysis operations
            if parsed_request.get("analyze_data"):
                analysis_result = await self._handle_data_analysis(project_id, user_id)
                results["analysis"] = analysis_result
            
            # Execute visualization operations
            if parsed_request.get("visualize_data"):
                viz_result = await self._handle_data_visualization(project_id, user_id)
                results["visualization"] = viz_result
            
            # Execute block execution
            if parsed_request.get("execute_blocks"):
                execution_result = await self._execute_all_blocks(project_id, user_id)
                results["execution"] = execution_result
            
            # Execute block management operations
            if parsed_request.get("add_blocks"):
                for block_type in parsed_request["add_blocks"]:
                    add_result = await self._add_block(block_type, project_id, user_id)
                    results[f"add_{block_type}"] = add_result
            
            if parsed_request.get("delete_blocks"):
                for block_ref in parsed_request["delete_blocks"]:
                    delete_result = await self._delete_block(block_ref, project_id, user_id)
                    results[f"delete_{block_ref}"] = delete_result
            
            if parsed_request.get("edit_blocks"):
                for block_ref in parsed_request["edit_blocks"]:
                    edit_result = await self._edit_block(block_ref, project_id, user_id)
                    results[f"edit_{block_ref}"] = edit_result
            
            return results
            
        except Exception as e:
            logger.error("Failed to execute AI agent request", error=str(e))
            raise
    
    async def _handle_data_import(self, dataset_name: str, project_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data import operations"""
        try:
            # Create data loading block
            import_code = f'''# Import and Load Data
import pandas as pd
import numpy as np

try:
    # Load the dataset
    df = pd.read_csv('{dataset_name}')
    
    # Display basic information
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
    
    # Store dataset in memory for other blocks
    print("\\n✅ Dataset loaded successfully and ready for analysis!")
    
except FileNotFoundError:
    print(f"❌ Error: Could not find file '{dataset_name}'")
    print("Please ensure the file exists in the data directory.")
except Exception as e:
    print(f"❌ Error loading dataset: {str(e)}")
    print("Please check the file format and try again.")'''
            
            block_data = BlockCreate(
                title=f"Data Import - {dataset_name}",
                kind=BlockKind.CODE,
                language=BlockLanguage.PYTHON,
                content=import_code,
                project_id=project_id
            )
            
            block = await self.block_service.create_block(block_data, user_id)
            
            return {
                "action": "data_import",
                "block_created": block.id,
                "dataset": dataset_name,
                "message": f"Successfully created data import block for {dataset_name}"
            }
            
        except Exception as e:
            logger.error("Failed to handle data import", error=str(e))
            raise
    
    async def _handle_data_cleaning(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data cleaning operations"""
        try:
            # Create data cleaning block
            cleaning_code = '''# Data Cleaning and Preprocessing
print("=== DATA CLEANING PROCESS ===")

# Check for duplicates
print("\\n1. Checking for duplicates:")
duplicates = df.duplicated().sum()
print(f"Duplicate rows: {duplicates}")

if duplicates > 0:
    df_cleaned = df.drop_duplicates()
    print(f"Removed {duplicates} duplicate rows")
else:
    df_cleaned = df.copy()
    print("No duplicates found")

# Check for missing values
print("\\n2. Handling missing values:")
missing_before = df_cleaned.isnull().sum()
print("Missing values before cleaning:")
print(missing_before)

# Fill missing values appropriately
if missing_before.sum() > 0:
    # For numeric columns, fill with median
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df_cleaned[col].isnull().sum() > 0:
            median_val = df_cleaned[col].median()
            df_cleaned[col].fillna(median_val, inplace=True)
            print(f"Filled missing values in {col} with median: {median_val}")
    
    # For categorical columns, fill with mode
    categorical_cols = df_cleaned.select_dtypes(include=['object']).columns
    for col in categorical_cols:
        if df_cleaned[col].isnull().sum() > 0:
            mode_val = df_cleaned[col].mode()[0]
            df_cleaned[col].fillna(mode_val, inplace=True)
            print(f"Filled missing values in {col} with mode: {mode_val}")

# Final check
print("\\n3. Final dataset info:")
print(f"Cleaned dataset shape: {df_cleaned.shape}")
print("\\nMissing values after cleaning:")
print(df_cleaned.isnull().sum())

print("\\n4. Sample of cleaned data:")
print(df_cleaned.head())

# Save cleaned data
df_cleaned.to_csv('data_cleaned.csv', index=False)
print("\\n✅ Cleaned data saved to 'data_cleaned.csv'")'''
            
            block_data = BlockCreate(
                title="Data Cleaning and Preprocessing",
                kind=BlockKind.CODE,
                language=BlockLanguage.PYTHON,
                content=cleaning_code,
                project_id=project_id
            )
            
            block = await self.block_service.create_block(block_data, user_id)
            
            return {
                "action": "data_cleaning",
                "block_created": block.id,
                "message": "Successfully created data cleaning block"
            }
            
        except Exception as e:
            logger.error("Failed to handle data cleaning", error=str(e))
            raise
    
    async def _handle_data_analysis(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data analysis operations"""
        try:
            # Create data analysis block
            analysis_code = '''# Statistical Analysis
print("=== STATISTICAL ANALYSIS ===")

try:
    # Check if df_cleaned exists, if not, try to load or create it
    if 'df_cleaned' not in locals() and 'df_cleaned' not in globals():
        if 'df' in locals() or 'df' in globals():
            print("Using original dataset for analysis...")
            df_cleaned = df
        else:
            print("Loading data from data_dirty.csv...")
            import pandas as pd
            import numpy as np
            df_cleaned = pd.read_csv('data/data_dirty.csv')
            print("Data loaded successfully!")

    # Calculate basic statistics for numeric columns
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns
    print(f"\\nNumeric columns for analysis: {list(numeric_cols)}")

    print("\\n1. MEAN VALUES:")
    means = {}
    for col in numeric_cols:
        mean_val = df_cleaned[col].mean()
        means[col] = mean_val
        print(f"{col}: {mean_val:.4f}")

    print("\\n2. MEDIAN VALUES:")
    medians = {}
    for col in numeric_cols:
        median_val = df_cleaned[col].median()
        medians[col] = median_val
        print(f"{col}: {median_val:.4f}")

    print("\\n3. COMPARISON: Mean vs Median")
    print("Column          Mean        Median      Difference")
    print("-" * 50)
    for col in numeric_cols:
        diff = abs(means[col] - medians[col])
        print(f"{col:<15} {means[col]:<11.4f} {medians[col]:<11.4f} {diff:<11.4f}")

    print("\\n4. INTERPRETATION:")
    print("• If mean ≈ median: Data is roughly symmetric")
    print("• If mean > median: Data is right-skewed (positive skew)")
    print("• If mean < median: Data is left-skewed (negative skew)")

    # Calculate skewness for each numeric column
    print("\\n5. SKEWNESS ANALYSIS:")
    for col in numeric_cols:
        skewness = df_cleaned[col].skew()
        print(f"{col}: {skewness:.4f}")
        if abs(skewness) < 0.5:
            print("  → Roughly symmetric")
        elif skewness > 0.5:
            print("  → Right-skewed (positive skew)")
        else:
            print("  → Left-skewed (negative skew)")

    # Create summary DataFrame
    summary_stats = pd.DataFrame({
        'Column': numeric_cols,
        'Mean': [means[col] for col in numeric_cols],
        'Median': [medians[col] for col in numeric_cols],
        'Skewness': [df_cleaned[col].skew() for col in numeric_cols]
    })

    print("\\n6. SUMMARY STATISTICS TABLE:")
    print(summary_stats.to_string(index=False))

    # Save summary statistics
    summary_stats.to_csv('summary_statistics.csv', index=False)
    print("\\n✅ Summary statistics saved to 'summary_statistics.csv'")
    
except Exception as e:
    print(f"Error during statistical analysis: {str(e)}")
    print("Make sure the data is loaded and cleaned first.")'''
            
            block_data = BlockCreate(
                title="Statistical Analysis - Mean and Median",
                kind=BlockKind.CODE,
                language=BlockLanguage.PYTHON,
                content=analysis_code,
                project_id=project_id
            )
            
            block = await self.block_service.create_block(block_data, user_id)
            
            return {
                "action": "data_analysis",
                "block_created": block.id,
                "message": "Successfully created statistical analysis block"
            }
            
        except Exception as e:
            logger.error("Failed to handle data analysis", error=str(e))
            raise
    
    async def _handle_data_visualization(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Handle data visualization operations"""
        try:
            # Create visualization block
            viz_code = '''# Data Visualization
print("=== DATA VISUALIZATION ===")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Data Analysis Visualizations', fontsize=16, fontweight='bold')
    
    # 1. Price Distribution
    axes[0, 0].hist(df_cleaned['price'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 0].axvline(df_cleaned['price'].mean(), color='red', linestyle='--', label=f'Mean: ${df_cleaned["price"].mean():.2f}')
    axes[0, 0].axvline(df_cleaned['price'].median(), color='green', linestyle='--', label=f'Median: ${df_cleaned["price"].median():.2f}')
    axes[0, 0].set_title('Price Distribution')
    axes[0, 0].set_xlabel('Price ($)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Sales Distribution
    axes[0, 1].hist(df_cleaned['sales'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
    axes[0, 1].axvline(df_cleaned['sales'].mean(), color='red', linestyle='--', label=f'Mean: ${df_cleaned["sales"].mean():.2f}')
    axes[0, 1].axvline(df_cleaned['sales'].median(), color='green', linestyle='--', label=f'Median: ${df_cleaned["sales"].median():.2f}')
    axes[0, 1].set_title('Sales Distribution')
    axes[0, 1].set_xlabel('Sales ($)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Category Analysis
    category_counts = df_cleaned['category'].value_counts()
    axes[1, 0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', startangle=90)
    axes[1, 0].set_title('Product Categories Distribution')
    
    # 4. Rating Analysis
    rating_counts = df_cleaned['rating'].value_counts().sort_index()
    axes[1, 1].bar(rating_counts.index, rating_counts.values, color='gold', alpha=0.7, edgecolor='black')
    axes[1, 1].set_title('Product Ratings Distribution')
    axes[1, 1].set_xlabel('Rating')
    axes[1, 1].set_ylabel('Count')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('data_analysis_visualizations.png', dpi=300, bbox_inches='tight')
    print("✅ Visualizations saved to 'data_analysis_visualizations.png'")
    
    # Display the plot
    plt.show()
    
except ImportError:
    print("⚠️  Matplotlib/Seaborn not available. Skipping visualizations.")
    print("Install with: pip install matplotlib seaborn")
    
# Alternative: Text-based summary
print("\\n📊 TEXT-BASED SUMMARY:")
print("=" * 50)
print(f"Total Products: {len(df_cleaned)}")
print(f"Categories: {df_cleaned['category'].nunique()}")
print(f"Price Range: ${df_cleaned['price'].min():.2f} - ${df_cleaned['price'].max():.2f}")
print(f"Sales Range: ${df_cleaned['sales'].min():.2f} - ${df_cleaned['sales'].max():.2f}")
print(f"Average Rating: {df_cleaned['rating'].mean():.2f}")'''
            
            block_data = BlockCreate(
                title="Data Visualization and Insights",
                kind=BlockKind.CODE,
                language=BlockLanguage.PYTHON,
                content=viz_code,
                project_id=project_id
            )
            
            block = await self.block_service.create_block(block_data, user_id)
            
            return {
                "action": "data_visualization",
                "block_created": block.id,
                "message": "Successfully created data visualization block"
            }
            
        except Exception as e:
            logger.error("Failed to handle data visualization", error=str(e))
            raise
    
    async def _add_block(self, block_type: str, project_id: str, user_id: str) -> Dict[str, Any]:
        """Add a new block to the project"""
        try:
            # Generate block content based on type
            if block_type == "new_block":
                content = '''# New Analysis Block
print("=== NEW ANALYSIS BLOCK ===")
print("This is a new block created by the AI agent.")
print("You can modify this content as needed.")

# Add your analysis code here
# Example:
# result = some_analysis_function(df_cleaned)
# print(f"Analysis result: {result}")'''
                
                title = "New Analysis Block"
            else:
                content = f"# {block_type.replace('_', ' ').title()}\nprint('Block content here')"
                title = f"{block_type.replace('_', ' ').title()}"
            
            block_data = BlockCreate(
                title=title,
                kind=BlockKind.CODE,
                language=BlockLanguage.PYTHON,
                content=content,
                project_id=project_id
            )
            
            block = await self.block_service.create_block(block_data, user_id)
            
            return {
                "action": "add_block",
                "block_created": block.id,
                "block_type": block_type,
                "message": f"Successfully added {block_type} block"
            }
            
        except Exception as e:
            logger.error("Failed to add block", error=str(e))
            raise
    
    async def _delete_block(self, block_ref: str, project_id: str, user_id: str) -> Dict[str, Any]:
        """Delete a block from the project"""
        try:
            existing_blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            if not existing_blocks:
                return {
                    "action": "delete_block",
                    "success": False,
                    "message": "No blocks to delete"
                }
            
            # Handle different block references
            if block_ref == "last_block":
                block_to_delete = existing_blocks[-1]
            else:
                # Try to find block by title or ID
                block_to_delete = None
                for block in existing_blocks:
                    if block_ref.lower() in block.title.lower() or block_ref == block.id:
                        block_to_delete = block
                        break
            
            if block_to_delete:
                success = await self.block_service.delete_block(block_to_delete.id, user_id)
                return {
                    "action": "delete_block",
                    "success": success,
                    "block_deleted": block_to_delete.id,
                    "block_title": block_to_delete.title,
                    "message": f"Successfully deleted block: {block_to_delete.title}"
                }
            else:
                return {
                    "action": "delete_block",
                    "success": False,
                    "message": f"Could not find block matching: {block_ref}"
                }
                
        except Exception as e:
            logger.error("Failed to delete block", error=str(e))
            raise
    
    async def _edit_block(self, block_ref: str, project_id: str, user_id: str) -> Dict[str, Any]:
        """Edit an existing block"""
        try:
            existing_blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            if not existing_blocks:
                return {
                    "action": "edit_block",
                    "success": False,
                    "message": "No blocks to edit"
                }
            
            # Find the block to edit
            block_to_edit = None
            for block in existing_blocks:
                if block_ref.lower() in block.title.lower() or block_ref == block.id:
                    block_to_edit = block
                    break
            
            if block_to_edit:
                # Update the block content
                updated_content = f"""# {block_to_edit.title} (Edited by AI Agent)
print("=== {block_to_edit.title.upper()} ===")
print("This block has been edited by the AI agent.")

{block_to_edit.content}

# Additional AI-suggested improvements:
print("\\n🤖 AI Agent: I've enhanced this block with additional functionality!")
print("You can further customize it based on your needs.")"""
                
                update_data = BlockUpdate(content=updated_content)
                updated_block = await self.block_service.update_block(block_to_edit.id, update_data, user_id)
                
                return {
                    "action": "edit_block",
                    "success": True,
                    "block_edited": block_to_edit.id,
                    "block_title": block_to_edit.title,
                    "message": f"Successfully edited block: {block_to_edit.title}"
                }
            else:
                return {
                    "action": "edit_block",
                    "success": False,
                    "message": f"Could not find block matching: {block_ref}"
                }
                
        except Exception as e:
            logger.error("Failed to edit block", error=str(e))
            raise
    
    async def _execute_all_blocks(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Execute all blocks in the project"""
        try:
            # Ensure block service is initialized
            if not self.block_service:
                self.block_service = BlockService(None)
            
            existing_blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            if not existing_blocks:
                return {
                    "action": "execute_blocks",
                    "success": False,
                    "message": "No blocks to execute"
                }
            
            # Filter only code blocks
            code_blocks = [block for block in existing_blocks if block.kind == BlockKind.CODE]
            
            if not code_blocks:
                return {
                    "action": "execute_blocks",
                    "success": False,
                    "message": "No code blocks to execute"
                }
            
            # Start an execution session
            session_id = await self.python_executor.start_execution_session("python3")
            if not session_id:
                return {
                    "action": "execute_blocks",
                    "success": False,
                    "message": "Failed to start Python execution session"
                }
            
            execution_results = []
            
            # Execute blocks in sequence
            for block in code_blocks:
                try:
                    execution_result = await self.python_executor.execute_code(
                        session_id, 
                        block.content, 
                        block.id
                    )
                    
                    # Update block with execution result
                    await self.block_service.update_block_execution_result(
                        block.id, 
                        execution_result, 
                        user_id
                    )
                    
                    execution_results.append({
                        "block_id": block.id,
                        "block_title": block.title,
                        "status": execution_result.status.value,
                        "execution_time_ms": execution_result.execution_time_ms,
                        "error": execution_result.error,
                        "outputs_count": len(execution_result.outputs)
                    })
                    
                except Exception as e:
                    execution_results.append({
                        "block_id": block.id,
                        "block_title": block.title,
                        "status": "failed",
                        "error": str(e),
                        "outputs_count": 0
                    })
            
            # Stop the execution session
            await self.python_executor.stop_execution_session(session_id)
            
            return {
                "action": "execute_blocks",
                "success": True,
                "session_id": session_id,
                "blocks_executed": len(code_blocks),
                "execution_results": execution_results,
                "message": f"Successfully executed {len(code_blocks)} blocks"
            }
            
        except Exception as e:
            logger.error("Failed to execute blocks", error=str(e))
            raise
    
    async def get_notebook_summary(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get a comprehensive summary of the notebook"""
        try:
            # Ensure services are initialized
            if not self.project_service:
                self.project_service = ProjectService(None)
            if not self.block_service:
                self.block_service = BlockService(None)
            
            project = await self.project_service.get_project(project_id, user_id)
            if not project:
                return {
                    "error": "Project not found",
                    "project_id": project_id,
                    "user_id": user_id
                }
            
            blocks = await self.block_service.get_project_blocks(project_id, user_id)
            
            # Categorize blocks
            code_blocks = [b for b in blocks if b.kind == BlockKind.CODE]
            markdown_blocks = [b for b in blocks if b.kind == BlockKind.MARKDOWN]
            
            # Get execution status
            executed_blocks = [b for b in code_blocks if b.status != BlockStatus.IDLE]
            
            summary = {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "created_at": project.created_at.isoformat()
                },
                "blocks": {
                    "total": len(blocks),
                    "code": len(code_blocks),
                    "markdown": len(markdown_blocks),
                    "executed": len(executed_blocks),
                    "pending": len(code_blocks) - len(executed_blocks)
                },
                "execution_status": {
                    "completed": len([b for b in executed_blocks if b.status == BlockStatus.COMPLETED]),
                    "failed": len([b for b in executed_blocks if b.status == BlockStatus.FAILED]),
                    "running": len([b for b in executed_blocks if b.status == BlockStatus.RUNNING])
                },
                "block_details": [
                    {
                        "id": block.id,
                        "title": block.title,
                        "kind": block.kind.value,
                        "language": block.language.value if block.language else None,
                        "status": block.status.value,
                        "created_at": block.created_at.isoformat(),
                        "updated_at": block.updated_at.isoformat()
                    }
                    for block in blocks
                ]
            }
            
            return summary
            
        except Exception as e:
            logger.error("Failed to get notebook summary", error=str(e))
            return {
                "error": str(e),
                "project_id": project_id,
                "user_id": user_id
            } 