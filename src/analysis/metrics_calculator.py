# src/analysis/metrics_calculator.py
from typing import List, Dict
import ast
import re
from ..utils.logging import get_logger
from dataclasses import dataclass
from collections import defaultdict

logger = get_logger(__name__)

@dataclass
class FileMetrics:
    complexity: float
    maintainability: float
    duplication_score: float
    lines_of_code: int
    comment_ratio: float

class MetricsCalculator:
    def __init__(self):
        self.pattern_cache = {}

    async def calculate_metrics(self, changes: List[Dict]) -> Dict:
        """Calculate various code metrics for changes."""
        try:
            file_metrics = []
            
            for change in changes:
                metrics = await self._analyze_file(change)
                file_metrics.append(metrics)
            
            return self._aggregate_metrics(file_metrics)
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

    async def _analyze_file(self, change: Dict) -> FileMetrics:
        """Analyze metrics for a single file."""
        code = change['patch']
        
        return FileMetrics(
            complexity=self._calculate_complexity(code),
            maintainability=self._calculate_maintainability(code),
            duplication_score=self._find_duplications(code),
            lines_of_code=self._count_lines(code),
            comment_ratio=self._calculate_comment_ratio(code)
        )

    def _calculate_complexity(self, code: str) -> float:
        """Calculate cyclomatic complexity."""
        try:
            tree = ast.parse(code)
            complexity = 1  # Base complexity
            
            for node in ast.walk(tree):
                # Increment for control flow statements
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                # Increment for logical operators
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                # Increment for comprehensions
                elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp)):
                    complexity += 1
                    
            return complexity
            
        except SyntaxError:
            # If we can't parse as Python, use simplified metric
            return code.count('if ') + code.count('while ') + code.count('for ')

    def _calculate_maintainability(self, code: str) -> float:
        """Calculate maintainability index."""
        # Simplified implementation of maintainability index
        loc = self._count_lines(code)
        avg_line_length = len(code) / (loc or 1)
        comment_ratio = self._calculate_comment_ratio(code)
        
        # Higher is better, scale 0-100
        maintainability = 100 - (
            (loc * 0.25) +
            (avg_line_length * 0.3) +
            (100 - comment_ratio * 100) * 0.2
        )
        
        return max(0, min(100, maintainability))

    def _find_duplications(self, code: str) -> float:
        """Detect code duplications."""
        MIN_DUPLICATE_LENGTH = 3  # minimum lines to consider as duplication
        lines = code.split('\n')
        total_lines = len(lines)
        
        if total_lines < MIN_DUPLICATE_LENGTH:
            return 0
            
        duplicated_lines = set()
        
        for i in range(len(lines) - MIN_DUPLICATE_LENGTH + 1):
            chunk = '\n'.join(lines[i:i + MIN_DUPLICATE_LENGTH])
            pattern = self.pattern_cache.get(chunk)
            
            if not pattern:
                pattern = re.compile(re.escape(chunk))
                self.pattern_cache[chunk] = pattern
                
            matches = pattern.finditer(code)
            match_count = sum(1 for _ in matches)
            
            if match_count > 1:
                for j in range(i, i + MIN_DUPLICATE_LENGTH):
                    duplicated_lines.add(j)
                    
        duplication_percentage = len(duplicated_lines) / total_lines * 100
        return duplication_percentage

    def _count_lines(self, code: str) -> int:
        """Count non-empty lines of code."""
        return len([line for line in code.split('\n') if line.strip()])

    def _calculate_comment_ratio(self, code: str) -> float:
        """Calculate ratio of comments to code."""
        lines = code.split('\n')
        comment_lines = sum(
            1 for line in lines 
            if line.strip().startswith(('#', '//')) or 
               '/*' in line or 
               '*/' in line
        )
        total_lines = self._count_lines(code)
        return comment_lines / (total_lines or 1)

    def _aggregate_metrics(self, file_metrics: List[FileMetrics]) -> Dict:
        """Aggregate metrics from multiple files."""
        if not file_metrics:
            return {
                'avg_complexity': 0,
                'maintainability_index': 100,
                'duplication_percentage': 0,
                'total_lines': 0,
                'avg_comment_ratio': 0
            }
            
        return {
            'avg_complexity': sum(m.complexity for m in file_metrics) / len(file_metrics),
            'maintainability_index': sum(m.maintainability for m in file_metrics) / len(file_metrics),
            'duplication_percentage': max(m.duplication_score for m in file_metrics),
            'total_lines': sum(m.lines_of_code for m in file_metrics),
            'avg_comment_ratio': sum(m.comment_ratio for m in file_metrics) / len(file_metrics)
        }