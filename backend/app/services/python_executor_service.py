"""
Python Code Execution Service with Persistent Kernel
This service provides a persistent Python execution environment similar to Jupyter kernels
that maintains state between code block executions and provides access to datasets.
"""

import asyncio
import json
import time
import traceback
import io
import sys
import contextlib
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import structlog
import subprocess
import tempfile
import os
import pickle
import base64
from pathlib import Path

from app.models.block import BlockStatus, BlockExecutionResult
from app.models.artifact import Artifact, ArtifactCreate

logger = structlog.get_logger()

class PythonExecutorService:
    """Service for executing Python code blocks in a persistent kernel environment"""
    
    def __init__(self, websocket_service=None):
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.kernels: Dict[str, Dict[str, Any]] = {}
        self.data_dir = Path("data")
        self.websocket_service = websocket_service
        
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        
    async def start_execution_session(self, session_name: str = "python3") -> str:
        """Start a new execution session with a persistent kernel"""
        try:
            session_id = f"session_{int(time.time())}_{hash(session_name)}"
            
            # Start a persistent Python kernel process
            kernel_process = await self._start_kernel_process(session_id)
            
            if not kernel_process:
                raise Exception("Failed to start kernel process")
            
            self.kernels[session_id] = {
                "process": kernel_process,
                "variables": {},
                "data_files": {},
                "working_dir": os.getcwd(),
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
            
            self.active_executions[session_id] = {
                "name": session_name,
                "status": "ready",
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "variables": {},
                "outputs": []
            }
            
            # Initialize kernel with common imports and setup
            await self._initialize_kernel(session_id)
            
            logger.info("Execution session started with persistent kernel", 
                       session_id=session_id, name=session_name)
            return session_id
            
        except Exception as e:
            logger.error("Error starting execution session", error=str(e))
            return None
    
    async def _start_kernel_process(self, session_id: str) -> Optional[subprocess.Popen]:
        """Start a persistent Python kernel process"""
        try:
            # Create a kernel script that maintains state
            kernel_script_path = self._create_kernel_script(session_id)
            
            logger.info("Starting kernel process", kernel_script_path=kernel_script_path)
            
            # Start the kernel process
            process = subprocess.Popen(
                [sys.executable, kernel_script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for kernel to be ready with timeout
            import time
            start_time = time.time()
            timeout = 10  # 10 seconds timeout
            
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    # Process died
                    stderr_output = process.stderr.read()
                    logger.error("Kernel process died", stderr=stderr_output)
                    return None
                
                # Check if stdout has data
                if process.stdout.readable():
                    ready_signal = process.stdout.readline().strip()
                    if ready_signal == "KERNEL_READY":
                        logger.info("Kernel process started successfully")
                        return process
                    elif ready_signal:
                        logger.info("Kernel output", output=ready_signal)
                
                time.sleep(0.1)
            
            # Timeout reached
            logger.error("Kernel startup timeout")
            process.terminate()
            return None
                
        except Exception as e:
            logger.error("Failed to start kernel process", error=str(e))
            return None
    
    def _create_kernel_script(self, session_id: str) -> str:
        """Create a kernel script that maintains state"""
        try:
            # Create kernel script content
            kernel_script_content = [
                "import sys",
                "import os",
                "import pickle",
                "import base64",
                "import json",
                "import traceback",
                "import io",
                "from pathlib import Path",
                "",
                "# Add current directory to Python path",
                "sys.path.insert(0, os.getcwd())",
                "",
                "# Global state storage",
                "kernel_state = {",
                "    'variables': {},",
                "    'data_files': {},",
                "    'working_dir': os.getcwd()",
                "}",
                "",
                "# Common imports",
                "try:",
                "    import pandas as pd",
                "    import numpy as np",
                "    import matplotlib.pyplot as plt",
                "    import seaborn as sns",
                "    from pathlib import Path",
                "    print('Common libraries imported successfully')",
                "except ImportError as e:",
                "    print(f'Warning: Some libraries not available: {e}')",
                "",
                "# Setup data directory",
                "data_dir = Path('data')",
                "data_dir.mkdir(exist_ok=True)",
                "",
                "def execute_code(code):",
                "    \"\"\"Execute Python code and capture results\"\"\"",
                "    try:",
                "        # Capture stdout/stderr",
                "        old_stdout = sys.stdout",
                "        old_stderr = sys.stderr",
                "        ",
                "        stdout_capture = io.StringIO()",
                "        stderr_capture = io.StringIO()",
                "        ",
                "        sys.stdout = stdout_capture",
                "        sys.stderr = stderr_capture",
                "        ",
                "        # Execute the code",
                "        exec(code, globals(), kernel_state['variables'])",
                "        ",
                "        # Restore stdout/stderr",
                "        sys.stdout = old_stdout",
                "        sys.stderr = old_stderr",
                "        ",
                "        # Capture outputs",
                "        stdout_content = stdout_capture.getvalue()",
                "        stderr_content = stderr_capture.getvalue()",
                "        ",
                "        # Check for data files",
                "        data_files = []",
                "        for file_path in Path('.').glob('*.csv'):",
                "            if file_path.name not in kernel_state['data_files']:",
                "                kernel_state['data_files'][file_path.name] = str(file_path.absolute())",
                "                data_files.append(file_path.name)",
                "        ",
                "        for file_path in Path('.').glob('*.png'):",
                "            if file_path.name not in kernel_state['data_files']:",
                "                kernel_state['data_files'][file_path.name] = str(file_path.absolute())",
                "                data_files.append(file_path.name)",
                "        ",
                "        # Return execution result",
                "        return {",
                "            'success': True,",
                "            'stdout': stdout_content,",
                "            'stderr': stderr_content,",
                "            'variables': list(kernel_state['variables'].keys()),",
                "            'data_files': data_files,",
                "            'working_dir': kernel_state['working_dir']",
                "        }",
                "        ",
                "    except Exception as e:",
                "        # Restore stdout/stderr",
                "        sys.stdout = old_stdout",
                "        sys.stderr = old_stderr",
                "        ",
                "        return {",
                "            'success': False,",
                "            'error': str(e),",
                "            'traceback': traceback.format_exc(),",
                "            'stdout': stdout_capture.getvalue() if 'stdout_capture' in locals() else '',",
                "            'stderr': stderr_capture.getvalue() if 'stderr_capture' in locals() else ''",
                "        }",
                "",
                "# Signal kernel is ready",
                "print('KERNEL_READY')",
                "sys.stdout.flush()",
                "",
                "# Main kernel loop",
                "while True:",
                "    try:",
                "        # Read command from stdin",
                "        command = input().strip()",
                "        ",
                "        if command == 'EXIT':",
                "            break",
                "            ",
                "        # Parse command",
                "        cmd_data = json.loads(command)",
                "        cmd_type = cmd_data.get('type')",
                "        ",
                "        if cmd_type == 'execute':",
                "            # Execute code",
                "            code = cmd_data.get('code', '')",
                "            result = execute_code(code)",
                "            print(json.dumps(result))",
                "            sys.stdout.flush()",
                "            ",
                "        elif cmd_type == 'get_variables':",
                "            # Return current variables",
                "            result = {",
                "                'type': 'variables',",
                "                'variables': list(kernel_state['variables'].keys()),",
                "                'data_files': list(kernel_state['data_files'].keys())",
                "            }",
                "            print(json.dumps(result))",
                "            sys.stdout.flush()",
                "            ",
                "        elif cmd_type == 'get_variable':",
                "            # Return specific variable value",
                "            var_name = cmd_data.get('var_name', '')",
                "            if var_name in kernel_state['variables']:",
                "                result = {",
                "                    'type': 'variable_value',",
                "                    'var_name': var_name,",
                "                    'value': str(kernel_state['variables'][var_name])",
                "                }",
                "            else:",
                "                result = {",
                "                    'type': 'variable_value',",
                "                'var_name': var_name,",
                "                'error': 'Variable not found'",
                "                }",
                "            print(json.dumps(result))",
                "            sys.stdout.flush()",
                "            ",
                "    except EOFError:",
                "        break",
                "    except Exception as e:",
                "        error_result = {",
                "            'type': 'error',",
                "            'error': str(e),",
                "            'traceback': traceback.format_exc()",
                "        }",
                "        print(json.dumps(error_result))",
                "        sys.stdout.flush()",
            ]
            
            # Write kernel script to temporary file
            kernel_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            kernel_file.write('\n'.join(kernel_script_content))
            kernel_file.close()
            
            logger.info("Kernel script created", kernel_file=kernel_file.name)
            return kernel_file.name
            
        except Exception as e:
            logger.error("Failed to create kernel script", error=str(e))
            raise
    
    async def _initialize_kernel(self, session_id: str):
        """Initialize kernel with common setup"""
        try:
            kernel = self.kernels[session_id]
            process = kernel['process']
            
            # Wait a bit for kernel to be fully ready
            import time
            time.sleep(0.5)
            
            # Setup data directory access
            setup_code = '''
# Setup data access
import os
import pandas as pd
from pathlib import Path

# Ensure data directory exists
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

# List available data files
print("Available data files:")
for file_path in data_dir.glob("*.csv"):
    print(f"  - {file_path.name}")
    kernel_state['data_files'][file_path.name] = str(file_path.absolute())

print("Kernel initialized and ready!")
'''
            
            # Send initialization code
            init_command = {
                'type': 'execute',
                'code': setup_code
            }
            
            process.stdin.write(json.dumps(init_command) + '\n')
            process.stdin.flush()
            
            # Read response with timeout
            start_time = time.time()
            timeout = 5
            
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    logger.error("Kernel process died during initialization")
                    return
                
                if process.stdout.readable():
                    response = process.stdout.readline().strip()
                    if response:
                        logger.info("Kernel initialization response", response=response)
                        break
                
                time.sleep(0.1)
            else:
                logger.warning("Kernel initialization timeout")
            
        except Exception as e:
            logger.error("Failed to initialize kernel", error=str(e))
    
    async def stop_execution_session(self, session_id: str) -> bool:
        """Stop an execution session and terminate the kernel"""
        try:
            # Terminate kernel process
            if session_id in self.kernels:
                kernel = self.kernels[session_id]
                process = kernel['process']
                
                # Send exit command
                exit_command = {'type': 'exit'}
                process.stdin.write(json.dumps(exit_command) + '\n')
                process.stdin.flush()
                
                # Wait for process to terminate
                process.wait(timeout=5)
                
                del self.kernels[session_id]
            
            # Clean up execution session
            if session_id in self.active_executions:
                del self.active_executions[session_id]
                
            logger.info("Execution session stopped", session_id=session_id)
            return True
            
        except Exception as e:
            logger.error("Error stopping execution session", error=str(e))
            return False
    
    async def execute_code(self, session_id: str, code: str, block_id: str) -> BlockExecutionResult:
        """Execute Python code in the persistent kernel"""
        start_time = time.time()
        
        try:
            if session_id not in self.kernels:
                raise Exception(f"Kernel session {session_id} not found")
            
            kernel = self.kernels[session_id]
            process = kernel['process']
            
            # Update session status
            if session_id in self.active_executions:
                self.active_executions[session_id]["status"] = "executing"
                self.active_executions[session_id]["last_activity"] = datetime.utcnow()
            
            # Broadcast execution started event
            await self._broadcast_terminal_event(session_id, "execution_started", {
                "block_id": block_id,
                "code_preview": code[:100] + "..." if len(code) > 100 else code
            })
            
            # Send execution command to kernel
            execute_command = {
                'type': 'execute',
                'code': code
            }
            
            process.stdin.write(json.dumps(execute_command) + '\n')
            process.stdin.flush()
            
            # Read response from kernel with real-time streaming
            execution_result = await self._read_execution_result_with_streaming(
                process, session_id, block_id
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Parse outputs
            outputs = []
            
            if execution_result.get('stdout'):
                outputs.append({
                    "type": "text/plain",
                    "content": execution_result['stdout'],
                    "metadata": {"output_type": "stdout"}
                })
            
            if execution_result.get('stderr'):
                outputs.append({
                    "type": "text/plain",
                    "content": execution_result['stderr'],
                    "metadata": {"output_type": "stderr"}
                })
            
            # Update kernel state
            if execution_result.get('success'):
                kernel['variables'].update({var: True for var in execution_result.get('variables', [])})
                kernel['data_files'].update({f: True for f in execution_result.get('data_files', [])})
                kernel['last_activity'] = datetime.utcnow()
            
            # Create execution result
            result = BlockExecutionResult(
                block_id=block_id,
                session_id=session_id,
                status=BlockStatus.COMPLETED if execution_result.get('success') else BlockStatus.FAILED,
                execution_time_ms=execution_time_ms,
                outputs=outputs,
                error=execution_result.get('error'),
                metadata={
                    "variables_created": execution_result.get('variables', []),
                    "data_files_created": execution_result.get('data_files', []),
                    "working_dir": execution_result.get('working_dir'),
                    "execution_timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Update session
            if session_id in self.active_executions:
                self.active_executions[session_id]["variables"].update(
                    {var: True for var in execution_result.get('variables', [])}
                )
                self.active_executions[session_id]["outputs"].extend(outputs)
                self.active_executions[session_id]["status"] = "ready"
                self.active_executions[session_id]["last_activity"] = datetime.utcnow()
            
            # Store in history
            self.execution_history.append({
                "session_id": session_id,
                "block_id": block_id,
                "code": code,
                "result": result.dict(),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            logger.info("Code execution completed", 
                       session_id=session_id, 
                       block_id=block_id, 
                       success=execution_result.get('success'),
                       execution_time_ms=execution_time_ms)
            
            return result
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Execution error: {str(e)}"
            
            logger.error("Code execution failed", 
                        session_id=session_id, 
                        block_id=block_id, 
                        error=str(e))
            
            # Update session status
            if session_id in self.active_executions:
                self.active_executions[session_id]["status"] = "error"
                self.active_executions[session_id]["last_activity"] = datetime.utcnow()
            
            return BlockExecutionResult(
                block_id=block_id,
                session_id=session_id,
                status=BlockStatus.FAILED,
                execution_time_ms=execution_time_ms,
                outputs=[],
                error=error_msg,
                metadata={
                    "error_traceback": traceback.format_exc(),
                    "execution_timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an execution session"""
        session_info = self.active_executions.get(session_id, {})
        
        if session_id in self.kernels:
            kernel = self.kernels[session_id]
            session_info.update({
                "kernel_variables": list(kernel['variables'].keys()),
                "kernel_data_files": list(kernel['data_files'].keys()),
                "kernel_working_dir": kernel['working_dir']
            })
        
        return session_info
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """List all active execution sessions"""
        return [
            {
                "session_id": session_id,
                **session_info
            }
            for session_id, session_info in self.active_executions.items()
        ]
    
    async def get_execution_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history"""
        return self.execution_history[-limit:] if self.execution_history else []
    
    async def install_requirements(self, requirements: List[str]) -> Dict[str, Any]:
        """Install Python packages (simulated for now)"""
        try:
            # In a real implementation, this would use pip
            logger.info("Requirements installation requested", requirements=requirements)
            
            return {
                "success": True,
                "message": f"Requirements {requirements} would be installed",
                "installed_packages": requirements
            }
        except Exception as e:
            logger.error("Failed to install requirements", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    # === REAL-TIME STREAMING METHODS ===
    
    async def _read_execution_result_with_streaming(
        self, 
        process: subprocess.Popen, 
        session_id: str, 
        block_id: str
    ) -> Dict[str, Any]:
        """Read execution result with real-time output streaming"""
        try:
            # For now, read the complete result (future enhancement: stream line by line)
            response = process.stdout.readline().strip()
            execution_result = json.loads(response)
            
            # Stream stdout if available
            if execution_result.get('stdout'):
                await self._broadcast_terminal_output(
                    session_id, 
                    "stdout", 
                    execution_result['stdout']
                )
            
            # Stream stderr if available
            if execution_result.get('stderr'):
                await self._broadcast_terminal_output(
                    session_id, 
                    "stderr", 
                    execution_result['stderr']
                )
            
            return execution_result
            
        except Exception as e:
            logger.error("Error reading execution result", error=str(e))
            return {"success": False, "stderr": str(e)}
    
    async def _broadcast_terminal_output(self, session_id: str, output_type: str, content: str):
        """Broadcast terminal output via WebSocket"""
        if self.websocket_service:
            try:
                await self.websocket_service.broadcast_terminal_output(
                    session_id, output_type, content
                )
            except Exception as e:
                logger.warning("Failed to broadcast terminal output", error=str(e))
    
    async def _broadcast_terminal_event(self, session_id: str, event_type: str, data: Dict[str, Any]):
        """Broadcast terminal events via WebSocket"""
        if self.websocket_service:
            try:
                await self.websocket_service.broadcast_terminal_log(
                    session_id, "info", f"{event_type}: {json.dumps(data)}"
                )
            except Exception as e:
                logger.warning("Failed to broadcast terminal event", error=str(e))
    
    def set_websocket_service(self, websocket_service):
        """Set the WebSocket service for real-time communication"""
        self.websocket_service = websocket_service
        logger.info("WebSocket service connected to Python executor")
    
    async def stream_kernel_logs(self, session_id: str, message: str, level: str = "info"):
        """Stream kernel logs to WebSocket subscribers"""
        if self.websocket_service:
            try:
                await self.websocket_service.broadcast_terminal_log(
                    session_id, level, message
                )
            except Exception as e:
                logger.warning("Failed to stream kernel logs", error=str(e)) 