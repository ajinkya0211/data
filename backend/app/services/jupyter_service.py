"""
Jupyter Kernel Service for executing code blocks
"""

import asyncio
import json
import time
from typing import Dict, Any, Optional, List
import httpx
import structlog
from datetime import datetime

from app.core.config import settings
from app.models.block import BlockStatus, BlockExecutionResult, BlockExecutionRequest
from app.models.artifact import Artifact, ArtifactCreate

logger = structlog.get_logger()

class JupyterService:
    """Service for managing Jupyter kernels and executing code blocks"""
    
    def __init__(self):
        self.base_url = settings.JUPYTER_KERNEL_URL
        self.token = settings.JUPYTER_KERNEL_TOKEN
        self.timeout = settings.KERNEL_TIMEOUT_SECONDS
        self.active_kernels: Dict[str, Dict[str, Any]] = {}
        
    async def start_kernel(self, kernel_name: str = "python3") -> Optional[str]:
        """Start a new Jupyter kernel"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Start kernel
                response = await client.post(
                    f"{self.base_url}/api/kernels",
                    headers={"Authorization": f"Token {self.token}"},
                    json={"name": kernel_name}
                )
                
                if response.status_code == 201:
                    kernel_data = response.json()
                    kernel_id = kernel_data["id"]
                    
                    # Store kernel info
                    self.active_kernels[kernel_id] = {
                        "name": kernel_name,
                        "status": "starting",
                        "created_at": datetime.utcnow(),
                        "last_activity": datetime.utcnow()
                    }
                    
                    logger.info("Kernel started successfully", kernel_id=kernel_id, name=kernel_name)
                    return kernel_id
                else:
                    logger.error("Failed to start kernel", status_code=response.status_code)
                    return None
                    
        except Exception as e:
            logger.error("Error starting kernel", error=str(e))
            return None
    
    async def stop_kernel(self, kernel_id: str) -> bool:
        """Stop a Jupyter kernel"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.delete(
                    f"{self.base_url}/api/kernels/{kernel_id}",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if response.status_code == 204:
                    if kernel_id in self.active_kernels:
                        del self.active_kernels[kernel_id]
                    logger.info("Kernel stopped successfully", kernel_id=kernel_id)
                    return True
                else:
                    logger.error("Failed to stop kernel", status_code=response.status_code)
                    return False
                    
        except Exception as e:
            logger.error("Error stopping kernel", error=str(e))
            return False
    
    async def execute_code(self, kernel_id: str, code: str, block_id: str) -> BlockExecutionResult:
        """Execute code in a Jupyter kernel"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Execute code
                execution_data = {
                    "code": code,
                    "silent": False,
                    "store_history": True,
                    "user_expressions": {},
                    "allow_stdin": False
                }
                
                response = await client.post(
                    f"{self.base_url}/api/kernels/{kernel_id}/execute",
                    headers={"Authorization": f"Token {self.token}"},
                    json=execution_data
                )
                
                if response.status_code == 200:
                    execution_result = response.json()
                    msg_id = execution_result["msg_id"]
                    
                    # Wait for execution to complete and get results
                    result = await self._wait_for_execution_result(kernel_id, msg_id, block_id)
                    return result
                else:
                    logger.error("Failed to execute code", status_code=response.status_code)
                    return BlockExecutionResult(
                        block_id=block_id,
                        status=BlockStatus.FAILED,
                        error=f"Execution failed: HTTP {response.status_code}"
                    )
                    
        except Exception as e:
            logger.error("Error executing code", error=str(e))
            return BlockExecutionResult(
                block_id=block_id,
                status=BlockStatus.FAILED,
                error=str(e)
            )
    
    async def _wait_for_execution_result(self, kernel_id: str, msg_id: str, block_id: str) -> BlockExecutionResult:
        """Wait for execution result and collect outputs"""
        try:
            start_time = time.time()
            outputs = []
            error = None
            status = BlockStatus.RUNNING
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Poll for execution results
                while time.time() - start_time < self.timeout:
                    # Get kernel status
                    status_response = await client.get(
                        f"{self.base_url}/api/kernels/{kernel_id}/status",
                        headers={"Authorization": f"Token {self.token}"}
                    )
                    
                    if status_response.status_code == 200:
                        kernel_status = status_response.json()
                        if kernel_status.get("execution_state") == "idle":
                            # Execution completed, get results
                            break
                    
                    await asyncio.sleep(0.5)
                
                # Get execution results
                result_response = await client.get(
                    f"{self.base_url}/api/kernels/{kernel_id}/history",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if result_response.status_code == 200:
                    history = result_response.json()
                    
                    # Find our execution result
                    for entry in history:
                        if entry.get("msg_id") == msg_id:
                            # Extract outputs
                            if "outputs" in entry:
                                for output in entry["outputs"]:
                                    if output.get("output_type") == "execute_result":
                                        outputs.append(Artifact(
                                            id=f"output_{block_id}_{int(time.time())}",
                                            name=f"Output for block {block_id}",
                                            type="text",
                                            content=output.get("data", {}).get("text/plain", ""),
                                            metadata={
                                                "output_type": "execute_result",
                                                "execution_count": output.get("execution_count"),
                                                "block_id": block_id
                                            }
                                        ))
                                    elif output.get("output_type") == "stream":
                                        outputs.append(Artifact(
                                            id=f"stream_{block_id}_{int(time.time())}",
                                            name=f"Stream output for block {block_id}",
                                            type="text",
                                            content=output.get("text", ""),
                                            metadata={
                                                "output_type": "stream",
                                                "name": output.get("name", "stdout"),
                                                "block_id": block_id
                                            }
                                        ))
                                    elif output.get("output_type") == "error":
                                        error = output.get("evalue", "Unknown error")
                                        status = BlockStatus.FAILED
                            
                            break
                    
                    if not error and status != BlockStatus.FAILED:
                        status = BlockStatus.COMPLETED
                
                execution_time = int((time.time() - start_time) * 1000)
                
                return BlockExecutionResult(
                    block_id=block_id,
                    status=status,
                    execution_time_ms=execution_time,
                    outputs=outputs,
                    error=error
                )
                
        except Exception as e:
            logger.error("Error waiting for execution result", error=str(e))
            return BlockExecutionResult(
                block_id=block_id,
                status=BlockStatus.FAILED,
                error=str(e)
            )
    
    async def get_kernel_status(self, kernel_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a kernel"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/api/kernels/{kernel_id}/status",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error("Error getting kernel status", error=str(e))
            return None
    
    async def list_kernels(self) -> List[Dict[str, Any]]:
        """List all active kernels"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    f"{self.base_url}/api/kernels",
                    headers={"Authorization": f"Token {self.token}"}
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return []
                    
        except Exception as e:
            logger.error("Error listing kernels", error=str(e))
            return []
    
    async def cleanup_inactive_kernels(self, max_idle_time: int = 3600) -> int:
        """Clean up kernels that have been idle for too long"""
        try:
            cleaned_count = 0
            current_time = datetime.utcnow()
            
            for kernel_id, kernel_info in list(self.active_kernels.items()):
                idle_time = (current_time - kernel_info["last_activity"]).total_seconds()
                
                if idle_time > max_idle_time:
                    if await self.stop_kernel(kernel_id):
                        cleaned_count += 1
            
            logger.info("Kernel cleanup completed", cleaned_count=cleaned_count)
            return cleaned_count
            
        except Exception as e:
            logger.error("Error during kernel cleanup", error=str(e))
            return 0 