"""
WebSocket Service for Real-time Execution Monitoring
Provides real-time updates for workflow execution, terminal logs, and system events
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
import structlog
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = structlog.get_logger()

class MessageType(str, Enum):
    # Execution events
    EXECUTION_STARTED = "execution_started"
    EXECUTION_PROGRESS = "execution_progress"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"
    
    # Node events
    NODE_STARTED = "node_started"
    NODE_COMPLETED = "node_completed"
    NODE_FAILED = "node_failed"
    
    # Terminal events
    TERMINAL_OUTPUT = "terminal_output"
    TERMINAL_ERROR = "terminal_error"
    TERMINAL_LOG = "terminal_log"
    
    # System events
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    
    # Client events
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"
    PONG = "pong"

@dataclass
class WebSocketMessage:
    type: MessageType
    data: Dict[str, Any]
    timestamp: datetime
    id: str = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }

class WebSocketConnection:
    def __init__(self, websocket: WebSocket, connection_id: str, user_id: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id = user_id
        self.subscriptions: Set[str] = set()
        self.connected_at = datetime.utcnow()
        self.last_ping = datetime.utcnow()
        self.is_alive = True

class WebSocketService:
    """Service for managing WebSocket connections and real-time communications"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.execution_subscriptions: Dict[str, Set[str]] = {}  # execution_id -> connection_ids
        self.project_subscriptions: Dict[str, Set[str]] = {}   # project_id -> connection_ids
        self.terminal_subscriptions: Dict[str, Set[str]] = {}  # session_id -> connection_ids
        self.message_history: List[WebSocketMessage] = []
        self.heartbeat_task: Optional[asyncio.Task] = None
        
    async def connect(self, websocket: WebSocket, user_id: str) -> str:
        """Accept a new WebSocket connection"""
        connection_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        connection = WebSocketConnection(websocket, connection_id, user_id)
        self.connections[connection_id] = connection
        
        logger.info("WebSocket connected", 
                   connection_id=connection_id, 
                   user_id=user_id,
                   total_connections=len(self.connections))
        
        # Send welcome message
        welcome_msg = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            data={
                "status": "connected",
                "connection_id": connection_id,
                "server_time": datetime.utcnow().isoformat()
            },
            timestamp=datetime.utcnow()
        )
        
        await self._send_message_to_connection(connection_id, welcome_msg)
        
        # Start heartbeat if not already running
        if self.heartbeat_task is None or self.heartbeat_task.done():
            self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """Disconnect a WebSocket connection"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.is_alive = False
            
            # Remove from all subscriptions
            self._remove_from_all_subscriptions(connection_id)
            
            del self.connections[connection_id]
            
            logger.info("WebSocket disconnected", 
                       connection_id=connection_id,
                       total_connections=len(self.connections))
    
    def _remove_from_all_subscriptions(self, connection_id: str):
        """Remove connection from all subscriptions"""
        # Remove from execution subscriptions
        for execution_id, subs in self.execution_subscriptions.items():
            subs.discard(connection_id)
        
        # Remove from project subscriptions
        for project_id, subs in self.project_subscriptions.items():
            subs.discard(connection_id)
        
        # Remove from terminal subscriptions
        for session_id, subs in self.terminal_subscriptions.items():
            subs.discard(connection_id)
        
        # Clean up empty subscription sets
        self.execution_subscriptions = {k: v for k, v in self.execution_subscriptions.items() if v}
        self.project_subscriptions = {k: v for k, v in self.project_subscriptions.items() if v}
        self.terminal_subscriptions = {k: v for k, v in self.terminal_subscriptions.items() if v}
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle incoming message from client"""
        try:
            msg_type = MessageType(message.get("type"))
            data = message.get("data", {})
            
            if msg_type == MessageType.SUBSCRIBE:
                await self._handle_subscribe(connection_id, data)
            elif msg_type == MessageType.UNSUBSCRIBE:
                await self._handle_unsubscribe(connection_id, data)
            elif msg_type == MessageType.PING:
                await self._handle_ping(connection_id)
            else:
                logger.warning("Unknown message type", type=msg_type, connection_id=connection_id)
                
        except Exception as e:
            logger.error("Error handling WebSocket message", 
                        error=str(e), 
                        connection_id=connection_id)
    
    async def _handle_subscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle subscription requests"""
        subscription_type = data.get("subscription_type")
        target_id = data.get("target_id")
        
        if not subscription_type or not target_id:
            await self._send_error(connection_id, "Invalid subscription request")
            return
        
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        if subscription_type == "execution":
            if target_id not in self.execution_subscriptions:
                self.execution_subscriptions[target_id] = set()
            self.execution_subscriptions[target_id].add(connection_id)
            
        elif subscription_type == "project":
            if target_id not in self.project_subscriptions:
                self.project_subscriptions[target_id] = set()
            self.project_subscriptions[target_id].add(connection_id)
            
        elif subscription_type == "terminal":
            if target_id not in self.terminal_subscriptions:
                self.terminal_subscriptions[target_id] = set()
            self.terminal_subscriptions[target_id].add(connection_id)
        
        connection.subscriptions.add(f"{subscription_type}:{target_id}")
        
        # Send confirmation
        confirm_msg = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            data={
                "status": "subscribed",
                "subscription_type": subscription_type,
                "target_id": target_id
            },
            timestamp=datetime.utcnow()
        )
        
        await self._send_message_to_connection(connection_id, confirm_msg)
        
        logger.info("WebSocket subscription added", 
                   connection_id=connection_id,
                   subscription_type=subscription_type,
                   target_id=target_id)
    
    async def _handle_unsubscribe(self, connection_id: str, data: Dict[str, Any]):
        """Handle unsubscription requests"""
        subscription_type = data.get("subscription_type")
        target_id = data.get("target_id")
        
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        if subscription_type == "execution":
            if target_id in self.execution_subscriptions:
                self.execution_subscriptions[target_id].discard(connection_id)
                
        elif subscription_type == "project":
            if target_id in self.project_subscriptions:
                self.project_subscriptions[target_id].discard(connection_id)
                
        elif subscription_type == "terminal":
            if target_id in self.terminal_subscriptions:
                self.terminal_subscriptions[target_id].discard(connection_id)
        
        connection.subscriptions.discard(f"{subscription_type}:{target_id}")
        
        logger.info("WebSocket subscription removed", 
                   connection_id=connection_id,
                   subscription_type=subscription_type,
                   target_id=target_id)
    
    async def _handle_ping(self, connection_id: str):
        """Handle ping from client"""
        if connection_id in self.connections:
            self.connections[connection_id].last_ping = datetime.utcnow()
            
            pong_msg = WebSocketMessage(
                type=MessageType.PONG,
                data={"timestamp": datetime.utcnow().isoformat()},
                timestamp=datetime.utcnow()
            )
            
            await self._send_message_to_connection(connection_id, pong_msg)
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message to client"""
        error_msg = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            data={
                "status": "error",
                "error": error_message
            },
            timestamp=datetime.utcnow()
        )
        
        await self._send_message_to_connection(connection_id, error_msg)
    
    # === BROADCASTING METHODS ===
    
    async def broadcast_execution_event(self, execution_id: str, event_type: str, data: Dict[str, Any]):
        """Broadcast execution events to subscribed clients"""
        message = WebSocketMessage(
            type=MessageType(event_type) if event_type in MessageType._value2member_map_ else MessageType.STATUS_UPDATE,
            data={
                "execution_id": execution_id,
                "event_type": event_type,
                **data
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_to_subscribers(self.execution_subscriptions.get(execution_id, set()), message)
        
        logger.debug("Broadcasted execution event", 
                    execution_id=execution_id,
                    event_type=event_type,
                    subscribers=len(self.execution_subscriptions.get(execution_id, set())))
    
    async def broadcast_terminal_output(self, session_id: str, output_type: str, content: str):
        """Broadcast terminal output to subscribed clients"""
        message = WebSocketMessage(
            type=MessageType.TERMINAL_OUTPUT if output_type == "stdout" else MessageType.TERMINAL_ERROR,
            data={
                "session_id": session_id,
                "output_type": output_type,
                "content": content
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_to_subscribers(self.terminal_subscriptions.get(session_id, set()), message)
    
    async def broadcast_terminal_log(self, session_id: str, log_level: str, message: str):
        """Broadcast terminal logs to subscribed clients"""
        log_message = WebSocketMessage(
            type=MessageType.TERMINAL_LOG,
            data={
                "session_id": session_id,
                "log_level": log_level,
                "message": message
            },
            timestamp=datetime.utcnow()
        )
        
        await self._broadcast_to_subscribers(self.terminal_subscriptions.get(session_id, set()), log_message)
    
    async def broadcast_system_status(self, status_data: Dict[str, Any]):
        """Broadcast system status to all connected clients"""
        message = WebSocketMessage(
            type=MessageType.STATUS_UPDATE,
            data=status_data,
            timestamp=datetime.utcnow()
        )
        
        # Send to all connections
        all_connection_ids = set(self.connections.keys())
        await self._broadcast_to_subscribers(all_connection_ids, message)
    
    async def _broadcast_to_subscribers(self, connection_ids: Set[str], message: WebSocketMessage):
        """Send message to a set of connections"""
        if not connection_ids:
            return
        
        # Store message in history
        self.message_history.append(message)
        
        # Keep only last 1000 messages
        if len(self.message_history) > 1000:
            self.message_history = self.message_history[-1000:]
        
        # Send to all connections
        tasks = []
        for connection_id in connection_ids:
            if connection_id in self.connections:
                task = self._send_message_to_connection(connection_id, message)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_message_to_connection(self, connection_id: str, message: WebSocketMessage):
        """Send message to a specific connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        try:
            await connection.websocket.send_text(json.dumps(message.to_dict()))
        except Exception as e:
            logger.warning("Failed to send WebSocket message", 
                          connection_id=connection_id,
                          error=str(e))
            # Mark connection as dead and disconnect
            await self.disconnect(connection_id)
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat to all connections"""
        while True:
            try:
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
                if not self.connections:
                    continue
                
                heartbeat_msg = WebSocketMessage(
                    type=MessageType.HEARTBEAT,
                    data={
                        "timestamp": datetime.utcnow().isoformat(),
                        "active_connections": len(self.connections)
                    },
                    timestamp=datetime.utcnow()
                )
                
                # Send to all connections
                dead_connections = []
                for connection_id, connection in self.connections.items():
                    try:
                        await connection.websocket.send_text(json.dumps(heartbeat_msg.to_dict()))
                    except Exception:
                        dead_connections.append(connection_id)
                
                # Clean up dead connections
                for connection_id in dead_connections:
                    await self.disconnect(connection_id)
                
            except Exception as e:
                logger.error("Heartbeat loop error", error=str(e))
    
    # === UTILITY METHODS ===
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about WebSocket connections"""
        return {
            "total_connections": len(self.connections),
            "execution_subscriptions": len(self.execution_subscriptions),
            "project_subscriptions": len(self.project_subscriptions),
            "terminal_subscriptions": len(self.terminal_subscriptions),
            "message_history_count": len(self.message_history)
        }
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific connection"""
        if connection_id not in self.connections:
            return None
        
        connection = self.connections[connection_id]
        return {
            "connection_id": connection_id,
            "user_id": connection.user_id,
            "connected_at": connection.connected_at.isoformat(),
            "last_ping": connection.last_ping.isoformat(),
            "subscriptions": list(connection.subscriptions),
            "is_alive": connection.is_alive
        }

# Global WebSocket service instance
websocket_service = WebSocketService()
