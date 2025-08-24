from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional, Dict, Any
import structlog
import pandas as pd
import os
from datetime import datetime
import json
from minio import Minio
from minio.error import S3Error

from app.models.dataset import DatasetModel, DatasetProfileModel, DatasetCreate, DatasetUpdate, DatasetInDB, DatasetProfile
from app.models.user import User
from app.core.config import settings

logger = structlog.get_logger()

class DatasetService:
    """Service for managing datasets and their profiles"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize MinIO client
        self.minio_client = Minio(
            "localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin123",
            secure=False
        )
        self.bucket_name = "notebook-artifacts"
    
    async def create_dataset(self, dataset_data: DatasetCreate, owner_id: str) -> DatasetModel:
        """Create a new dataset record"""
        try:
            import uuid
            
            dataset = DatasetModel(
                id=str(uuid.uuid4()),
                name=dataset_data.name,
                source_type=dataset_data.source_type,
                source_path=dataset_data.source_path,
                source_connection=dataset_data.source_connection,
                tags=dataset_data.tags,
                owner_id=owner_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Store in database instead of in-memory
            self.db.add(dataset)
            await self.db.commit()
            await self.db.refresh(dataset)
            
            logger.info("Dataset created successfully", dataset_id=dataset.id, owner_id=owner_id)
            return dataset
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to create dataset", error=str(e), owner_id=owner_id)
            raise
    
    async def create_dataset_from_upload(self, file, dataset_info: Dict[str, Any], owner_id: str) -> DatasetModel:
        """Create dataset from uploaded file"""
        try:
            # Generate unique filename
            import uuid
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Read file content
            content = await file.read()
            
            # Upload to MinIO
            try:
                import io
                file_stream = io.BytesIO(content)
                self.minio_client.put_object(
                    self.bucket_name,
                    f"datasets/{unique_filename}",
                    file_stream,
                    length=len(content),
                    content_type="application/octet-stream"
                )
                logger.info("File uploaded to MinIO", filename=unique_filename, size=len(content))
            except S3Error as e:
                logger.error("Failed to upload file to MinIO", error=str(e))
                raise Exception(f"Failed to upload file to storage: {e}")
            
            # Create dataset record with MinIO path
            dataset_data = DatasetCreate(
                name=dataset_info.get('name', file.filename),
                source_type='file',
                source_path=f"s3://{self.bucket_name}/datasets/{unique_filename}",
                tags=dataset_info.get('tags', []),
                source_connection={
                    'filename': file.filename,
                    'size_bytes': len(content),
                    'uploaded_at': datetime.utcnow().isoformat(),
                    'storage_path': f"datasets/{unique_filename}",
                    'bucket': self.bucket_name
                }
            )
            
            dataset = await self.create_dataset(dataset_data, owner_id)
            
            logger.info("Dataset created from upload", dataset_id=dataset.id, filename=unique_filename)
            return dataset
            
        except Exception as e:
            logger.error("Failed to create dataset from upload", error=str(e))
            raise
    
    async def get_dataset(self, dataset_id: str, user_id: str) -> Optional[DatasetModel]:
        """Get a dataset by ID with access control"""
        try:
            # Query database instead of in-memory storage
            query = select(DatasetModel).where(
                (DatasetModel.id == dataset_id) & 
                (DatasetModel.owner_id == user_id)
            )
            result = await self.db.execute(query)
            dataset = result.scalar_one_or_none()
            
            return dataset
            
        except Exception as e:
            logger.error("Failed to get dataset", error=str(e), dataset_id=dataset_id)
            raise
    
    async def list_datasets(self, user_id: str, skip: int = 0, limit: int = 100) -> List[DatasetModel]:
        """List all datasets owned by a user"""
        try:
            # Query database instead of in-memory storage
            query = select(DatasetModel).where(
                DatasetModel.owner_id == user_id
            ).order_by(DatasetModel.updated_at.desc()).offset(skip).limit(limit)
            
            result = await self.db.execute(query)
            datasets = result.scalars().all()
            
            return list(datasets)
            
        except Exception as e:
            logger.error("Failed to list datasets", error=str(e), user_id=user_id)
            raise
    
    async def search_datasets(self, search_params: Dict[str, Any], user_id: str) -> List[DatasetModel]:
        """Search datasets by various criteria"""
        try:
            query = select(DatasetModel).where(DatasetModel.owner_id == user_id)
            
            # Add search filters
            if search_params.get('query'):
                search_term = f"%{search_params['query']}%"
                query = query.where(
                    (DatasetModel.name.ilike(search_term)) |
                    (DatasetModel.description.ilike(search_term))
                )
            
            if search_params.get('source_type'):
                query = query.where(DatasetModel.source_type == search_params['source_type'])
            
            if search_params.get('tags'):
                # Simple tag search - in a full implementation, this would be more sophisticated
                for tag in search_params['tags']:
                    query = query.where(DatasetModel.tags.contains([tag]))
            
            # Apply pagination
            query = query.offset(search_params.get('offset', 0)).limit(search_params.get('limit', 50))
            
            result = await self.db.execute(query)
            datasets = result.scalars().all()
            
            return list(datasets)
            
        except Exception as e:
            logger.error("Failed to search datasets", error=str(e), user_id=user_id)
            raise
    
    async def update_dataset(self, dataset_id: str, dataset_update: DatasetUpdate, user_id: str) -> Optional[DatasetModel]:
        """Update dataset metadata"""
        try:
            # Get dataset and verify ownership
            dataset = await self.get_dataset(dataset_id, user_id)
            if not dataset:
                return None
            
            # Update fields
            update_data = dataset_update.dict(exclude_unset=True)
            if update_data:
                # Add updated_at timestamp
                update_data['updated_at'] = datetime.utcnow()
                
                query = update(DatasetModel).where(
                    DatasetModel.id == dataset_id
                ).values(**update_data)
                
                await self.db.execute(query)
                await self.db.commit()
                
                # Get updated dataset
                updated_dataset = await self.get_dataset(dataset_id, user_id)
                logger.info("Dataset updated successfully", dataset_id=dataset_id)
                return updated_dataset
            
            return dataset
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to update dataset", error=str(e), dataset_id=dataset_id)
            raise
    
    async def delete_dataset(self, dataset_id: str, user_id: str) -> bool:
        """Delete a dataset and its files"""
        try:
            # Get dataset and verify ownership
            dataset = await self.get_dataset(dataset_id, user_id)
            if not dataset:
                return False
            
            # Delete file from MinIO if it exists
            if dataset.source_type == 'file' and dataset.source_connection and 'storage_path' in dataset.source_connection:
                try:
                    storage_path = dataset.source_connection['storage_path']
                    self.minio_client.remove_object(self.bucket_name, storage_path)
                    logger.info("Dataset file deleted from MinIO", storage_path=storage_path)
                except S3Error as e:
                    logger.warning("Failed to delete file from MinIO", error=str(e), storage_path=storage_path)
                    # Continue with deletion even if file removal fails
            
            # Delete dataset record from database
            query = delete(DatasetModel).where(DatasetModel.id == dataset_id)
            await self.db.execute(query)
            await self.db.commit()
            
            logger.info("Dataset deleted successfully", dataset_id=dataset_id)
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to delete dataset", error=str(e), dataset_id=dataset_id)
            raise
    
    async def get_dataset_preview(self, dataset_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset preview with sample data and schema"""
        try:
            dataset = await self.get_dataset(dataset_id, user_id)
            if not dataset:
                return None
            
            # For now, return basic preview
            # In a full implementation, this would include actual data profiling
            preview = {
                'dataset': dataset,
                'profile': None,
                'sample_rows': [],
                'column_info': []
            }
            
            # Try to read sample data if it's a file
            if dataset.source_type == 'file' and os.path.exists(dataset.source_path):
                try:
                    if dataset.source_path.endswith('.csv'):
                        df = pd.read_csv(dataset.source_path, nrows=5)
                        preview['sample_rows'] = df.to_dict('records')
                        preview['column_info'] = [
                            {
                                'name': col,
                                'dtype': str(dtype),
                                'null_count': df[col].isnull().sum(),
                                'unique_count': df[col].nunique(),
                                'sample_values': df[col].dropna().unique()[:3].tolist()
                            }
                            for col, dtype in df.dtypes.items()
                        ]
                except Exception as e:
                    logger.warning("Failed to read dataset file for preview", error=str(e))
            
            return preview
            
        except Exception as e:
            logger.error("Failed to get dataset preview", error=str(e), dataset_id=dataset_id)
            raise
    
    async def get_download_info(self, dataset_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get download information for a dataset"""
        try:
            dataset = await self.get_dataset(dataset_id, user_id)
            if not dataset:
                return None
            
            if dataset.source_type == 'file' and os.path.exists(dataset.source_path):
                file_size = os.path.getsize(dataset.source_path)
                return {
                    'download_url': f"/api/v1/datasets/{dataset_id}/download",
                    'filename': os.path.basename(dataset.source_path),
                    'size_bytes': file_size
                }
            
            return None
            
        except Exception as e:
            logger.error("Failed to get download info", error=str(e), dataset_id=dataset_id)
            raise
    
    async def profile_dataset(self, dataset_id: str) -> Optional[DatasetProfileModel]:
        """Profile a dataset to extract schema and statistics"""
        try:
            # Get dataset from database
            query = select(DatasetModel).where(DatasetModel.id == dataset_id)
            result = await self.db.execute(query)
            dataset = result.scalar_one_or_none()
            
            if not dataset:
                logger.warning("Dataset not found", dataset_id=dataset_id)
                return None
            
            if dataset.source_type != 'file':
                logger.warning("Cannot profile dataset - not a file dataset", dataset_id=dataset_id)
                return None
            
            # Read dataset from MinIO
            try:
                # Extract storage path from source_connection or source_path
                if dataset.source_connection and 'storage_path' in dataset.source_connection:
                    storage_path = dataset.source_connection['storage_path']
                else:
                    # Fallback: try to extract from source_path
                    if dataset.source_path.startswith('s3://'):
                        # Remove s3://bucket/ prefix but keep the full path structure
                        path_parts = dataset.source_path.split('/', 3)
                        if len(path_parts) >= 4:
                            storage_path = '/'.join(path_parts[3:])  # Keep everything after bucket name
                        else:
                            storage_path = path_parts[-1]  # Fallback to last part
                    else:
                        storage_path = dataset.source_path
                
                # Download file from MinIO
                response = self.minio_client.get_object(self.bucket_name, storage_path)
                file_content = response.read()
                response.close()
                response.release_conn()
                
                logger.info("File downloaded from MinIO", storage_path=storage_path, size=len(file_content))
                
            except S3Error as e:
                logger.error("Failed to download file from MinIO", error=str(e), storage_path=storage_path)
                raise Exception(f"Failed to download file from storage: {e}")
            
            # Read dataset with pandas based on file extension
            file_extension = os.path.splitext(storage_path)[1].lower()
            
            if file_extension == '.csv':
                import io
                df = pd.read_csv(io.BytesIO(file_content))
            elif file_extension == '.parquet':
                import io
                df = pd.read_parquet(io.BytesIO(file_content))
            elif file_extension == '.json':
                import io
                df = pd.read_json(io.BytesIO(file_content))
            else:
                logger.warning("Unsupported file format for profiling", dataset_id=dataset_id, extension=file_extension)
                return None
            
            # Generate schema
            schema = {}
            for col in df.columns:
                schema[col] = {
                    'dtype': str(df[col].dtype),
                    'null_count': int(df[col].isnull().sum()),
                    'unique_count': int(df[col].nunique()),
                    'min_value': float(df[col].min()) if df[col].dtype in ['int64', 'float64'] else None,
                    'max_value': float(df[col].max()) if df[col].dtype in ['int64', 'float64'] else None,
                    'mean_value': float(df[col].mean()) if df[col].dtype in ['int64', 'float64'] else None
                }
            
            # Generate statistics
            statistics = {
                'total_rows': int(len(df)),
                'total_columns': int(len(df.columns)),
                'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024 / 1024),
                'duplicate_rows': int(df.duplicated().sum()),
                'missing_values_percentage': float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            }
            
            # Create profile and store in database
            import uuid
            profile = DatasetProfileModel(
                id=str(uuid.uuid4()),
                dataset_id=dataset_id,
                schema=schema,
                row_count_estimate=statistics['total_rows'],
                preview_data=df.head(5).to_dict('records'),
                statistics=statistics,
                created_at=datetime.utcnow()
            )
            
            # Store profile in database
            self.db.add(profile)
            
            # Update dataset with profiling timestamp
            query = update(DatasetModel).where(
                DatasetModel.id == dataset_id
            ).values(last_profiled_at=datetime.utcnow())
            
            await self.db.execute(query)
            await self.db.commit()
            
            logger.info("Dataset profiled successfully", dataset_id=dataset_id)
            return profile
            
        except Exception as e:
            await self.db.rollback()
            logger.error("Failed to profile dataset", error=str(e), dataset_id=dataset_id)
            raise
    
    async def get_latest_profile(self, dataset_id: str) -> Optional[DatasetProfileModel]:
        """Get the latest profile for a dataset"""
        try:
            # Query database for the latest profile
            query = select(DatasetProfileModel).where(
                DatasetProfileModel.dataset_id == dataset_id
            ).order_by(DatasetProfileModel.created_at.desc()).limit(1)
            
            result = await self.db.execute(query)
            profile = result.scalar_one_or_none()
            
            if profile:
                logger.info("Latest profile retrieved", dataset_id=dataset_id, profile_id=profile.id)
            else:
                logger.info("No profile found for dataset", dataset_id=dataset_id)
            
            return profile
            
        except Exception as e:
            logger.error("Failed to get latest profile", error=str(e), dataset_id=dataset_id)
            raise 