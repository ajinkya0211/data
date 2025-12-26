#!/usr/bin/env python3
"""
Simple WebSocket test client for testing real-time communication
"""
import asyncio
import websockets
import json
import time

async def test_websocket():
    """Test WebSocket connection and real-time updates"""
    uri = "ws://localhost:8000/ws"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Send a ping to test basic communication
            await websocket.send(json.dumps({"type": "ping"}))
            
            # Listen for messages
            print("🔍 Listening for real-time updates...")
            start_time = time.time()
            
            while time.time() - start_time < 30:  # Listen for 30 seconds
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "pong":
                        print("✅ Ping-pong successful")
                    elif data.get("type") == "system_metrics":
                        print(f"📊 System metrics: {data.get('workflows_count')} workflows, {data.get('blocks_count')} blocks")
                    elif data.get("type") == "execution_started":
                        print(f"🚀 Execution started for workflow: {data.get('workflow_id')}")
                    elif data.get("type") == "execution_completed":
                        print(f"✅ Execution completed: {'Success' if data.get('success') else 'Failed'}")
                    elif data.get("type") == "block_executed":
                        print(f"🔧 Block executed: {data.get('block_id')} - {data.get('status')}")
                    elif data.get("type") == "dag_updated":
                        print(f"🔄 DAG updated: {len(data.get('nodes', []))} nodes, {len(data.get('edges', []))} edges")
                    else:
                        print(f"📨 Received: {data.get('type', 'unknown')}")
                        
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

if __name__ == "__main__":
    print("🧪 Testing WebSocket real-time communication...")
    asyncio.run(test_websocket())
