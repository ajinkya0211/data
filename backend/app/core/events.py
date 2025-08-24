import structlog
from fastapi import FastAPI
from app.core.database import init_db, close_db

logger = structlog.get_logger()

def create_start_app_handler(app: FastAPI):
    """Create startup event handler"""
    async def start_app() -> None:
        logger.info("Starting AI Notebook System")
        try:
            # Initialize database
            await init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
            raise
    
    return start_app

def create_stop_app_handler(app: FastAPI):
    """Create shutdown event handler"""
    async def stop_app() -> None:
        logger.info("Shutting down AI Notebook System")
        try:
            # Close database connections
            await close_db()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))
    
    return stop_app 