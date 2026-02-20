import os
import importlib
import ast
import re
from typing import Dict, List, Set

class ProjectAnalyzer:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.issues = []
        self.imports = set()
        self.routes = set()
        
    def analyze_project(self) -> Dict:
        """Analyze entire project structure and dependencies"""
        return {
            'circular_deps': self.find_circular_dependencies(),
            'unused_imports': self.find_unused_imports(),
            'route_conflicts': self.find_route_conflicts(),
            'security_issues': self.find_security_issues(),
            'performance_issues': self.find_performance_issues()
        }
    
    def find_circular_dependencies(self) -> List[str]:
        """Find circular import dependencies"""
        dependency_graph = {}
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        try:
                            tree = ast.parse(f.read())
                            imports = [n for n in ast.walk(tree) if isinstance(n, ast.Import)]
                            dependency_graph[path] = [i.names[0].name for i in imports]
                        except Exception as e:
                            self.issues.append(f"Error parsing {path}: {str(e)}")
        return self._detect_cycles(dependency_graph)

    def find_route_conflicts(self) -> List[str]:
        """Find conflicting route definitions"""
        routes = {}
        conflicts = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        # Find route decorators
                        route_patterns = [
                            r"@.*route\('([^']*)'",
                            r'@.*route\("([^"]*)"'
                        ]
                        for pattern in route_patterns:
                            for route in re.findall(pattern, content):
                                if route in routes:
                                    conflicts.append(f"Route conflict: {route} in {path} and {routes[route]}")
                                routes[route] = path
        return conflicts

    def find_unused_imports(self) -> List[str]:
        """Find unused imports in Python files"""
        unused = []
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        try:
                            tree = ast.parse(f.read())
                            imports = {n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)}
                            used = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
                            unused.extend([f"{imp} in {path}" for imp in imports - used])
                        except Exception as e:
                            self.issues.append(f"Error analyzing imports in {path}: {str(e)}")
        return unused

    def find_security_issues(self) -> List[str]:
        """Find potential security issues"""
        issues = []
        patterns = {
            'hardcoded_secret': r'(SECRET|KEY|PASSWORD|TOKEN).*(\'|\")',
            'sql_injection': r'execute\([\'"].*\%.*[\'"]\)',
            'debug_mode': r'debug\s*=\s*True'
        }
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        for issue, pattern in patterns.items():
                            if re.search(pattern, content):
                                issues.append(f"{issue} found in {path}")
        return issues

    def find_performance_issues(self) -> List[str]:
        """Find potential performance issues"""
        issues = []
        patterns = {
            'n_plus_one': r'for.*in.*query\.',
            'large_query': r'SELECT.*\*.*FROM',
            'unclosed_resource': r'open\(.*\)'
        }
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r') as f:
                        content = f.read()
                        for issue, pattern in patterns.items():
                            if re.search(pattern, content):
                                issues.append(f"{issue} found in {path}")
        return issues

    def _detect_cycles(self, graph: Dict) -> List[str]:
        """Helper method to detect cycles in dependency graph"""
        visited = set()
        path = []
        cycles = []

        def visit(vertex):
            if vertex in path:
                cycle = path[path.index(vertex):]
                cycles.append(' -> '.join(cycle))
                return
            if vertex in visited:
                return
            visited.add(vertex)
            path.append(vertex)
            for neighbor in graph.get(vertex, []):
                visit(neighbor)
            path.pop()

        for vertex in graph:
            visit(vertex)
        return cycles