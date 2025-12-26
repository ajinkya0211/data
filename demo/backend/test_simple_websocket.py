#!/usr/bin/env python3
"""
Simple WebSocket test for basic endpoint
"""
import asyncio
import websockets

async def test_simple_websocket():
    """Test simple WebSocket connection"""
    uri = "ws://localhost:8000/ws/test"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to simple WebSocket")
            
            # Receive the message
            message = await websocket.recv()
            print(f"📨 Received: {message}")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing simple WebSocket...")
    asyncio.run(test_simple_websocket())

