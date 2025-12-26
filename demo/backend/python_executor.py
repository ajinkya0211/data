"""
Enhanced Python Execution Service
Provides sophisticated code execution with session management and variable tracking
"""

import asyncio
import subprocess
import tempfile
import os
import sys
import json
import re
import traceback
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import logging
import uuid
import traceback
from pathlib import Path
from enum import Enum

# Data science libraries
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    DS_LIBS_AVAILABLE = True
except ImportError:
    DS_LIBS_AVAILABLE = False
    print("Warning: Some data science libraries not available")

logger = logging.getLogger(__name__)

class ExecutionStatus(Enum):
    """Status of code execution"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class ExecutionResult:
    """Result of code execution"""
    success: bool
    output: Optional[str]
    error: Optional[str]
    execution_time: float
    variables_defined: Dict[str, Any]
    variables_used: List[str]
    imports_added: List[str]
    functions_defined: List[str]
    functions_called: List[str]
    dataframes_created: List[str]
    plots_generated: List[str]
    memory_usage: Optional[float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class SessionState:
    """State of a Python execution session"""
    session_id: str
    variables: Dict[str, Any]
    dataframes: Dict[str, Any]
    imports: Set[str]
    functions: Dict[str, str]
    classes: Dict[str, str]
    execution_history: List[Dict[str, Any]]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    memory_usage: float = 0.0
    is_active: bool = True

class CodeAnalyzer:
    """Enhanced analyzer for Python code dependencies and structure"""
    
    def __init__(self):
        # Import patterns
        self.import_patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import\s+(\w+)',
            r'^from\s+(\w+)\s+import\s+\*',
        ]
        
        # Variable patterns
        self.variable_pattern = r'^(\w+)\s*=\s*([^#\n]+)'
        self.variable_usage_pattern = r'\b(\w+)\b(?=\s*[^\w\s])'
        
        # Function patterns
        self.function_def_pattern = r'^def\s+(\w+)\s*\('
        self.function_call_pattern = r'\b(\w+)\s*\('
        
        # Class patterns
        self.class_def_pattern = r'^class\s+(\w+)'
        self.class_usage_pattern = r'\b(\w+)\s*\.\s*\w+'
        
        # Data structure patterns
        self.dataframe_pattern = r'(\w+)\s*=\s*pd\.DataFrame\('
        self.array_pattern = r'(\w+)\s*=\s*np\.(array|zeros|ones|linspace|arange)'
        self.plot_pattern = r'plt\.(figure|subplot|plot|hist|scatter|bar|boxplot|violinplot|heatmap|pairplot)'
        
        # Library installation patterns
        self.pip_install_pattern = r'pip\s+install\s+([^\s]+)'
        self.conda_install_pattern = r'conda\s+install\s+([^\s]+)'
        
        # File I/O patterns
        self.file_read_pattern = r'(?:pd\.|np\.)?(?:read_csv|read_json|read_excel|load|loadtxt)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        self.file_write_pattern = r'(?:pd\.|np\.)?(?:to_csv|to_json|to_excel|save|savetxt)\s*\(\s*[\'"]([^\'"]+)[\'"]'
        
        # Common library aliases
        self.library_aliases = {
            'pd': 'pandas',
            'np': 'numpy',
            'plt': 'matplotlib.pyplot',
            'sns': 'seaborn',
            'sk': 'sklearn',
            'tf': 'tensorflow',
            'torch': 'torch',
            'cv2': 'opencv-python'
        }
    
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code and extract comprehensive dependency information"""
        lines = code.split('\n')
        analysis = {
            'imports': [],
            'imports_with_aliases': {},
            'variables_defined': [],
            'variables_used': [],
            'functions_defined': [],
            'functions_called': [],
            'classes_defined': [],
            'classes_used': [],
            'dataframes_created': [],
            'arrays_created': [],
            'plots_generated': [],
            'libraries_required': set(),
            'files_read': [],
            'files_written': [],
            'dependencies': {
                'variables': set(),
                'functions': set(),
                'classes': set(),
                'libraries': set(),
                'files': set()
            },
            'has_errors': False,
            'estimated_complexity': 0,
            'execution_requirements': []
        }
        
        # Track context for better analysis
        current_context = {
            'in_function': False,
            'in_class': False,
            'current_function': None,
            'current_class': None
        }
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Update context
            if re.match(self.function_def_pattern, line):
                current_context['in_function'] = True
                current_context['current_function'] = re.match(self.function_def_pattern, line).group(1)
            elif line.startswith('class '):
                current_context['in_class'] = True
                current_context['current_class'] = re.match(self.class_def_pattern, line).group(1)
            elif line.startswith('def ') or line.startswith('class '):
                current_context['in_function'] = False
                current_context['in_class'] = False
                current_context['current_function'] = None
                current_context['current_class'] = None
            
            # Analyze imports
            self._analyze_imports(line, analysis)
            
            # Analyze variable definitions and usage
            self._analyze_variables(line, analysis, current_context)
            
            # Analyze functions
            self._analyze_functions(line, analysis, current_context)
            
            # Analyze classes
            self._analyze_classes(line, analysis, current_context)
            
            # Analyze data structures
            self._analyze_data_structures(line, analysis)
            
            # Analyze file operations
            self._analyze_file_operations(line, analysis)
            
            # Analyze library requirements
            self._analyze_library_requirements(line, analysis)
        
        # Post-process analysis
        self._post_process_analysis(analysis)
        
        return analysis
    
    def _analyze_imports(self, line: str, analysis: Dict[str, Any]):
        """Analyze import statements"""
        for pattern in self.import_patterns:
            match = re.match(pattern, line)
            if match:
                if 'from' in pattern:
                    if '*' in line:
                        module = match.group(1)
                        analysis['imports'].append(f"from {module} import *")
                        analysis['libraries_required'].add(module)
                    else:
                        module = match.group(1)
                        item = match.group(2)
                        analysis['imports'].append(f"from {module} import {item}")
                        analysis['imports_with_aliases'][item] = module
                        analysis['libraries_required'].add(module)
                else:
                    module = match.group(1)
                    analysis['imports'].append(f"import {module}")
                    analysis['libraries_required'].add(module)
                break
    
    def _analyze_variables(self, line: str, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Analyze variable definitions and usage"""
        # Variable definitions
        var_match = re.match(self.variable_pattern, line)
        if var_match:
            var_name = var_match.group(1)
            if var_name not in ['pd', 'np', 'plt', 'sns', 'df']:
                analysis['variables_defined'].append(var_name)
                analysis['dependencies']['variables'].add(var_name)
        
        # Variable usage (excluding function calls and definitions)
        if not re.match(self.function_def_pattern, line) and not re.match(self.class_def_pattern, line):
            usage_matches = re.findall(self.variable_usage_pattern, line)
            for var in usage_matches:
                if var not in ['def', 'class', 'if', 'for', 'while', 'try', 'except', 'with', 'as', 'in', 'is', 'and', 'or', 'not']:
                    analysis['variables_used'].append(var)
    
    def _analyze_functions(self, line: str, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Analyze function definitions and calls"""
        # Function definitions
        func_match = re.match(self.function_def_pattern, line)
        if func_match:
            func_name = func_match.group(1)
            analysis['functions_defined'].append(func_name)
            analysis['dependencies']['functions'].add(func_name)
        
        # Function calls (excluding definitions)
        if not re.match(self.function_def_pattern, line):
            func_calls = re.findall(self.function_call_pattern, line)
            for func in func_calls:
                if func not in ['def', 'class', 'if', 'for', 'while', 'try', 'except', 'with']:
                    analysis['functions_called'].append(func)
    
    def _analyze_classes(self, line: str, analysis: Dict[str, Any], context: Dict[str, Any]):
        """Analyze class definitions and usage"""
        # Class definitions
        class_match = re.match(self.class_def_pattern, line)
        if class_match:
            class_name = class_match.group(1)
            analysis['classes_defined'].append(class_name)
            analysis['dependencies']['classes'].add(class_name)
        
        # Class usage
        class_usage = re.findall(self.class_usage_pattern, line)
        for class_name in class_usage:
            if class_name not in ['pd', 'np', 'plt', 'sns']:
                analysis['classes_used'].append(class_name)
    
    def _analyze_data_structures(self, line: str, analysis: Dict[str, Any]):
        """Analyze data structure creation"""
        # DataFrames
        df_match = re.search(self.dataframe_pattern, line)
        if df_match:
            analysis['dataframes_created'].append(df_match.group(1))
        
        # Arrays
        array_match = re.search(self.array_pattern, line)
        if array_match:
            analysis['arrays_created'].append(array_match.group(1))
        
        # Plots
        plot_match = re.search(self.plot_pattern, line)
        if plot_match:
            analysis['plots_generated'].append(plot_match.group(1))
    
    def _analyze_file_operations(self, line: str, analysis: Dict[str, Any]):
        """Analyze file read/write operations"""
        # File reads
        read_matches = re.findall(self.file_read_pattern, line)
        for file_path in read_matches:
            analysis['files_read'].append(file_path)
            analysis['dependencies']['files'].add(file_path)
        
        # File writes
        write_matches = re.findall(self.file_write_pattern, line)
        for file_path in write_matches:
            analysis['files_written'].append(file_path)
    
    def _analyze_library_requirements(self, line: str, analysis: Dict[str, Any]):
        """Analyze library installation requirements"""
        # Pip installs
        pip_matches = re.findall(self.pip_install_pattern, line)
        for lib in pip_matches:
            analysis['libraries_required'].add(lib)
            analysis['dependencies']['libraries'].add(lib)
        
        # Conda installs
        conda_matches = re.findall(self.conda_install_pattern, line)
        for lib in conda_matches:
            analysis['libraries_required'].add(lib)
            analysis['dependencies']['libraries'].add(lib)
    
    def _post_process_analysis(self, analysis: Dict[str, Any]):
        """Post-process analysis results"""
        # Convert sets to lists for JSON serialization
        analysis['libraries_required'] = list(analysis['libraries_required'])
        analysis['dependencies'] = {
            k: list(v) for k, v in analysis['dependencies'].items()
        }
        
        # Calculate complexity score
        complexity = 0
        complexity += len(analysis['variables_defined']) * 1
        complexity += len(analysis['functions_defined']) * 3
        complexity += len(analysis['classes_defined']) * 5
        complexity += len(analysis['imports']) * 1
        complexity += len(analysis['dataframes_created']) * 2
        complexity += len(analysis['plots_generated']) * 2
        
        analysis['estimated_complexity'] = complexity
        
        # Generate execution requirements
        requirements = []
        if analysis['libraries_required']:
            requirements.append(f"Install libraries: {', '.join(analysis['libraries_required'])}")
        if analysis['files_read']:
            requirements.append(f"Required files: {', '.join(analysis['files_read'])}")
        if analysis['variables_used']:
            requirements.append(f"Required variables: {', '.join(set(analysis['variables_used']))}")
        if analysis['functions_called']:
            requirements.append(f"Required functions: {', '.join(set(analysis['functions_called']))}")
        
        analysis['execution_requirements'] = requirements
        
        return analysis

class SessionManager:
    """Manages Python execution sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionState] = {}
        self.global_imports = {
            'pandas': 'pd',
            'numpy': 'np', 
            'matplotlib.pyplot': 'plt',
            'seaborn': 'sns',
            'datetime': 'datetime',
            'json': 'json',
            're': 're',
            'os': 'os',
            'sys': 'sys'
        }
    
    def create_session(self, session_id: str = None) -> str:
        """Create a new Python execution session"""
        if not session_id:
            session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Initialize session with common imports
        session = SessionState(
            session_id=session_id,
            variables={},
            dataframes={},
            imports=set(self.global_imports.values()),
            functions={},
            classes={},
            execution_history=[]
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Update session activity timestamp"""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.now(timezone.utc)
    
    def add_execution_result(self, session_id: str, result: ExecutionResult):
        """Add execution result to session history"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.execution_history.append({
                'timestamp': result.timestamp,
                'success': result.success,
                'execution_time': result.execution_time,
                'variables_defined': result.variables_defined,
                'imports_added': result.imports_added,
                'output': result.output,
                'error': result.error
            })
            
            # Update session state
            session.variables.update(result.variables_defined)
            session.imports.update(result.imports_added)
            session.last_activity = datetime.now(timezone.utc)
    
    def cleanup_inactive_sessions(self, max_age_hours: int = 24):
        """Clean up inactive sessions"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
        sessions_to_remove = []
        
        for session_id, session in self.sessions.items():
            if session.last_activity < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.info(f"Cleaned up inactive session: {session_id}")
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session_id,
            'variables_count': len(session.variables),
            'dataframes_count': len(session.dataframes),
            'imports_count': len(session.imports),
            'functions_count': len(session.functions),
            'classes_count': len(session.classes),
            'execution_count': len(session.execution_history),
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'memory_usage': session.memory_usage,
            'is_active': session.is_active
        }

class PythonExecutor:
    """Enhanced Python code executor with session management"""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self.code_analyzer = CodeAnalyzer()
        self.execution_timeout = 60  # seconds
        self.max_output_size = 1024 * 1024  # 1MB
        self.temp_dir = Path(tempfile.gettempdir()) / "ai_notebook_executor"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def execute_code(
        self, 
        code: str, 
        session_id: str = None,
        context: Dict[str, Any] = None
    ) -> ExecutionResult:
        """Execute Python code in a session"""
        start_time = datetime.now(timezone.utc)
        
        # Create or get session
        if not session_id:
            session_id = self.session_manager.create_session()
        else:
            # Ensure session exists
            if not self.session_manager.get_session(session_id):
                self.session_manager.create_session(session_id)
        
        session = self.session_manager.get_session(session_id)
        if not session:
            return ExecutionResult(
                success=False,
                output=None,
                error="Session not found",
                execution_time=0.0,
                variables_defined={},
                variables_used=[],
                imports_added=[],
                functions_defined=[],
                functions_called=[],
                dataframes_created=[],
                plots_generated=[],
                memory_usage=None
            )
        
        try:
            # Analyze code
            code_analysis = self.code_analyzer.analyze_code(code)
            logger.info(f"Code analysis result: {code_analysis}")
            
            # Prepare execution environment
            execution_code = self._prepare_execution_code(code, session, context)
            
            # Execute code
            result = await self._execute_code_safely(execution_code, session_id)
            
            # Process results
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Extract variables and update session
            variables_defined = self._extract_variables_from_output(result.get('output', ''))
            
            execution_result = ExecutionResult(
                success=result.get('success', False),
                output=result.get('output', ''),
                error=result.get('error'),
                execution_time=execution_time,
                variables_defined=variables_defined,
                variables_used=code_analysis['variables_used'],
                imports_added=code_analysis['imports'],
                functions_defined=code_analysis['functions_defined'],
                functions_called=code_analysis['functions_called'],
                dataframes_created=code_analysis['dataframes_created'],
                plots_generated=code_analysis['plots_generated'],
                memory_usage=self._estimate_memory_usage(session)
            )
            
            # Update session
            self.session_manager.add_execution_result(session_id, execution_result)
            self.session_manager.update_session_activity(session_id)
            
            return execution_result
            
        except Exception as e:
            execution_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.error(f"Error executing code: {e}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error traceback: {traceback.format_exc()}")
            
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e),
                execution_time=execution_time,
                variables_defined={},
                variables_used=[],
                imports_added=[],
                functions_defined=[],
                functions_called=[],
                dataframes_created=[],
                plots_generated=[],
                memory_usage=None
            )
    
    def _prepare_execution_code(
        self, 
        code: str, 
        session: SessionState,
        context: Dict[str, Any] = None
    ) -> str:
        """Prepare code for execution with session context"""
        # Build imports section - map aliases back to module names
        import_mapping = {
            'pd': 'pandas',
            'np': 'numpy', 
            'plt': 'matplotlib.pyplot',
            'sns': 'seaborn',
            'datetime': 'datetime',
            'json': 'json',
            're': 're',
            'os': 'os',
            'sys': 'sys'
        }
        
        imports_section = ""
        for import_item in session.imports:
            # Handle full import statements like "import pandas"
            if import_item.startswith("import "):
                imports_section += f"{import_item}\n"
            # Handle aliases like "pd", "np"
            elif import_item in import_mapping:
                module_name = import_mapping[import_item]
                if import_item == module_name:
                    imports_section += f"import {import_item}\n"
                else:
                    imports_section += f"import {module_name} as {import_item}\n"
            else:
                imports_section += f"import {import_item}\n"
        
        # Build variables section
        variables_section = ""
        for var_name, var_value in session.variables.items():
            if isinstance(var_value, str):
                variables_section += f'{var_name} = "{var_value}"\n'
            else:
                variables_section += f'{var_name} = {var_value}\n'
        
        # Build dataframes section
        dataframes_section = ""
        for df_name, df_data in session.dataframes.items():
            dataframes_section += f'{df_name} = {df_data}\n'
        
        # Add context variables
        context_section = ""
        if context:
            for key, value in context.items():
                if isinstance(value, str):
                    context_section += f'{key} = "{value}"\n'
                else:
                    context_section += f'{key} = {value}\n'
        
        # Combine all sections
        full_code = f"""# Session context
{imports_section}

# Session variables
{variables_section}

# Session dataframes
{dataframes_section}

# Context variables
{context_section}

# User code
{code}

# Output session state
print("\\n=== SESSION STATE ===")
print(f"Variables: {list(session.variables.keys())}")
print(f"Dataframes: {list(session.dataframes.keys())}")
print(f"Imports: {list(session.imports)}")
"""
        
        # Debug logging
        logger.info(f"Generated execution code:\n{full_code}")
        
        return full_code
    
    async def _execute_code_safely(self, code: str, session_id: str) -> Dict[str, Any]:
        """Execute code safely with timeout and output limits"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix='.py', 
                delete=False,
                dir=self.temp_dir
            ) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute with timeout
                start_time = datetime.now(timezone.utc)
                
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        sys.executable, temp_file,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=self.execution_timeout
                )
                
                stdout, stderr = await process.communicate()
                end_time = datetime.now(timezone.utc)
                
                execution_time = (end_time - start_time).total_seconds()
                
                # Process output
                output = stdout.decode('utf-8') if stdout else ""
                error = stderr.decode('utf-8') if stderr else ""
                
                # Limit output size
                if len(output) > self.max_output_size:
                    output = output[:self.max_output_size] + "\n... (output truncated)"
                
                if len(error) > self.max_output_size:
                    error = error[:self.max_output_size] + "\n... (error truncated)"
                
                return {
                    'success': process.returncode == 0,
                    'output': output,
                    'error': error if error else None,
                    'execution_time': execution_time,
                    'return_code': process.returncode
                }
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except asyncio.TimeoutError:
            return {
                'success': False,
                'output': None,
                'error': f"Execution timed out after {self.execution_timeout} seconds",
                'execution_time': self.execution_timeout,
                'return_code': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': str(e),
                'execution_time': 0.0,
                'return_code': -1
            }
    
    def _extract_variables_from_output(self, output: str) -> Dict[str, Any]:
        """Extract variable definitions from execution output"""
        variables = {}
        
        # Look for variable assignments in output
        var_pattern = r'(\w+)\s*=\s*([^#\n]+)'
        matches = re.findall(var_pattern, output)
        
        for var_name, var_value in matches:
            try:
                # Try to evaluate the value
                if var_value.strip().isdigit():
                    variables[var_name] = int(var_value.strip())
                elif var_value.strip().replace('.', '').isdigit():
                    variables[var_name] = float(var_value.strip())
                elif var_value.strip().startswith('"') and var_value.strip().endswith('"'):
                    variables[var_name] = var_value.strip().strip('"')
                elif var_value.strip().startswith("'") and var_value.strip().endswith("'"):
                    variables[var_name] = var_value.strip().strip("'")
                else:
                    variables[var_name] = var_value.strip()
            except:
                variables[var_name] = var_value.strip()
        
        return variables
    
    def _estimate_memory_usage(self, session: SessionState) -> float:
        """Estimate memory usage of session"""
        # Simple estimation based on number of variables and dataframes
        base_memory = 1024 * 1024  # 1MB base
        variable_memory = len(session.variables) * 1024  # 1KB per variable
        dataframe_memory = len(session.dataframes) * 1024 * 1024  # 1MB per dataframe
        
        return base_memory + variable_memory + dataframe_memory
    
    def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get current state of a session"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session_id,
            'variables': session.variables,
            'dataframes': session.dataframes,
            'imports': list(session.imports),
            'functions': session.functions,
            'classes': session.classes,
            'execution_history': session.execution_history,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'memory_usage': session.memory_usage,
            'is_active': session.is_active
        }
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all active sessions"""
        return [
            self.session_manager.get_session_summary(session_id)
            for session_id in self.session_manager.sessions.keys()
        ]
    
    def cleanup_sessions(self):
        """Clean up inactive sessions"""
        self.session_manager.cleanup_inactive_sessions()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get status of the Python executor system"""
        active_sessions = [
            s for s in self.session_manager.sessions.values() 
            if s.is_active
        ]
        
        total_memory = sum(s.memory_usage for s in active_sessions)
        
        return {
            'total_sessions': len(self.session_manager.sessions),
            'active_sessions': len(active_sessions),
            'total_memory_usage': total_memory,
            'execution_timeout': self.execution_timeout,
            'max_output_size': self.max_output_size,
            'temp_directory': str(self.temp_dir),
            'ds_libs_available': DS_LIBS_AVAILABLE
        }

# Global instance
python_executor = PythonExecutor()
