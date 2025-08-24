from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import structlog
from datetime import datetime
import json
import uuid

from app.models.project import Project, ProjectCreate, ProjectUpdate, ProjectInDB, ProjectWithBlocks
from app.models.block import Block, BlockCreate, BlockUpdate
from app.models.edge import Edge, EdgeCreate
from app.models.user import User
from app.core.database import AsyncSessionLocal

logger = structlog.get_logger()

class ProjectService:
    """Service for managing projects and their DAGs"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_project(self, project_data: ProjectCreate, owner_id: str) -> Project:
        """Create a new project"""
        try:
            # Create project with required fields
            from datetime import datetime
            import uuid
            
            project = Project(
                id=str(uuid.uuid4()),
                name=project_data.name,
                description=project_data.description,
                owner_id=owner_id,
                is_public=project_data.is_public,
                project_metadata=project_data.metadata,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database
            self.db.add(project)
            await self.db.commit()
            await self.db.refresh(project)
            
            logger.info("Project created successfully", project_id=project.id, owner_id=owner_id)
            return project
            
        except Exception as e:
            logger.error("Failed to create project", error=str(e), owner_id=owner_id)
            raise
    
    async def get_project(self, project_id: str, user_id: str) -> Optional[Project]:
        """Get a project by ID with access control"""
        try:
            from sqlalchemy import select
            
            # Query database for project
            stmt = select(Project).where(Project.id == project_id)
            result = await self.db.execute(stmt)
            project = result.scalar_one_or_none()
            
            # Check if user owns the project or has access
            if project and project.owner_id == user_id:
                return project
            
            return None
            
        except Exception as e:
            logger.error("Failed to get project", error=str(e), project_id=project_id)
            raise
    
    async def get_project_with_blocks(self, project_id: str, user_id: str) -> Optional[ProjectWithBlocks]:
        """Get project with all blocks and edges"""
        try:
            # Get project and verify ownership
            project = await self.get_project(project_id, user_id)
            if not project:
                return None
            
            # Convert to ProjectWithBlocks (for now, with empty blocks and edges)
            project_with_blocks = ProjectWithBlocks(
                **project.dict(),
                blocks=[],
                edges=[]
            )
            
            return project_with_blocks
            
        except Exception as e:
            logger.error("Failed to get project with blocks", error=str(e), project_id=project_id)
            raise
    
    async def list_user_projects(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Project]:
        """List all projects owned by a user"""
        try:
            from sqlalchemy import select
            
            # Query database for user projects
            stmt = select(Project).where(Project.owner_id == user_id).order_by(Project.updated_at.desc())
            result = await self.db.execute(stmt)
            projects = result.scalars().all()
            
            # Apply pagination
            return projects[skip:skip + limit]
            
        except Exception as e:
            logger.error("Failed to list user projects", error=str(e), user_id=user_id)
            raise
    
    async def update_project(self, project_id: str, project_update: ProjectUpdate, user_id: str) -> Optional[Project]:
        """Update project details"""
        try:
            # Get project and verify ownership
            project = await self.get_project(project_id, user_id)
            if not project:
                return None
            
            # Update fields
            update_data = project_update.dict(exclude_unset=True)
            if update_data:
                for field, value in update_data.items():
                    setattr(project, field, value)
                project.updated_at = datetime.utcnow()
                
                            # Update in database
                await self.db.commit()
                await self.db.refresh(project)
                
                logger.info("Project updated successfully", project_id=project_id)
                return project
            
            return project
            
        except Exception as e:
            logger.error("Failed to update project", error=str(e), project_id=project_id)
            raise
    
    async def delete_project(self, project_id: str, user_id: str) -> bool:
        """Delete a project and all its blocks/edges"""
        try:
            # Get project and verify ownership
            project = await self.get_project(project_id, user_id)
            if not project:
                return False
            
            # Delete project from database
            await self.db.delete(project)
            await self.db.commit()
            
            logger.info("Project deleted successfully", project_id=project_id)
            return True
            
        except Exception as e:
            logger.error("Failed to delete project", error=str(e), project_id=project_id)
            raise
    
    async def apply_patch(self, project_id: str, patch_data: Dict[str, Any], user_id: str) -> Optional[ProjectWithBlocks]:
        """Apply a patch to the project (atomic operation)"""
        try:
            # Get current project
            project = await self.get_project_with_blocks(project_id, user_id)
            if not project:
                return None
            
            # Apply patch operations
            operations = patch_data.get('operations', [])
            
            for operation in operations:
                op_type = operation.get('op')
                path = operation.get('path')
                value = operation.get('value')
                
                if op_type == 'add' and path.startswith('/blocks'):
                    # Add new block
                    block_data = BlockCreate(**value, project_id=project_id)
                    await self._add_block(block_data)
                    
                elif op_type == 'update' and path.startswith('/blocks'):
                    # Update existing block
                    block_id = path.split('/')[-1]
                    block_update = BlockUpdate(**value)
                    await self._update_block(block_id, block_update)
                    
                elif op_type == 'delete' and path.startswith('/blocks'):
                    # Delete block
                    block_id = path.split('/')[-1]
                    await self._delete_block(block_id)
                    
                elif op_type == 'link' and path.startswith('/edges'):
                    # Add edge between blocks
                    edge_data = EdgeCreate(**value, project_id=project_id)
                    await self._add_edge(edge_data)
                    
                elif op_type == 'unlink' and path.startswith('/edges'):
                    # Remove edge
                    edge_id = path.split('/')[-1]
                    await self._delete_edge(edge_id)
            
            # Increment project version
            await self._increment_version(project_id)
            
            # Get updated project
            updated_project = await self.get_project_with_blocks(project_id, user_id)
            
            logger.info("Patch applied successfully", project_id=project_id, operations_count=len(operations))
            return updated_project
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to apply patch", error=str(e), project_id=project_id)
            raise
    
    async def export_project(self, project_id: str, export_config: Dict[str, Any], user_id: str) -> Optional[str]:
        """Export project in various formats"""
        try:
            # Get project with blocks
            project = await self.get_project_with_blocks(project_id, user_id)
            if not project:
                return None
            
            export_format = export_config.get('format', 'ipynb')
            
            if export_format == 'ipynb':
                return await self._export_to_notebook(project)
            elif export_format == 'html':
                return await self._export_to_html(project)
            elif export_format == 'script':
                return await self._export_to_script(project)
            else:
                raise ValueError(f"Unsupported export format: {export_format}")
                
        except Exception as e:
            logger.error("Failed to export project", error=str(e), project_id=project_id)
            raise
    
    async def get_project_versions(self, project_id: str, user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get project version history"""
        try:
            # For now, return basic version info
            # In a full implementation, this would query a versions table
            project = await self.get_project(project_id, user_id)
            if not project:
                return []
            
            return [{
                'version': project.version,
                'created_at': project.updated_at,
                'description': f'Version {project.version}'
            }]
            
        except Exception as e:
            logger.error("Failed to get project versions", error=str(e), project_id=project_id)
            raise
    
    async def restore_version(self, project_id: str, version_number: int, user_id: str) -> Optional[ProjectWithBlocks]:
        """Restore project to a specific version"""
        try:
            # For now, this is a placeholder
            # In a full implementation, this would restore from a versions table
            logger.info("Version restoration not yet implemented", project_id=project_id, version=version_number)
            return await self.get_project_with_blocks(project_id, user_id)
            
        except Exception as e:
            logger.error("Failed to restore version", error=str(e), project_id=project_id)
            raise
    
    # Helper methods for patch operations
    async def _add_block(self, block_data: BlockCreate) -> Block:
        """Add a new block to the project"""
        block = Block(**block_data.dict())
        self.db.add(block)
        await self.db.commit()
        await self.db.refresh(block)
        return block
    
    async def _update_block(self, block_id: str, block_update: BlockUpdate) -> bool:
        """Update an existing block"""
        update_data = block_update.dict(exclude_unset=True)
        if update_data:
            query = update(Block).where(Block.id == block_id).values(**update_data)
            await self.db.execute(query)
            await self.db.commit()
            return True
        return False
    
    async def _delete_block(self, block_id: str) -> bool:
        """Delete a block"""
        query = delete(Block).where(Block.id == block_id)
        await self.db.execute(query)
        await self.db.commit()
        return True
    
    async def _add_edge(self, edge_data: EdgeCreate) -> Edge:
        """Add a new edge between blocks"""
        edge = Edge(**edge_data.dict())
        self.db.add(edge)
        await self.db.commit()
        await self.db.refresh(edge)
        return edge
    
    async def _delete_edge(self, edge_id: str) -> bool:
        """Delete an edge"""
        query = delete(Edge).where(Edge.id == edge_id)
        await self.db.execute(query)
        await self.db.commit()
        return True
    
    async def _increment_version(self, project_id: str) -> None:
        """Increment project version number"""
        query = update(Project).where(Project.id == project_id).values(
            version=Project.version + 1
        )
        await self.db.execute(query)
        await self.db.commit()
    
    # Export methods
    async def _export_to_notebook(self, project: ProjectWithBlocks) -> str:
        """Export project to Jupyter notebook format"""
        notebook = {
            "cells": [],
            "metadata": {
                "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                "language_info": {"codemirror_mode": {"name": "ipython", "version": 3}, "file_extension": ".py", "mimetype": "text/x-python", "name": "python", "nbconvert_exporter": "python", "pygments_lexer": "ipython3", "version": "3.8.0"}
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Add project description
        if project.description:
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {project.name}\n\n{project.description}"]
            })
        
        # Add blocks as cells
        for block in project.blocks:
            if block.kind == 'code':
                notebook["cells"].append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [block.content or ""]
                })
            elif block.kind == 'markdown':
                notebook["cells"].append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [block.content or ""]
                })
        
        return json.dumps(notebook, indent=2)
    
    async def _export_to_html(self, project: ProjectWithBlocks) -> str:
        """Export project to HTML format"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{project.name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .block {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .code {{ background: #f5f5f5; padding: 10px; border-radius: 3px; font-family: monospace; }}
                .markdown {{ line-height: 1.6; }}
            </style>
        </head>
        <body>
            <h1>{project.name}</h1>
            {f'<p>{project.description}</p>' if project.description else ''}
        """
        
        for block in project.blocks:
            if block.kind == 'code':
                html += f"""
                <div class="block">
                    <h3>Code Block: {block.title or 'Untitled'}</h3>
                    <div class="code">{block.content or ''}</div>
                </div>
                """
            elif block.kind == 'markdown':
                html += f"""
                <div class="block">
                    <div class="markdown">{block.content or ''}</div>
                </div>
                """
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def _export_to_script(self, project: ProjectWithBlocks) -> str:
        """Export project to Python script format"""
        script = f"""# {project.name}
{f'# {project.description}' if project.description else ''}

"""
        
        for block in project.blocks:
            if block.kind == 'code':
                script += f"# {block.title or 'Code Block'}\n"
                script += f"{block.content or ''}\n\n"
        
        return script 