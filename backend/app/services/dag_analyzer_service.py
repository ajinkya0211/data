"""
Automatic DAG Analyzer Service
Creates and manages DAGs automatically based on code analysis
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict, deque
import structlog
from datetime import datetime

from app.models.block import Block
from app.services.block_service import BlockService

logger = structlog.get_logger()

class DependencyInfo:
    """Information about a block's dependencies and outputs"""
    
    def __init__(self, block_id: str):
        self.block_id = block_id
        self.imports: Set[str] = set()
        self.variables_used: Set[str] = set()
        self.variables_defined: Set[str] = set()
        self.functions_called: Set[str] = set()
        self.functions_defined: Set[str] = set()
        self.data_files: Set[str] = set()
        self.external_apis: Set[str] = set()
        self.dependencies: Set[str] = set()
        self.outputs: Set[str] = set()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "block_id": self.block_id,
            "imports": list(self.imports),
            "variables_used": list(self.variables_used),
            "variables_defined": list(self.variables_defined),
            "functions_called": list(self.functions_called),
            "functions_defined": list(self.functions_defined),
            "data_files": list(self.data_files),
            "external_apis": list(self.external_apis),
            "dependencies": list(self.dependencies),
            "outputs": list(self.outputs)
        }

class DAGAnalyzerService:
    """Service for automatically analyzing code and creating DAGs"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.block_service = BlockService(db_session)
        
        # Common data science libraries and their typical functions
        self.data_science_libs = {
            'pandas': ['read_csv', 'read_excel', 'DataFrame', 'Series'],
            'numpy': ['array', 'load', 'save', 'genfromtxt'],
            'matplotlib': ['plot', 'scatter', 'hist', 'figure', 'show'],
            'seaborn': ['distplot', 'boxplot', 'heatmap', 'pairplot'],
            'sklearn': ['train_test_split', 'fit', 'predict', 'transform'],
            'scipy': ['stats', 'optimize', 'signal'],
            'plotly': ['Figure', 'scatter', 'bar', 'show']
        }
        
        # Common data file patterns
        self.data_file_patterns = [
            r'\.csv$', r'\.xlsx?$', r'\.json$', r'\.parquet$', r'\.h5$',
            r'\.pkl$', r'\.pickle$', r'\.sql$', r'\.db$'
        ]
    
    async def analyze_project_dependencies(self, project_id: str) -> Dict[str, Any]:
        """
        Analyze all blocks in a project and create DAG automatically
        
        Args:
            project_id: Project to analyze
            
        Returns:
            Dict with DAG information
        """
        try:
            logger.info("Starting project dependency analysis", project_id=project_id)
            
            # Get all blocks in the project
            blocks = await self.block_service.get_project_blocks(project_id, "admin_123")
            
            if not blocks:
                return {
                    "is_valid": False,
                    "error": "No blocks found in project",
                    "dag": None
                }
            
            # Filter executable blocks
            executable_blocks = [b for b in blocks if b.kind.lower() == 'code']
            
            if not executable_blocks:
                return {
                    "is_valid": False,
                    "error": "No executable code blocks found",
                    "dag": None
                }
            
            # Analyze dependencies for each block
            dependency_map = {}
            for block in executable_blocks:
                deps = self.analyze_block_dependencies(block)
                dependency_map[block.id] = deps.to_dict()  # Convert to dict immediately
            
            # Build DAG from dependencies
            dag = self.build_dag_from_dependencies(dependency_map, executable_blocks)
            
            # Validate DAG
            validation = self.validate_dag(dag['nodes'], dag['edges'])
            
            if not validation['is_valid']:
                logger.warning("DAG validation failed", error=validation['error'])
                # Fall back to simple sequential DAG
                dag = self.create_sequential_dag(executable_blocks)
            
            logger.info("Project dependency analysis completed", 
                       project_id=project_id,
                       total_blocks=len(blocks),
                       executable_blocks=len(executable_blocks),
                       dag_nodes=len(dag['nodes']),
                       dag_edges=len(dag['edges']))
            
            return {
                "is_valid": True,
                "error": None,
                "dag": dag,
                "dependency_map": dependency_map  # Now contains dicts, not DependencyInfo objects
            }
            
        except Exception as e:
            logger.error("Project dependency analysis failed", 
                        project_id=project_id, error=str(e))
            return {
                "is_valid": False,
                "error": f"Analysis failed: {str(e)}",
                "dag": None
            }
    
    def analyze_block_dependencies(self, block: Block) -> DependencyInfo:
        """
        Analyze a single block for dependencies
        
        Args:
            block: Block to analyze
            
        Returns:
            DependencyInfo object
        """
        deps = DependencyInfo(block.id)
        
        if not block.content:
            return deps
        
        try:
            # Parse Python code
            tree = ast.parse(block.content)
            
            # Analyze AST nodes
            for node in ast.walk(tree):
                self._analyze_ast_node(node, deps)
            
            # Additional pattern-based analysis
            self._analyze_patterns(block.content, deps)
            
            # Infer outputs based on common patterns
            self._infer_outputs(block.content, deps)
            
        except SyntaxError as e:
            logger.warning("Failed to parse block content", 
                          block_id=block.id, error=str(e))
            # Fall back to pattern-based analysis
            self._analyze_patterns(block.content, deps)
        
        return deps
    
    def _analyze_ast_node(self, node: ast.AST, deps: DependencyInfo):
        """Analyze a single AST node for dependencies"""
        
        if isinstance(node, ast.Import):
            for alias in node.names:
                deps.imports.add(alias.name)
                
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                deps.imports.add(f"{module}.{alias.name}")
                
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                deps.variables_used.add(node.id)
            elif isinstance(node.ctx, ast.Store):
                deps.variables_defined.add(node.id)
                
        elif isinstance(node, ast.Call):
            if hasattr(node.func, 'id'):
                deps.functions_called.add(node.func.id)
            elif hasattr(node.func, 'attr'):
                deps.functions_called.add(node.func.attr)
                
        elif isinstance(node, ast.FunctionDef):
            deps.functions_defined.add(node.name)
            
        elif isinstance(node, ast.ClassDef):
            deps.functions_defined.add(node.name)
    
    def _analyze_patterns(self, content: str, deps: DependencyInfo):
        """Analyze content using regex patterns for additional dependencies"""
        
        # Find data file references
        for pattern in self.data_file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            deps.data_files.update(matches)
        
        # Find common data science operations
        data_ops = [
            r'read_csv\s*\([^)]*\)',
            r'read_excel\s*\([^)]*\)',
            r'DataFrame\s*\([^)]*\)',
            r'plot\s*\([^)]*\)',
            r'show\s*\([^)]*\)',
            r'fit\s*\([^)]*\)',
            r'predict\s*\([^)]*\)'
        ]
        
        for pattern in data_ops:
            if re.search(pattern, content, re.IGNORECASE):
                deps.outputs.add('data_processing')
    
    def _infer_outputs(self, content: str, deps: DependencyInfo):
        """Infer what outputs this block produces"""
        
        # Check for visualization patterns
        viz_patterns = [
            r'plt\.', r'seaborn\.', r'plotly\.', r'\.plot\(', r'\.hist\(',
            r'\.scatter\(', r'\.bar\(', r'\.show\(\)'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in viz_patterns):
            deps.outputs.add('visualization')
        
        # Check for data processing patterns
        process_patterns = [
            r'\.dropna\(\)', r'\.fillna\(', r'\.groupby\(', r'\.merge\(',
            r'\.join\(', r'\.concat\(', r'\.apply\(', r'\.transform\('
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in process_patterns):
            deps.outputs.add('data_processing')
        
        # Check for model training patterns
        model_patterns = [
            r'\.fit\(', r'\.train\(', r'RandomForest', r'LinearRegression',
            r'LogisticRegression', r'KMeans', r'fit_transform'
        ]
        
        if any(re.search(pattern, content, re.IGNORECASE) for pattern in model_patterns):
            deps.outputs.add('model_training')
    
    def build_dag_from_dependencies(self, dependency_map: Dict[str, Any], 
                                  blocks: List[Block]) -> Dict[str, Any]:
        """
        Build DAG from dependency information
        
        Args:
            dependency_map: Map of block_id to DependencyInfo or dict
            blocks: List of blocks
            
        Returns:
            Dict with DAG structure
        """
        # Create node mapping
        node_map = {block.id: block for block in blocks}
        
        # Build dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        
        for block_id, deps in dependency_map.items():
            in_degree[block_id] = 0
        
        # Create edges based on dependencies
        edges = []
        for block_id, deps in dependency_map.items():
            # Handle both DependencyInfo objects and dictionaries
            if hasattr(deps, 'variables_used'):
                variables_used = deps.variables_used
            else:
                variables_used = deps.get('variables_used', [])
            
            for dep_var in variables_used:
                # Find which block defines this variable
                for other_id, other_deps in dependency_map.items():
                    if other_id != block_id:
                        # Handle both DependencyInfo objects and dictionaries
                        if hasattr(other_deps, 'variables_defined'):
                            variables_defined = other_deps.variables_defined
                        else:
                            variables_defined = other_deps.get('variables_defined', [])
                        
                        if dep_var in variables_defined:
                            edges.append((other_id, block_id))
                            graph[other_id].append(block_id)
                            in_degree[block_id] += 1
        
        # Add sequential edges for blocks without dependencies
        for i in range(len(blocks) - 1):
            current_id = blocks[i].id
            next_id = blocks[i + 1].id
            
            # Only add if no dependency exists
            if not any(next_id in graph[dep_id] for dep_id in graph):
                edges.append((current_id, next_id))
                graph[current_id].append(next_id)
                in_degree[next_id] += 1
        
        # Topological sort for execution order
        execution_order = self._topological_sort(graph, in_degree)
        
        return {
            'nodes': [block.id for block in blocks],
            'edges': edges,
            'execution_order': execution_order,
            'graph': dict(graph),
            'in_degree': dict(in_degree)
        }
    
    def _topological_sort(self, graph: Dict[str, List[str]], 
                         in_degree: Dict[str, int]) -> List[str]:
        """Perform topological sort to determine execution order"""
        
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        result = []
        
        while queue:
            node = queue.popleft()
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Add any remaining nodes (should be empty for valid DAG)
        for node, degree in in_degree.items():
            if degree > 0:
                logger.warning("Circular dependency detected", node=node)
        
        return result
    
    def create_sequential_dag(self, blocks: List[Block]) -> Dict[str, Any]:
        """Create a simple sequential DAG as fallback"""
        
        node_ids = [block.id for block in blocks]
        edges = []
        
        for i in range(len(node_ids) - 1):
            edges.append((node_ids[i], node_ids[i + 1]))
        
        return {
            'nodes': node_ids,
            'edges': edges,
            'execution_order': node_ids,
            'graph': {},
            'in_degree': {}
        }
    
    def validate_dag(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        """Validate that the graph is a valid DAG"""
        
        try:
            # Build adjacency list
            graph = defaultdict(list)
            in_degree = defaultdict(int)
            
            for node in nodes:
                in_degree[node] = 0
            
            for from_node, to_node in edges:
                graph[from_node].append(to_node)
                in_degree[to_node] += 1
            
            # Check for cycles using DFS
            visited = set()
            rec_stack = set()
            
            def has_cycle_dfs(node: str) -> bool:
                visited.add(node)
                rec_stack.add(node)
                
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        if has_cycle_dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
                
                rec_stack.remove(node)
                return False
            
            # Check each node for cycles
            for node in nodes:
                if node not in visited:
                    if has_cycle_dfs(node):
                        return {
                            "is_valid": False,
                            "error": "Cycle detected in graph",
                            "cycle_nodes": list(rec_stack)
                        }
            
            return {
                "is_valid": True,
                "error": None,
                "cycle_nodes": []
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "error": f"Validation failed: {str(e)}",
                "cycle_nodes": []
            }
