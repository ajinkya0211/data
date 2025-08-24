from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import structlog
import pandas as pd
import os
from datetime import datetime

from app.models.dataset import DatasetProfile
from app.services.dataset_service import DatasetService

logger = structlog.get_logger()

class ProfilerService:
    """Service for profiling datasets and extracting metadata"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.dataset_service = DatasetService(db)
    
    async def profile_dataset(self, dataset_id: str) -> Optional[DatasetProfile]:
        """Profile a dataset to extract schema and statistics"""
        try:
            # Use the dataset service to profile
            profile = await self.dataset_service.profile_dataset(dataset_id)
            
            if profile:
                logger.info("Dataset profiled successfully", dataset_id=dataset_id)
            else:
                logger.warning("Failed to profile dataset", dataset_id=dataset_id)
            
            return profile
            
        except Exception as e:
            logger.error("Failed to profile dataset", error=str(e), dataset_id=dataset_id)
            raise
    
    async def get_latest_profile(self, dataset_id: str) -> Optional[DatasetProfile]:
        """Get the latest profile for a dataset"""
        try:
            # Use the dataset service to get profile
            profile = await self.dataset_service.get_latest_profile(dataset_id)
            return profile
            
        except Exception as e:
            logger.error("Failed to get latest profile", error=str(e), dataset_id=dataset_id)
            raise
    
    async def profile_file_directly(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Profile a file directly without creating a dataset record"""
        try:
            if not os.path.exists(file_path):
                logger.warning("File not found for profiling", file_path=file_path)
                return None
            
            # Determine file type and read accordingly
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            else:
                logger.warning("Unsupported file format for profiling", file_path=file_path)
                return None
            
            # Generate comprehensive profile
            profile = {
                'file_info': {
                    'path': file_path,
                    'size_bytes': os.path.getsize(file_path),
                    'filename': os.path.basename(file_path),
                    'profiled_at': datetime.utcnow().isoformat()
                },
                'schema': {},
                'statistics': {
                    'total_rows': int(len(df)),
                    'total_columns': int(len(df.columns)),
                    'memory_usage_mb': float(df.memory_usage(deep=True).sum() / 1024 / 1024),
                    'duplicate_rows': int(df.duplicated().sum()),
                    'missing_values_percentage': float(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
                },
                'preview_data': df.head(5).to_dict('records'),
                'column_analysis': []
            }
            
            # Analyze each column
            for col in df.columns:
                col_data = df[col]
                col_analysis = {
                    'name': col,
                    'dtype': str(col_data.dtype),
                    'null_count': int(col_data.isnull().sum()),
                    'null_percentage': float(col_data.isnull().sum() / len(df) * 100),
                    'unique_count': int(col_data.nunique()),
                    'unique_percentage': float(col_data.nunique() / len(df) * 100)
                }
                
                # Add numeric-specific analysis
                if col_data.dtype in ['int64', 'float64']:
                    col_analysis.update({
                        'min_value': float(col_data.min()) if not col_data.isnull().all() else None,
                        'max_value': float(col_data.max()) if not col_data.isnull().all() else None,
                        'mean_value': float(col_data.mean()) if not col_data.isnull().all() else None,
                        'median_value': float(col_data.median()) if not col_data.isnull().all() else None,
                        'std_value': float(col_data.std()) if not col_data.isnull().all() else None
                    })
                
                # Add categorical-specific analysis
                if col_data.dtype == 'object' or col_data.nunique() < 50:
                    value_counts = col_data.value_counts()
                    col_analysis.update({
                        'top_values': value_counts.head(5).to_dict(),
                        'cardinality': 'low' if col_data.nunique() < 10 else 'medium' if col_data.nunique() < 50 else 'high'
                    })
                
                profile['column_analysis'].append(col_analysis)
                
                # Add to schema
                profile['schema'][col] = {
                    'dtype': str(col_data.dtype),
                    'null_count': col_analysis['null_count'],
                    'unique_count': col_analysis['unique_count'],
                    'min_value': col_analysis.get('min_value'),
                    'max_value': col_analysis.get('max_value'),
                    'mean_value': col_analysis.get('mean_value')
                }
            
            # Add data quality score
            profile['data_quality'] = self._calculate_data_quality_score(profile)
            
            logger.info("File profiled successfully", file_path=file_path)
            return profile
            
        except Exception as e:
            logger.error("Failed to profile file directly", error=str(e), file_path=file_path)
            raise
    
    def _calculate_data_quality_score(self, profile: Dict[str, Any]) -> float:
        """Calculate a data quality score from 0 to 100"""
        try:
            score = 100.0
            
            # Penalize for missing values
            missing_percentage = profile['statistics']['missing_values_percentage']
            if missing_percentage > 0:
                score -= min(missing_percentage * 2, 30)  # Max 30 point penalty
            
            # Penalize for duplicate rows
            duplicate_percentage = profile['statistics']['duplicate_rows'] / profile['statistics']['total_rows'] * 100
            if duplicate_percentage > 0:
                score -= min(duplicate_percentage * 2, 20)  # Max 20 point penalty
            
            # Penalize for low column variety
            low_variety_columns = sum(1 for col in profile['column_analysis'] if col.get('unique_percentage', 0) < 5)
            if low_variety_columns > 0:
                score -= min(low_variety_columns * 5, 25)  # Max 25 point penalty
            
            # Bonus for good structure
            if profile['statistics']['total_columns'] >= 5:
                score += 5
            if profile['statistics']['total_rows'] >= 1000:
                score += 5
            
            return max(0, min(100, score))
            
        except Exception as e:
            logger.warning("Failed to calculate data quality score", error=str(e))
            return 50.0  # Default score
    
    async def batch_profile_datasets(self, dataset_ids: list) -> Dict[str, Any]:
        """Profile multiple datasets in batch"""
        try:
            results = {
                'successful': [],
                'failed': [],
                'total': len(dataset_ids)
            }
            
            for dataset_id in dataset_ids:
                try:
                    profile = await self.profile_dataset(dataset_id)
                    if profile:
                        results['successful'].append({
                            'dataset_id': dataset_id,
                            'profile': profile
                        })
                    else:
                        results['failed'].append({
                            'dataset_id': dataset_id,
                            'error': 'Profile generation failed'
                        })
                except Exception as e:
                    results['failed'].append({
                        'dataset_id': dataset_id,
                        'error': str(e)
                    })
            
            logger.info("Batch profiling completed", 
                       successful=len(results['successful']), 
                       failed=len(results['failed']))
            
            return results
            
        except Exception as e:
            logger.error("Failed to batch profile datasets", error=str(e))
            raise
    
    async def get_profiling_summary(self) -> Dict[str, Any]:
        """Get a summary of profiling activities"""
        try:
            # This would typically query a profiling history table
            # For now, return a basic summary
            summary = {
                'total_datasets_profiled': 0,
                'last_profiling_activity': None,
                'profiling_success_rate': 0.0,
                'average_data_quality_score': 0.0
            }
            
            logger.info("Profiling summary retrieved")
            return summary
            
        except Exception as e:
            logger.error("Failed to get profiling summary", error=str(e))
            raise 