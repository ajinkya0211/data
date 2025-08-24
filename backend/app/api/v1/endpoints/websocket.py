"""
WebSocket endpoints for real-time communication
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Optional
import structlog

from app.services.websocket_service import websocket_service
from app.core.websocket_auth import authenticate_websocket

logger = structlog.get_logger()

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: Optional[str] = None):
    """
    WebSocket endpoint for real-time communication
    
    Query parameters:
    - token: JWT authentication token
    """
    connection_id = None
    
    try:
        # Authenticate user
        user_id = await authenticate_websocket(websocket, token)
        if not user_id:
            return
        
        # Accept connection
        connection_id = await websocket_service.connect(websocket, user_id)
        
        logger.info("WebSocket connection established", 
                   connection_id=connection_id, 
                   user_id=user_id)
        
        # Handle messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle the message
                await websocket_service.handle_message(connection_id, message)
                
            except WebSocketDisconnect:
                logger.info("WebSocket client disconnected", connection_id=connection_id)
                break
            except json.JSONDecodeError:
                logger.warning("Invalid JSON received", connection_id=connection_id)
                await websocket_service._send_error(connection_id, "Invalid JSON format")
            except Exception as e:
                logger.error("WebSocket message handling error", 
                           connection_id=connection_id,
                           error=str(e))
                
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
        if connection_id:
            await websocket_service.disconnect(connection_id)
    
    finally:
        if connection_id:
            await websocket_service.disconnect(connection_id)

@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return websocket_service.get_connection_stats()

@router.get("/ws/connections/{connection_id}")
async def get_connection_info(connection_id: str):
    """Get information about a specific WebSocket connection"""
    info = websocket_service.get_connection_info(connection_id)
    if not info:
        raise HTTPException(status_code=404, detail="Connection not found")
    return info
