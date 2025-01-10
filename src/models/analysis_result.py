# src/models/analysis_result.py
from dataclasses import dataclass
from typing import List
from datetime import datetime

@dataclass
class CodeIssue:
    type: str
    severity: str
    description: str

@dataclass
class SecurityConcern:
    level: str
    description: str

@dataclass
class AnalysisResult:
    commit_sha: str
    quality_score: float
    issues: List[CodeIssue]
    security_concerns: List[SecurityConcern]
    performance_impact: str
    recommendations: List[str]
    analyzed_at: datetime = datetime.now()
    
    def to_dict(self):
        return {
            'commit_sha': self.commit_sha,
            'quality_score': self.quality_score,
            'issues': [vars(issue) for issue in self.issues],
            'security_concerns': [vars(concern) for concern in self.security_concerns],
            'performance_impact': self.performance_impact,
            'recommendations': self.recommendations,
            'analyzed_at': self.analyzed_at.isoformat()
        }