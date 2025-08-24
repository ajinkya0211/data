"""
WebSocket Authentication utilities
"""

from typing import Optional
from fastapi import WebSocket, status
import jwt
import structlog

from app.core.config import settings

logger = structlog.get_logger()

async def authenticate_websocket(websocket: WebSocket, token: Optional[str] = None) -> Optional[str]:
    """
    Authenticate WebSocket connection and return user_id
    
    Args:
        websocket: WebSocket connection
        token: JWT token from query parameter
        
    Returns:
        user_id if authenticated, None otherwise
    """
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication required")
        return None
    
    try:
        # For now, simplified authentication - in production, decode JWT properly
        # payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        # user_id = payload.get("sub")
        
        # Simplified for demo - just use token as user_id
        # In production, this should properly validate JWT
        user_id = token if token.startswith("admin") or token.startswith("user") else "demo_user"
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token expired")
        return None
    except jwt.InvalidTokenError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None
    except Exception as e:
        logger.error("WebSocket authentication error", error=str(e))
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication error")
        return None
