# src/analysis/code_analyzer.py
from typing import List, Dict
from ..models.analysis_result import AnalysisResult, CodeIssue, SecurityConcern
from ..api.github_service import GitHubService
from ..api.openai_service import OpenAIService
from ..utils.logging import get_logger
from .metrics_calculator import MetricsCalculator

logger = get_logger(__name__)

class CodeAnalyzer:
    def __init__(
        self,
        github_service: GitHubService,
        openai_service: OpenAIService,
        metrics_calculator: MetricsCalculator
    ):
        self.github_service = github_service
        self.openai_service = openai_service
        self.metrics_calculator = metrics_calculator

    async def analyze_commit(self, commit_sha: str) -> AnalysisResult:
        """Perform comprehensive analysis of a commit."""
        try:
            # Get commit changes
            changes = await self.github_service.get_commit_changes(commit_sha)
            
            # Parallel analysis
            ai_analysis_task = self.openai_service.analyze_code(changes)
            metrics_task = self.metrics_calculator.calculate_metrics(changes)
            
            # Wait for both analyses to complete
            ai_analysis, metrics = await asyncio.gather(ai_analysis_task, metrics_task)
            
            # Combine AI analysis with metrics
            quality_score = self._calculate_final_score(ai_analysis['quality_score'], metrics)
            
            return AnalysisResult(
                commit_sha=commit_sha,
                quality_score=quality_score,
                issues=[
                    CodeIssue(**issue) for issue in ai_analysis['issues']
                ],
                security_concerns=[
                    SecurityConcern(**concern) 
                    for concern in ai_analysis['security_concerns']
                ],
                performance_impact=ai_analysis['performance_impact'],
                recommendations=ai_analysis['recommendations'] + 
                              self._generate_metric_recommendations(metrics)
            )
            
        except Exception as e:
            logger.error(f"Error analyzing commit {commit_sha}: {str(e)}")
            raise

    def _calculate_final_score(self, ai_score: float, metrics: Dict) -> float:
        """Calculate final quality score combining AI and metrics analysis."""
        # Weights for different components
        weights = {
            'ai_score': 0.5,
            'complexity': 0.2,
            'duplication': 0.15,
            'maintainability': 0.15
        }
        
        metrics_score = (
            (10 - metrics['avg_complexity']) * weights['complexity'] +
            (100 - metrics['duplication_percentage']) * weights['maintainability'] / 100 +
            metrics['maintainability_index'] * weights['maintainability'] / 100
        )
        
        return (ai_score * weights['ai_score'] + metrics_score)

    def _generate_metric_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        if metrics['avg_complexity'] > 15:
            recommendations.append(
                "Consider reducing function complexity in highlighted areas"
            )
        
        if metrics['duplication_percentage'] > 10:
            recommendations.append(
                "Significant code duplication detected. Consider refactoring"
            )
            
        if metrics['maintainability_index'] < 65:
            recommendations.append(
                "Code maintainability is low. Consider simplifying complex parts"
            )
            
        return recommendations

    async def analyze_multiple_commits(
        self, 
        commit_shas: List[str]
    ) -> List[AnalysisResult]:
        """Analyze multiple commits in parallel."""
        tasks = [
            self.analyze_commit(sha) 
            for sha in commit_shas
        ]
        return await asyncio.gather(*tasks)