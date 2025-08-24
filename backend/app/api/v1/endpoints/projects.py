from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectInDB, 
    ProjectResponse, ProjectWithBlocks, ProjectPatch, ProjectExport
)
from app.services.project_service import ProjectService
from app.services.dag_service import DAGService

logger = structlog.get_logger()
router = APIRouter()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new project"""
    try:
        project_service = ProjectService(db)
        return await project_service.create_project(project, current_user.id)
    except Exception as e:
        logger.error("Failed to create project", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create project"
        )

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List user's projects"""
    try:
        project_service = ProjectService(db)
        return await project_service.list_user_projects(current_user.id, skip, limit)
    except Exception as e:
        logger.error("Failed to list projects", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list projects"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get project by ID"""
    try:
        project_service = ProjectService(db)
        project = await project_service.get_project(project_id, current_user.id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get project", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project"
        )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update project details"""
    try:
        project_service = ProjectService(db)
        project = await project_service.update_project(project_id, project_update, current_user.id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        return project
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update project", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update project"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete project"""
    try:
        project_service = ProjectService(db)
        success = await project_service.delete_project(project_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete project", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )

@router.post("/{project_id}/patch", response_model=ProjectWithBlocks)
async def apply_patch(
    project_id: str,
    patch: ProjectPatch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Apply a patch to the project (atomic operation)"""
    try:
        project_service = ProjectService(db)
        dag_service = DAGService(db)
        
        # Validate patch
        if not await dag_service.validate_patch(project_id, patch):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid patch - would create cycles or invalid state"
            )
        
        # Apply patch
        updated_project = await project_service.apply_patch(project_id, patch, current_user.id)
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to apply patch", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply patch"
        )

@router.post("/{project_id}/export")
async def export_project(
    project_id: str,
    export_config: ProjectExport,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export project in various formats"""
    try:
        project_service = ProjectService(db)
        export_data = await project_service.export_project(
            project_id, 
            export_config, 
            current_user.id
        )
        if not export_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Return appropriate response based on format
        if export_config.format == "ipynb":
            return {
                "format": "ipynb",
                "content": export_data,
                "filename": f"project_{project_id}.ipynb"
            }
        elif export_config.format == "html":
            return {
                "format": "html",
                "content": export_data,
                "filename": f"project_{project_id}.html"
            }
        else:
            return {
                "format": export_config.format,
                "content": export_data,
                "filename": f"project_{project_id}.{export_config.format}"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to export project", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export project"
        )

@router.get("/{project_id}/blocks")
async def get_project_blocks(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all blocks for a project"""
    try:
        from app.services.block_service import BlockService
        block_service = BlockService(db)
        blocks = await block_service.get_project_blocks(project_id, current_user.id)
        return blocks
    except Exception as e:
        logger.error("Failed to get project blocks", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project blocks"
        )

@router.get("/{project_id}/versions")
async def get_project_versions(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """Get project version history"""
    try:
        project_service = ProjectService(db)
        versions = await project_service.get_project_versions(
            project_id, 
            current_user.id, 
            skip, 
            limit
        )
        return versions
    except Exception as e:
        logger.error("Failed to get project versions", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get project versions"
        )

@router.post("/{project_id}/restore/{version_number}")
async def restore_project_version(
    project_id: str,
    version_number: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Restore project to a specific version"""
    try:
        project_service = ProjectService(db)
        restored_project = await project_service.restore_version(
            project_id, 
            version_number, 
            current_user.id
        )
        if not restored_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project or version not found"
            )
        return restored_project
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to restore project version", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restore project version"
        ) 