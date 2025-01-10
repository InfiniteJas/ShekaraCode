# src/api/github_service.py
from typing import List, Dict, Optional
from github import Github
from github.Repository import Repository
from github.GithubException import GithubException, UnknownObjectException
import asyncio
from functools import lru_cache
from ..models.commit import CommitModel
from ..utils.logging import get_logger
from ..config.settings import Settings

logger = get_logger(__name__)

class GitHubService:
    def __init__(self, settings: Settings):
        logger.info(f"Initializing GitHub service for repo: {settings.repository_name}")
        try:
            self.github = Github(settings.github_token)
            self._repo: Optional[Repository] = None
            self.settings = settings
            # Проверяем валидность токена
            self.github.get_user().login
            logger.info("GitHub authentication successful")
        except Exception as e:
            logger.error(f"Failed to initialize GitHub service: {str(e)}")
            raise
        
    @property
    def repo(self) -> Repository:
        if not self._repo:
            try:
                logger.info(f"Attempting to get repository: {self.settings.repository_name}")
                self._repo = self.github.get_repo(self.settings.repository_name)
                logger.info(f"Successfully connected to repository: {self._repo.full_name}")
            except UnknownObjectException:
                logger.error(f"Repository not found: {self.settings.repository_name}")
                raise
            except GithubException as e:
                logger.error(f"GitHub API error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error accessing repository: {str(e)}")
                raise
        return self._repo
        
    @lru_cache(maxsize=100)
    async def get_commit(self, commit_sha: str) -> CommitModel:
        """Get commit details with caching."""
        try:
            logger.info(f"Fetching commit: {commit_sha}")
            commit = self.repo.get_commit(commit_sha)
            return CommitModel(
                sha=commit.sha,
                message=commit.commit.message,
                author=commit.commit.author.name,
                date=commit.commit.author.date,
                stats=commit.stats
            )
        except Exception as e:
            logger.error(f"Error fetching commit {commit_sha}: {str(e)}")
            raise
            
    async def get_commit_changes(self, commit_sha: str) -> List[Dict]:
        """Get code changes from commit."""
        try:
            commit = self.repo.get_commit(commit_sha)
            changes = []
            
            for file in commit.files:
                if file.patch and file.filename.endswith(
                    ('.py', '.js', '.ts', '.java', '.cpp', '.cs', '.go')
                ):
                    changes.append({
                        'filename': file.filename,
                        'patch': file.patch,
                        'additions': file.additions,
                        'deletions': file.deletions,
                        'status': file.status
                    })
            logger.info(f"Found {len(changes)} files with changes in commit {commit_sha}")
            return changes
        except Exception as e:
            logger.error(f"Error getting commit changes: {str(e)}")
            raise
        
    async def get_recent_commits(self, limit: int = 10) -> List[CommitModel]:
        """Get recent commits."""
        try:
            logger.info(f"Fetching {limit} recent commits")
            commits = []
            for commit in self.repo.get_commits()[:limit]:
                commits.append(
                    CommitModel(
                        sha=commit.sha,
                        message=commit.commit.message,
                        author=commit.commit.author.name,
                        date=commit.commit.author.date,
                        stats=commit.stats
                    )
                )
            logger.info(f"Successfully fetched {len(commits)} commits")
            return commits
        except Exception as e:
            logger.error(f"Error fetching recent commits: {str(e)}")
            raise
        
    async def get_repo_statistics(self) -> Dict:
        """Get repository statistics."""
        try:
            logger.info("Fetching repository statistics")
            repo = self.repo  # This will trigger the property and any potential errors
            stats = {
                'name': repo.name,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'open_issues': repo.open_issues_count,
                'language': repo.language,
                'created_at': repo.created_at
            }
            logger.info("Successfully fetched repository statistics")
            return stats
        except Exception as e:
            logger.error(f"Error fetching repository statistics: {str(e)}")
            raise