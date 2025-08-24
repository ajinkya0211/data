from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime
import json
import uuid

from app.models.block import Block, BlockCreate, BlockUpdate, BlockInDB, BlockKind, BlockLanguage, BlockExecutionResult
from app.models.user import User

logger = structlog.get_logger()

class BlockService:
    """Service for managing individual blocks with database persistence"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_block(self, block_data: BlockCreate, user_id: str) -> Block:
        """Create a new block in the database"""
        try:
            # Convert string values to enum values for SQLAlchemy
            from app.models.block import BlockKind, BlockLanguage, BlockStatus
            
            # Create block with required fields
            block = Block(
                id=str(uuid.uuid4()),
                title=block_data.title,
                kind=block_data.kind.lower() if block_data.kind else "code",
                language=block_data.language.lower() if block_data.language else "python",
                content=block_data.content,
                project_id=block_data.project_id,
                block_metadata=block_data.metadata or {},
                owner_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database
            self.db.add(block)
            await self.db.commit()
            await self.db.refresh(block)
            
            logger.info("Block created successfully in database", block_id=block.id, user_id=user_id)
            return block
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create block in database", error=str(e), user_id=user_id)
            raise
    
    async def get_block(self, block_id: str, user_id: str) -> Optional[Block]:
        """Get a block by ID from the database with access control"""
        try:
            # Query from database
            result = await self.db.execute(
                select(Block).where(Block.id == block_id)
            )
            block = result.scalar_one_or_none()
            
            # Check ownership
            if block and block.owner_id == user_id:
                return block
            
            return None
            
        except Exception as e:
            logger.error("Failed to get block from database", error=str(e), block_id=block_id)
            raise
    
    async def get_project_blocks(self, project_id: str, user_id: str) -> List[Block]:
        """Get all blocks for a project from the database"""
        try:
            # Query from database
            result = await self.db.execute(
                select(Block)
                .where(Block.project_id == project_id)
                .where(Block.owner_id == user_id)
                .order_by(Block.created_at)
            )
            blocks = result.scalars().all()
            
            return list(blocks)
            
        except Exception as e:
            logger.error("Failed to get project blocks from database", error=str(e), project_id=project_id)
            raise
    
    async def update_block(self, block_id: str, block_update: BlockUpdate, user_id: str) -> Optional[Block]:
        """Update a block in the database"""
        try:
            # Get block and verify ownership
            block = await self.get_block(block_id, user_id)
            if not block:
                return None
            
            # Update fields
            update_data = block_update.dict(exclude_unset=True)
            if update_data:
                # Handle string conversions
                if 'kind' in update_data and update_data['kind']:
                    update_data['kind'] = update_data['kind'].lower()
                
                if 'language' in update_data and update_data['language']:
                    update_data['language'] = update_data['language'].lower()
                
                # Update the block
                for field, value in update_data.items():
                    if hasattr(block, field):
                        setattr(block, field, value)
                
                # Update timestamp
                block.updated_at = datetime.utcnow()
                
                # Commit to database
                await self.db.commit()
                await self.db.refresh(block)
                
                logger.info("Block updated successfully in database", block_id=block_id, user_id=user_id)
            
            return block
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update block in database", error=str(e), block_id=block_id)
            raise
    
    async def delete_block(self, block_id: str, user_id: str) -> bool:
        """Delete a block from the database"""
        try:
            # Get block and verify ownership
            block = await self.get_block(block_id, user_id)
            if not block:
                return False
            
            # Delete from database
            await self.db.delete(block)
            await self.db.commit()
            
            logger.info("Block deleted successfully from database", block_id=block_id, user_id=user_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete block from database", error=str(e), block_id=block_id)
            raise
    
    async def update_block_execution_result(self, block_id: str, execution_result: BlockExecutionResult, user_id: str) -> bool:
        """Update block with execution result and outputs in the database"""
        try:
            # Get block and verify ownership
            block = await self.get_block(block_id, user_id)
            if not block:
                return False
            
            # Extract output content for user visibility
            output_content = ""
            if execution_result.outputs:
                for output in execution_result.outputs:
                    if hasattr(output, 'content'):
                        output_content += output.content + "\n"
                    else:
                        output_content += str(output) + "\n"
            
            # Update block status and outputs
            block.status = execution_result.status
            block.outputs = execution_result.outputs
            block.last_execution_output = output_content.strip() if output_content else None
            block.last_execution_error = execution_result.error
            block.execution_count = getattr(block, 'execution_count', 0) + 1
            block.updated_at = datetime.utcnow()
            
            # Update metadata
            block.block_metadata = {
                **block.block_metadata,
                "last_execution": {
                    "status": execution_result.status.value,
                    "execution_time_ms": execution_result.execution_time_ms,
                    "error": execution_result.error,
                    "executed_at": datetime.utcnow().isoformat(),
                    "outputs_count": len(execution_result.outputs)
                }
            }
            
            # Commit to database
            await self.db.commit()
            await self.db.refresh(block)
            
            logger.info("Block execution result updated in database with outputs", 
                       block_id=block_id, 
                       status=execution_result.status.value,
                       outputs_count=len(execution_result.outputs))
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update block execution result in database", error=str(e), block_id=block_id)
            return False
    
    async def validate_block_content(self, block_data: BlockCreate) -> Dict[str, Any]:
        """Validate block content and provide feedback"""
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Check content length
            if block_data.content and len(block_data.content) > 100000:  # 100KB limit
                validation_result["warnings"].append("Content is very long, consider splitting into multiple blocks")
            
            # Check for empty content
            if not block_data.content or block_data.content.strip() == "":
                validation_result["warnings"].append("Block content is empty")
            
            # Language-specific validation
            if block_data.language == BlockLanguage.PYTHON:
                # Basic Python syntax check
                try:
                    compile(block_data.content or "", "<string>", "exec")
                except SyntaxError as e:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Python syntax error: {str(e)}")
            
            elif block_data.language == BlockLanguage.SQL:
                # Basic SQL validation (very basic)
                sql_content = (block_data.content or "").upper()
                if "SELECT" in sql_content and "FROM" not in sql_content:
                    validation_result["warnings"].append("SQL query may be incomplete")
            
            # Kind-specific validation
            if block_data.kind == BlockKind.CODE and not block_data.language:
                validation_result["warnings"].append("Code blocks should specify a language")
            
            return validation_result
            
        except Exception as e:
            logger.error("Block validation failed", error=str(e))
            return {
                "is_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": []
            }
    
    async def get_block_lineage(self, block_id: str, user_id: str) -> Dict[str, Any]:
        """Get block lineage information (dependencies and dependents)"""
        try:
            # This would typically query the edges table
            # For now, return basic information
            block = await self.get_block(block_id, user_id)
            if not block:
                return {}
            
            return {
                "block_id": block_id,
                "title": block.title,
                "kind": block.kind.value if block.kind else None,
                "dependencies": [],  # Would come from edges table
                "dependents": [],    # Would come from edges table
                "created_at": block.created_at.isoformat(),
                "updated_at": block.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to get block lineage", error=str(e), block_id=block_id)
            raise 