from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.block import Block, BlockCreate, BlockUpdate, BlockKind, BlockLanguage, BlockExecutionRequest, BlockExecutionResult, BlockResponse
from app.services.block_service import BlockService
from app.services.python_executor_service import PythonExecutorService

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=BlockResponse)
async def create_block(
    block_data: BlockCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new block"""
    try:
        block_service = BlockService(db)
        
        # Validate block content
        validation = await block_service.validate_block_content(block_data)
        if not validation["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Block validation failed: {'; '.join(validation['errors'])}"
            )
        
        # Create block
        block = await block_service.create_block(block_data, current_user.id)
        
        return block
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create block", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create block"
        )

@router.get("/{block_id}", response_model=BlockResponse)
async def get_block(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a block by ID"""
    try:
        block_service = BlockService(db)
        block = await block_service.get_block(block_id, current_user.id)
        
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        return block
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get block", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get block"
        )

@router.get("/project/{project_id}", response_model=List[BlockResponse])
async def get_project_blocks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all blocks for a project"""
    try:
        block_service = BlockService(db)
        blocks = await block_service.get_project_blocks(project_id, current_user.id)
        
        return blocks
        
    except Exception as e:
        logger.error("Failed to get project blocks", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project blocks"
        )

@router.put("/{block_id}", response_model=BlockResponse)
async def update_block(
    block_id: str,
    block_update: BlockUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a block"""
    try:
        block_service = BlockService(db)
        
        # Validate update data if content is being updated
        if block_update.content is not None:
            # Get current block to create validation data
            current_block = await block_service.get_block(block_id, current_user.id)
            if current_block:
                validation_data = BlockCreate(
                    title=block_update.title or current_block.title,
                    kind=block_update.kind or current_block.kind,
                    language=block_update.language or current_block.language,
                    content=block_update.content,
                    project_id=current_block.project_id
                )
                
                validation = await block_service.validate_block_content(validation_data)
                if not validation["is_valid"]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Block validation failed: {'; '.join(validation['errors'])}"
                    )
        
        # Update block
        updated_block = await block_service.update_block(block_id, block_update, current_user.id)
        
        if not updated_block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        return updated_block
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update block", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update block"
        )

@router.delete("/{block_id}")
async def delete_block(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a block"""
    try:
        block_service = BlockService(db)
        success = await block_service.delete_block(block_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        return {"message": "Block deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete block", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete block"
        )

@router.post("/{block_id}/duplicate", response_model=BlockResponse)
async def duplicate_block(
    block_id: str,
    new_project_id: Optional[str] = Query(None, description="New project ID for the duplicate"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Duplicate a block"""
    try:
        block_service = BlockService(db)
        duplicate_block = await block_service.duplicate_block(block_id, current_user.id, new_project_id)
        
        if not duplicate_block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        return duplicate_block
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to duplicate block", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to duplicate block"
        )

@router.get("/project/{project_id}/kind/{kind}", response_model=List[BlockResponse])
async def get_blocks_by_kind(
    project_id: str,
    kind: BlockKind,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get blocks of a specific kind in a project"""
    try:
        block_service = BlockService(db)
        blocks = await block_service.get_block_by_kind(project_id, kind, current_user.id)
        
        return blocks
        
    except Exception as e:
        logger.error("Failed to get blocks by kind", error=str(e), project_id=project_id, kind=kind)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get blocks by kind"
        )

@router.get("/project/{project_id}/language/{language}", response_model=List[BlockResponse])
async def get_blocks_by_language(
    project_id: str,
    language: BlockLanguage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get blocks of a specific language in a project"""
    try:
        block_service = BlockService(db)
        blocks = await block_service.get_block_by_language(project_id, language, current_user.id)
        
        return blocks
        
    except Exception as e:
        logger.error("Failed to get blocks by language", error=str(e), project_id=project_id, language=language)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get blocks by language"
        )

@router.get("/project/{project_id}/search", response_model=List[BlockResponse])
async def search_blocks(
    project_id: str,
    query: str = Query(..., description="Search query for block content or title"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search blocks by content or title"""
    try:
        block_service = BlockService(db)
        blocks = await block_service.search_blocks(project_id, query, current_user.id)
        
        return blocks
        
    except Exception as e:
        logger.error("Failed to search blocks", error=str(e), project_id=project_id, query=query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search blocks"
        )

@router.get("/project/{project_id}/statistics")
async def get_block_statistics(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics about blocks in a project"""
    try:
        block_service = BlockService(db)
        statistics = await block_service.get_block_statistics(project_id, current_user.id)
        
        return statistics
        
    except Exception as e:
        logger.error("Failed to get block statistics", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get block statistics"
        )

@router.get("/{block_id}/lineage")
async def get_block_lineage(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get block lineage information (dependencies and dependents)"""
    try:
        block_service = BlockService(db)
        lineage = await block_service.get_block_lineage(block_id, current_user.id)
        
        if not lineage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        return lineage
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get block lineage", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get block lineage"
        )

@router.post("/{block_id}/validate")
async def validate_block_content(
    block_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Validate block content"""
    try:
        block_service = BlockService(db)
        
        # Get current block
        block = await block_service.get_block(block_id, current_user.id)
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        # Create validation data
        validation_data = BlockCreate(
            title=block.title,
            kind=block.kind,
            language=block.language,
            content=block.content,
            project_id=block.project_id
        )
        
        # Validate content
        validation = await block_service.validate_block_content(validation_data)
        
        return {
            "block_id": block_id,
            "validation": validation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to validate block content", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate block content"
        )

@router.post("/{block_id}/execute")
async def execute_block(
    block_id: str,
    execution_request: BlockExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute a code block"""
    try:
        block_service = BlockService(db)
        python_executor = PythonExecutorService()
        
        # Get block and verify ownership
        block = await block_service.get_block(block_id, current_user.id)
        if not block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Block not found"
            )
        
        # Check if block is executable
        if block.kind != BlockKind.CODE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only code blocks can be executed"
            )
        
        # Start execution session if not provided
        session_id = execution_request.session_id
        if not session_id:
            session_id = await python_executor.start_execution_session("python3")
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start Python execution session"
                )
        
        # Execute the code
        execution_result = await python_executor.execute_code(session_id, block.content, block_id)
        
        # Store execution result in block metadata
        await block_service.update_block_execution_result(block_id, execution_result, current_user.id)
        
        return execution_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to execute block", error=str(e), block_id=block_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute block"
        )

@router.post("/execute-multiple")
async def execute_multiple_blocks(
    execution_request: BlockExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute multiple blocks in sequence"""
    try:
        block_service = BlockService(db)
        python_executor = PythonExecutorService()
        
        results = []
        
        # Start execution session if not provided
        session_id = execution_request.session_id
        if not session_id:
            session_id = await python_executor.start_execution_session("python3")
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start Python execution session"
                )
        
        # Execute blocks in sequence
        for block_id in execution_request.block_ids:
            try:
                # Get block and verify ownership
                block = await block_service.get_block(block_id, current_user.id)
                if not block or block.kind != BlockKind.CODE:
                    results.append(BlockExecutionResult(
                        block_id=block_id,
                        status=block_id,
                        error="Block not found or not executable"
                    ))
                    continue
                
                # Execute the block
                execution_result = await python_executor.execute_code(session_id, block.content, block_id)
                results.append(execution_result)
                
                # Store execution result
                await block_service.update_block_execution_result(block_id, execution_result, current_user.id)
                
            except Exception as e:
                logger.error(f"Failed to execute block {block_id}", error=str(e))
                results.append(BlockExecutionResult(
                    block_id=block_id,
                    status=BlockStatus.FAILED,
                    error=str(e)
                ))
        
        return {
            "kernel_id": kernel_id,
            "results": results
        }
        
    except Exception as e:
        logger.error("Failed to execute multiple blocks", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute multiple blocks"
        )

@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user)
):
    """List active Python execution sessions"""
    try:
        python_executor = PythonExecutorService()
        sessions = await python_executor.list_active_sessions()
        return {"sessions": sessions}
        
    except Exception as e:
        logger.error("Failed to list sessions", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )

@router.post("/sessions/{session_id}/stop")
async def stop_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Stop a Python execution session"""
    try:
        python_executor = PythonExecutorService()
        success = await python_executor.stop_execution_session(session_id)
        
        if success:
            return {"message": f"Session {session_id} stopped successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to stop session"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to stop session", error=str(e), session_id=session_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop session"
        ) 