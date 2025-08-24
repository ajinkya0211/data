"""
Database configuration and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from fastapi import HTTPException
import structlog
import asyncio

from app.core.config import settings

logger = structlog.get_logger()

# Convert PostgreSQL URL to async
def get_async_database_url():
    """Convert synchronous PostgreSQL URL to async"""
    if settings.DATABASE_URL.startswith("postgresql://"):
        return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    return settings.DATABASE_URL

# Create async engine
engine = create_async_engine(
    get_async_database_url(),
    echo=settings.DEBUG,
    pool_size=5,  # Reduce pool size to prevent exhaustion
    max_overflow=10,  # Reduce max overflow
    pool_pre_ping=True,
    pool_recycle=1800,  # Reduce recycle time to 30 minutes
    pool_timeout=20,  # 20 second timeout for getting connection from pool
    pool_reset_on_return='rollback',  # Rollback on return for better transaction management
    connect_args={
        "command_timeout": 30,  # Increase connection timeout
        "server_settings": {
            "statement_timeout": "30000",  # 30 second timeout for queries
            "idle_in_transaction_session_timeout": "30000"  # 30 second timeout for idle transactions
        }
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

async def get_db():
    """Dependency to get database session"""
    session = None
    try:
        session = AsyncSessionLocal()
        # Test connection health with timeout
        await asyncio.wait_for(
            session.execute(text("SELECT 1")),
            timeout=10.0
        )
        yield session
    except asyncio.TimeoutError:
        logger.error("Database connection timeout")
        if session:
            await session.close()
        raise HTTPException(
            status_code=500,
            detail="Database connection timeout"
        )
    except Exception as e:
        logger.error("Database session error", error=str(e))
        if session:
            try:
                await session.rollback()
            except:
                pass
            await session.close()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        if session:
            try:
                await session.close()
            except:
                pass

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models to ensure they are registered
            from app.models.user import User
            from app.models.project import Project
            from app.models.block import Block
            from app.models.dataset import DatasetModel, DatasetProfileModel
            from app.models.workflow import WorkflowDefinition, WorkflowExecution
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

async def close_db():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error("Failed to close database connections", error=str(e)) 