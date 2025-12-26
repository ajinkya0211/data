"""
DAG (Directed Acyclic Graph) System for AI Notebook
Tracks dependencies, imports, variables, and execution order
"""

import networkx as nx
import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

class DependencyType(Enum):
    """Types of dependencies between blocks"""
    DATA_FLOW = "data_flow"
    IMPORT_DEPENDENCY = "import_dependency"
    VARIABLE_DEPENDENCY = "variable_dependency"
    EXECUTION_ORDER = "execution_order"
    FUNCTION_DEPENDENCY = "function_dependency"

class BlockStatus(Enum):
    """Status of a block"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

@dataclass
class Dependency:
    """Represents a dependency between blocks"""
    id: str
    source_block_id: str
    target_block_id: str
    dependency_type: DependencyType
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class BlockNode:
    """Represents a block in the DAG"""
    id: str
    block_type: str
    content: str
    position: Dict[str, int]
    status: BlockStatus = BlockStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    imports: Set[str] = field(default_factory=set)
    variables_defined: Set[str] = field(default_factory=set)
    variables_used: Set[str] = field(default_factory=set)
    functions_defined: Set[str] = field(default_factory=set)
    functions_called: Set[str] = field(default_factory=set)
    execution_order: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

# Import the enhanced CodeAnalyzer from python_executor
from python_executor import CodeAnalyzer

class DAGManager:
    """Manages the DAG structure and execution order"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.blocks: Dict[str, BlockNode] = {}
        self.dependencies: Dict[str, Dependency] = {}
        self.code_analyzer = CodeAnalyzer()
        self.execution_order: List[str] = []
        self.import_registry: Dict[str, Set[str]] = {}
        self.variable_registry: Dict[str, Set[str]] = {}
        self.function_registry: Dict[str, Set[str]] = {}
        self.library_registry: Dict[str, Set[str]] = {}
        self.file_registry: Dict[str, Set[str]] = {}
        self.class_registry: Dict[str, Set[str]] = {}
    
    def add_block(self, block_data: Dict[str, Any]) -> str:
        """Add a new block to the DAG"""
        block_id = block_data.get('id', str(uuid.uuid4()))
        
        # Analyze the code
        code_analysis = self.code_analyzer.analyze_code(block_data['content'])
        
        # Create block node
        block_node = BlockNode(
            id=block_id,
            block_type=block_data.get('type', 'code'),
            content=block_data['content'],
            position=block_data.get('position', {'x': 0, 'y': 0}),
            imports=code_analysis['imports'],
            variables_defined=code_analysis['variables_defined'],
            variables_used=code_analysis['variables_used'],
            functions_defined=code_analysis['functions_defined'],
            functions_called=code_analysis['functions_called']
        )
        
        # Add to collections
        self.blocks[block_id] = block_node
        self.graph.add_node(block_id, **block_data)
        
        # Update registries
        self._update_registries(block_id, code_analysis)
        
        # Analyze dependencies
        self._analyze_dependencies(block_id)
        
        # Update execution order
        self._update_execution_order()
        
        return block_id
    
    def update_block(self, block_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing block"""
        if block_id not in self.blocks:
            return False
        
        block = self.blocks[block_id]
        
        # Update content if changed
        if 'content' in updates and updates['content'] != block.content:
            # Remove old dependencies
            self._remove_block_dependencies(block_id)
            
            # Update content and re-analyze
            block.content = updates['content']
            code_analysis = self.code_analyzer.analyze_code(block.content)
            
            # Update block properties
            block.imports = code_analysis['imports']
            block.variables_defined = code_analysis['variables_defined']
            block.variables_used = code_analysis['variables_used']
            block.functions_defined = code_analysis['functions_defined']
            block.functions_called = code_analysis['functions_called']
            block.updated_at = datetime.now(timezone.utc)
            
            # Update registries
            self._update_registries(block_id, code_analysis)
            
            # Re-analyze dependencies
            self._analyze_dependencies(block_id)
            
            # Update execution order
            self._update_execution_order()
        
        # Update other properties
        for key, value in updates.items():
            if hasattr(block, key) and key != 'content':
                setattr(block, key, value)
        
        return True
    
    def remove_block(self, block_id: str) -> bool:
        """Remove a block from the DAG"""
        if block_id not in self.blocks:
            return False
        
        # Remove dependencies
        self._remove_block_dependencies(block_id)
        
        # Remove from graph
        self.graph.remove_node(block_id)
        
        # Remove from blocks
        del self.blocks[block_id]
        
        # Update execution order
        self._update_execution_order()
        
        return True
    
    def _update_registries(self, block_id: str, analysis: Dict[str, Any]):
        """Update comprehensive registries for enhanced dependency tracking"""
        # Update import registry
        for imp in analysis.get('imports', []):
            if imp not in self.import_registry:
                self.import_registry[imp] = set()
            self.import_registry[imp].add(block_id)
        
        # Update variable registry
        for var in analysis.get('variables_defined', []):
            if var not in self.variable_registry:
                self.variable_registry[var] = set()
            self.variable_registry[var].add(block_id)
        
        # Update function registry
        for func in analysis.get('functions_defined', []):
            if func not in self.function_registry:
                self.function_registry[func] = set()
            self.function_registry[func].add(block_id)
        
        # Update library registry
        for lib in analysis.get('libraries_required', []):
            if lib not in self.library_registry:
                self.library_registry[lib] = set()
            self.library_registry[lib].add(block_id)
        
        # Update file registry
        for file_path in analysis.get('files_read', []):
            if file_path not in self.file_registry:
                self.file_registry[file_path] = set()
            self.file_registry[file_path].add(block_id)
        
        # Update class registry
        for class_name in analysis.get('classes_defined', []):
            if class_name not in self.class_registry:
                self.class_registry[class_name] = set()
            self.class_registry[class_name].add(block_id)
    
    def _remove_block_dependencies(self, block_id: str):
        """Remove all dependencies for a block"""
        # Remove from all registries
        for registry in [self.import_registry, self.variable_registry, self.function_registry, 
                        self.library_registry, self.file_registry, self.class_registry]:
            for key in list(registry.keys()):
                if block_id in registry[key]:
                    registry[key].remove(block_id)
                    if not registry[key]:
                        del registry[key]
        
        # Remove dependency objects
        deps_to_remove = []
        for dep_id, dep in self.dependencies.items():
            if dep.source_block_id == block_id or dep.target_block_id == block_id:
                deps_to_remove.append(dep_id)
        
        for dep_id in deps_to_remove:
            del self.dependencies[dep_id]
    
    def _analyze_dependencies(self, block_id: str):
        """Enhanced dependency analysis using comprehensive code analysis"""
        block = self.blocks[block_id]
        
        # Use enhanced code analyzer for better dependency detection
        code_analysis = self.code_analyzer.analyze_code(block.content)
        
        # Update block with enhanced analysis
        block.imports = set(code_analysis.get('imports', []))
        block.variables_defined = set(code_analysis.get('variables_defined', []))
        block.variables_used = set(code_analysis.get('variables_used', []))
        block.functions_defined = set(code_analysis.get('functions_defined', []))
        block.functions_called = set(code_analysis.get('functions_called', []))
        
        # Track library dependencies
        libraries_required = set(code_analysis.get('libraries_required', []))
        files_read = set(code_analysis.get('files_read', []))
        
        # Variable dependencies
        for var_name in block.variables_used:
            if var_name in self.variable_registry:
                for source_block_id in self.variable_registry[var_name]:
                    if source_block_id != block_id:
                        self._add_dependency(
                            source_block_id, 
                            block_id, 
                            DependencyType.VARIABLE_DEPENDENCY,
                            f"Variable '{var_name}' defined in {source_block_id}",
                            {'variable_name': var_name, 'dependency_strength': 'strong'}
                        )
        
        # Function dependencies
        for func_name in block.functions_called:
            if func_name in self.function_registry:
                for source_block_id in self.function_registry[func_name]:
                    if source_block_id != block_id:
                        self._add_dependency(
                            source_block_id,
                            block_id,
                            DependencyType.FUNCTION_DEPENDENCY,
                            f"Function '{func_name}' defined in {source_block_id}",
                            {'function_name': func_name, 'dependency_strength': 'strong'}
                        )
        
        # Import dependencies (blocks that provide required libraries)
        for lib in libraries_required:
            if lib in self.library_registry:
                for source_block_id in self.library_registry[lib]:
                    if source_block_id != block_id:
                        self._add_dependency(
                            source_block_id,
                            block_id,
                            DependencyType.IMPORT_DEPENDENCY,
                            f"Library '{lib}' provided by {source_block_id}",
                            {'library': lib, 'dependency_strength': 'medium'}
                        )
        
        # File dependencies
        for file_path in files_read:
            if file_path in self.file_registry:
                for source_block_id in self.file_registry[file_path]:
                    if source_block_id != block_id:
                        self._add_dependency(
                            source_block_id,
                            block_id,
                            DependencyType.DATA_FLOW,
                            f"File '{file_path}' processed by {source_block_id}",
                            {'file_path': file_path, 'dependency_strength': 'strong'}
                        )
        
        # Add execution order dependency based on position
        self._add_position_dependencies(block_id)
        
        # Update registries
        self._update_registries(block_id, code_analysis)
    
    def _add_position_dependencies(self, block_id: str):
        """Add dependencies based on block positions"""
        block = self.blocks[block_id]
        
        for other_id, other_block in self.blocks.items():
            if other_id == block_id:
                continue
            
            # Left to right dependency
            if (other_block.position['y'] == block.position['y'] and 
                other_block.position['x'] < block.position['x']):
                self._add_dependency(
                    other_id,
                    block_id,
                    DependencyType.EXECUTION_ORDER,
                    f"Position-based dependency: {other_id} -> {block_id}"
                )
            
            # Top to bottom dependency
            elif (other_block.position['x'] == block.position['x'] and 
                  other_block.position['y'] < block.position['y']):
                self._add_dependency(
                    other_id,
                    block_id,
                    DependencyType.EXECUTION_ORDER,
                    f"Position-based dependency: {other_id} -> {block_id}"
                )
    
    def _add_dependency(self, source_id: str, target_id: str, dep_type: DependencyType, description: str, metadata: Dict[str, Any] = None):
        """Add a dependency between blocks with enhanced metadata"""
        dep_id = str(uuid.uuid4())
        
        if metadata is None:
            metadata = {}
        
        dependency = Dependency(
            id=dep_id,
            source_block_id=source_id,
            target_block_id=target_id,
            dependency_type=dep_type,
            description=description,
            metadata=metadata
        )
        
        self.dependencies[dep_id] = dependency
        
        # Add to graph
        self.graph.add_edge(source_id, target_id, dependency=dependency)
        
        # Update block references
        if source_id in self.blocks:
            self.blocks[source_id].dependents.append(target_id)
        if target_id in self.blocks:
            self.blocks[target_id].dependencies.append(source_id)
    
    def _update_execution_order(self):
        """Update the execution order based on dependencies"""
        try:
            # Use topological sort to determine execution order
            if nx.is_directed_acyclic_graph(self.graph):
                self.execution_order = list(nx.topological_sort(self.graph))
            else:
                # Handle cycles by using position-based ordering
                self.execution_order = self._get_position_based_order()
            
            # Update execution order in blocks
            for i, block_id in enumerate(self.execution_order):
                if block_id in self.blocks:
                    self.blocks[block_id].execution_order = i
                    
        except Exception as e:
            logger.error(f"Error updating execution order: {e}")
            # Fallback to position-based ordering
            self.execution_order = self._get_position_based_order()
    
    def _get_position_based_order(self) -> List[str]:
        """Get execution order based on block positions"""
        sorted_blocks = sorted(
            self.blocks.values(),
            key=lambda b: (b.position['y'], b.position['x'])
        )
        return [block.id for block in sorted_blocks]
    
    def get_execution_plan(self) -> List[Dict[str, Any]]:
        """Get the execution plan with detailed information"""
        plan = []
        
        for i, block_id in enumerate(self.execution_order):
            if block_id in self.blocks:
                block = self.blocks[block_id]
                
                # Get dependencies for this block
                dependencies = [
                    {
                        'block_id': dep_id,
                        'type': self.dependencies.get(dep_id, {}).get('dependency_type', 'unknown'),
                        'description': self.dependencies.get(dep_id, {}).get('description', '')
                    }
                    for dep_id in block.dependencies
                ]
                
                plan.append({
                    'order': i,
                    'block_id': block_id,
                    'block_type': block.block_type,
                    'status': block.status.value if hasattr(block.status, 'value') else str(block.status),
                    'dependencies': dependencies,
                    'dependencies_count': len(dependencies),
                    'position': block.position,
                    'content_preview': block.content[:100] + "..." if len(block.content) > 100 else block.content
                })
        
        return plan
    
    def validate_workflow(self) -> Dict[str, Any]:
        """Validate the workflow structure"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'cycles_detected': False,
            'orphaned_blocks': [],
            'dependency_issues': []
        }
        
        # Check for cycles
        try:
            cycles = list(nx.simple_cycles(self.graph))
            if cycles:
                validation['is_valid'] = False
                validation['cycles_detected'] = True
                validation['errors'].append(f"Circular dependencies detected: {cycles}")
        except:
            pass
        
        # Check for orphaned blocks
        orphaned = [bid for bid in self.blocks.keys() if bid not in self.execution_order]
        if orphaned:
            validation['warnings'].append(f"Orphaned blocks found: {orphaned}")
            validation['orphaned_blocks'] = orphaned
        
        # Check dependency issues
        for block_id, block in self.blocks.items():
            if block.dependencies and not all(dep in self.blocks for dep in block.dependencies):
                validation['warnings'].append(f"Block {block_id} has invalid dependencies")
                validation['dependency_issues'].append(block_id)
        
        return validation
    
    def get_block_dependencies(self, block_id: str) -> Dict[str, Any]:
        """Get detailed dependency information for a block"""
        if block_id not in self.blocks:
            return {}
        
        block = self.blocks[block_id]
        
        return {
            'block_id': block_id,
            'dependencies': [
                {
                    'block_id': dep_id,
                    'type': self.dependencies.get(dep_id, {}).get('dependency_type', 'unknown'),
                    'description': self.dependencies.get(dep_id, {}).get('description', ''),
                    'block_info': {
                        'type': self.blocks.get(dep_id, {}).get('block_type', 'unknown'),
                        'content_preview': self.blocks.get(dep_id, {}).get('content', '')[:100]
                    }
                }
                for dep_id in block.dependencies
            ],
            'dependents': [
                {
                    'block_id': dep_id,
                    'type': self.dependencies.get(dep_id, {}).get('dependency_type', 'unknown'),
                    'description': self.dependencies.get(dep_id, {}).get('description', ''),
                    'block_info': {
                        'type': self.blocks.get(dep_id, {}).get('block_type', 'unknown'),
                        'content_preview': self.blocks.get(dep_id, {}).get('content', '')[:100]
                    }
                }
                for dep_id in block.dependents
            ],
            'execution_order': block.execution_order,
            'status': block.status.value if hasattr(block.status, 'value') else str(block.status)
        }
    
    def get_dag_visualization_data(self) -> Dict[str, Any]:
        """Get enhanced data for DAG visualization with comprehensive dependency information"""
        nodes = []
        edges = []
        
        for block_id, block in self.blocks.items():
            # Get enhanced analysis for the block
            code_analysis = self.code_analyzer.analyze_code(block.content)
            
            nodes.append({
                'id': block_id,
                'type': block.block_type,
                'position': block.position,
                'status': block.status.value if hasattr(block.status, 'value') else str(block.status),
                'execution_order': block.execution_order,
                'content_preview': block.content[:100] + "..." if len(block.content) > 100 else block.content,
                'dependencies_count': len(block.dependencies),
                'dependents_count': len(block.dependents),
                # Enhanced analysis data
                'imports': list(block.imports),
                'variables_defined': list(block.variables_defined),
                'variables_used': list(block.variables_used),
                'functions_defined': list(block.functions_defined),
                'functions_called': list(block.functions_called),
                'libraries_required': code_analysis.get('libraries_required', []),
                'files_read': code_analysis.get('files_read', []),
                'files_written': code_analysis.get('files_written', []),
                'estimated_complexity': code_analysis.get('estimated_complexity', 0),
                'execution_requirements': code_analysis.get('execution_requirements', [])
            })
        
        for dep_id, dependency in self.dependencies.items():
            edges.append({
                'id': dep_id,
                'source': dependency.source_block_id,
                'target': dependency.target_block_id,
                'type': dependency.dependency_type.value,
                'description': dependency.description,
                'metadata': dependency.metadata,
                'dependency_strength': dependency.metadata.get('dependency_strength', 'medium')
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'execution_order': self.execution_order,
            'validation': self.validate_workflow(),
            'dependency_summary': {
                'total_variable_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.VARIABLE_DEPENDENCY]),
                'total_function_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.FUNCTION_DEPENDENCY]),
                'total_import_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.IMPORT_DEPENDENCY]),
                'total_data_flow_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.DATA_FLOW]),
                'total_execution_order_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.EXECUTION_ORDER])
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the enhanced DAG system"""
        return {
            'total_blocks': len(self.blocks),
            'total_dependencies': len(self.dependencies),
            'execution_order_length': len(self.execution_order),
            'graph_nodes': self.graph.number_of_nodes(),
            'graph_edges': self.graph.number_of_edges(),
            'is_dag': nx.is_directed_acyclic_graph(self.graph),
            'has_cycles': len(list(nx.simple_cycles(self.graph))) > 0,
            # Registry information
            'imports_registered': len(self.import_registry),
            'variables_registered': len(self.variable_registry),
            'functions_registered': len(self.function_registry),
            'libraries_registered': len(self.library_registry),
            'files_registered': len(self.file_registry),
            'classes_registered': len(self.class_registry),
            # Dependency type breakdown
            'dependency_types': {
                'variable_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.VARIABLE_DEPENDENCY]),
                'function_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.FUNCTION_DEPENDENCY]),
                'import_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.IMPORT_DEPENDENCY]),
                'data_flow_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.DATA_FLOW]),
                'execution_order_dependencies': len([d for d in self.dependencies.values() if d.dependency_type == DependencyType.EXECUTION_ORDER])
            },
            'validation': self.validate_workflow()
        }
