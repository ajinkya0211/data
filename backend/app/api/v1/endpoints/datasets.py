from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import structlog

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.models.dataset import (
    Dataset, DatasetCreate, DatasetUpdate, DatasetInDB, 
    DatasetProfile, DatasetPreview, DatasetSearch, DatasetUpload
)
from app.services.dataset_service import DatasetService
from app.services.profiler_service import ProfilerService

logger = structlog.get_logger()
router = APIRouter()

@router.post("/upload", response_model=Dataset, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_info: DatasetUpload = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and register a new dataset"""
    try:
        dataset_service = DatasetService(db)
        profiler_service = ProfilerService(db)
        
        # Validate file type
        if not any(file.filename.endswith(ext) for ext in ['.csv', '.parquet', '.json', '.xlsx']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Supported: .csv, .parquet, .json, .xlsx"
            )
        
        # Create dataset record
        dataset = await dataset_service.create_dataset_from_upload(
            file, dataset_info, current_user.id
        )
        
        # Auto-profile if requested
        if dataset_info.auto_profile:
            await profiler_service.profile_dataset(dataset.id)
        
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to upload dataset", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload dataset"
        )

@router.post("/register", response_model=Dataset, status_code=status.HTTP_201_CREATED)
async def register_dataset(
    dataset: DatasetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Register an existing dataset (file, SQL, S3, API)"""
    try:
        dataset_service = DatasetService(db)
        return await dataset_service.create_dataset(dataset, current_user.id)
    except Exception as e:
        logger.error("Failed to register dataset", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register dataset"
        )

@router.get("/", response_model=List[Dataset])
async def list_datasets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """List available datasets"""
    try:
        dataset_service = DatasetService(db)
        return await dataset_service.list_datasets(current_user.id, skip, limit)
    except Exception as e:
        logger.error("Failed to list datasets", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list datasets"
        )

@router.post("/search", response_model=List[Dataset])
async def search_datasets(
    search_params: DatasetSearch,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search datasets by various criteria"""
    try:
        dataset_service = DatasetService(db)
        return await dataset_service.search_datasets(search_params, current_user.id)
    except Exception as e:
        logger.error("Failed to search datasets", error=str(e), user_id=current_user.id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search datasets"
        )

@router.get("/{dataset_id}", response_model=Dataset)
async def get_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dataset details"""
    try:
        dataset_service = DatasetService(db)
        dataset = await dataset_service.get_dataset(dataset_id, current_user.id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get dataset", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dataset"
        )

@router.get("/{dataset_id}/preview", response_model=DatasetPreview)
async def get_dataset_preview(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get dataset preview with sample data and schema"""
    try:
        dataset_service = DatasetService(db)
        preview = await dataset_service.get_dataset_preview(dataset_id, current_user.id)
        if not preview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        return preview
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get dataset preview", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dataset preview"
        )

@router.post("/{dataset_id}/profile", response_model=DatasetProfile)
async def profile_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Profile dataset to extract schema and statistics"""
    try:
        profiler_service = ProfilerService(db)
        profile = await profiler_service.profile_dataset(dataset_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to profile dataset", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to profile dataset"
        )

@router.get("/{dataset_id}/profile", response_model=DatasetProfile)
async def get_dataset_profile(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get latest dataset profile"""
    try:
        profiler_service = ProfilerService(db)
        profile = await profiler_service.get_latest_profile(dataset_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset profile not found"
            )
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get dataset profile", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dataset profile"
        )

@router.put("/{dataset_id}", response_model=Dataset)
async def update_dataset(
    dataset_id: str,
    dataset_update: DatasetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update dataset metadata"""
    try:
        dataset_service = DatasetService(db)
        dataset = await dataset_service.update_dataset(dataset_id, dataset_update, current_user.id)
        if not dataset:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        return dataset
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update dataset", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update dataset"
        )

@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete dataset"""
    try:
        dataset_service = DatasetService(db)
        success = await dataset_service.delete_dataset(dataset_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete dataset", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete dataset"
        )

@router.get("/{dataset_id}/download")
async def download_dataset(
    dataset_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download dataset file"""
    try:
        dataset_service = DatasetService(db)
        file_info = await dataset_service.get_download_info(dataset_id, current_user.id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found"
            )
        
        # Return file download response
        # This would typically stream the file from storage
        return {
            "download_url": file_info["download_url"],
            "filename": file_info["filename"],
            "size_bytes": file_info["size_bytes"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get download info", error=str(e), dataset_id=dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get download info"
        ) 