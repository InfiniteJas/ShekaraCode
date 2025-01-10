# src/models/commit.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

@dataclass
class CommitModel:
    sha: str
    message: str
    author: str
    date: datetime
    stats: Dict
    
    @property
    def short_sha(self) -> str:
        """Return first 7 characters of the commit SHA."""
        return self.sha[:7]
    
    @property
    def summary(self) -> str:
        """Return a summary of the commit."""
        return f"{self.short_sha} - {self.message[:50]}"
        
    def to_dict(self) -> Dict:
        """Convert commit to dictionary format."""
        return {
            'sha': self.sha,
            'message': self.message,
            'author': self.author,
            'date': self.date.isoformat(),
            'stats': self.stats
        }