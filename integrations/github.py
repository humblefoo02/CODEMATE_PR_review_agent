from github import Github
from github.GithubException import GithubException
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class GitHubIntegration:
    def __init__(self, config: dict):
        self.token = config["github"]["token"]
        self.client = Github(self.token)
        self.rate_limit_remaining = None

    def fetch_pr(self, repo: str, pr_id: int) -> Dict[str, Any]:
        """Fetch PR data from GitHub with comprehensive error handling"""
        try:
            # Check rate limit
            self._check_rate_limit()
            
            # Get repository
            repository = self.client.get_repo(repo)
            logger.info(f"Fetched repository: {repo}")
            
            # Get pull request
            pr = repository.get_pull(pr_id)
            logger.info(f"Fetched PR #{pr_id}: {pr.title}")
            
            # Get PR files with detailed information
            files = pr.get_files()
            diffs = []
            
            for file in files:
                file_info = {
                    "file": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch,
                    "blob_url": file.blob_url,
                    "raw_url": file.raw_url,
                    "contents_url": file.contents_url
                }
                diffs.append(file_info)
            
            # Get additional PR metadata
            pr_data = {
                "id": pr.number,
                "title": pr.title,
                "body": pr.body,
                "author": pr.user.login,
                "author_id": pr.user.id,
                "author_avatar": pr.user.avatar_url,
                "state": pr.state,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
                "base_branch": pr.base.ref,
                "head_branch": pr.head.ref,
                "base_sha": pr.base.sha,
                "head_sha": pr.head.sha,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "draft": pr.draft,
                "labels": [label.name for label in pr.labels],
                "assignees": [assignee.login for assignee in pr.assignees],
                "reviewers": [reviewer.login for reviewer in pr.requested_reviewers],
                "commits": pr.commits,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "changed_files": pr.changed_files,
                "diffs": diffs
            }
            
            logger.info(f"Successfully fetched PR data: {len(diffs)} files, {pr.additions} additions, {pr.deletions} deletions")
            return pr_data
            
        except GithubException as e:
            if e.status == 404:
                logger.error(f"PR #{pr_id} not found in repository {repo}")
                raise ValueError(f"PR #{pr_id} not found in repository {repo}")
            elif e.status == 403:
                logger.error(f"Access forbidden to repository {repo}. Check token permissions.")
                raise PermissionError(f"Access forbidden to repository {repo}. Check token permissions.")
            elif e.status == 401:
                logger.error("Invalid GitHub token")
                raise ValueError("Invalid GitHub token")
            else:
                logger.error(f"GitHub API error: {e}")
                raise Exception(f"GitHub API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching PR: {e}")
            raise Exception(f"Unexpected error fetching PR: {e}")

    def _check_rate_limit(self):
        """Check GitHub API rate limit"""
        try:
            rate_limit = self.client.get_rate_limit()
            self.rate_limit_remaining = rate_limit.core.remaining
            
            if self.rate_limit_remaining < 10:
                logger.warning(f"Low GitHub API rate limit: {self.rate_limit_remaining} requests remaining")
            
            if self.rate_limit_remaining == 0:
                reset_time = rate_limit.core.reset
                logger.error(f"GitHub API rate limit exceeded. Resets at {reset_time}")
                raise Exception(f"GitHub API rate limit exceeded. Resets at {reset_time}")
                
        except Exception as e:
            logger.warning(f"Could not check rate limit: {e}")

    def get_pr_reviews(self, repo: str, pr_id: int) -> List[Dict[str, Any]]:
        """Get existing reviews for a PR"""
        try:
            repository = self.client.get_repo(repo)
            pr = repository.get_pull(pr_id)
            reviews = pr.get_reviews()
            
            review_data = []
            for review in reviews:
                review_data.append({
                    "id": review.id,
                    "user": review.user.login,
                    "state": review.state,
                    "body": review.body,
                    "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None,
                    "commit_id": review.commit_id
                })
            
            return review_data
            
        except Exception as e:
            logger.error(f"Error fetching PR reviews: {e}")
            return []

    def create_review_comment(self, repo: str, pr_id: int, file_path: str, line: int, body: str) -> bool:
        """Create a review comment on a specific line"""
        try:
            repository = self.client.get_repo(repo)
            pr = repository.get_pull(pr_id)
            
            # Get the latest commit
            commits = pr.get_commits()
            if not commits:
                logger.error("No commits found in PR")
                return False
            
            latest_commit = commits[-1]
            
            # Create the review comment
            pr.create_review_comment(
                body=body,
                commit=latest_commit,
                path=file_path,
                line=line
            )
            
            logger.info(f"Created review comment on {file_path}:{line}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating review comment: {e}")
            return False

    def get_repo_info(self, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            repository = self.client.get_repo(repo)
            return {
                "name": repository.name,
                "full_name": repository.full_name,
                "description": repository.description,
                "language": repository.language,
                "stars": repository.stargazers_count,
                "forks": repository.forks_count,
                "open_issues": repository.open_issues_count,
                "created_at": repository.created_at.isoformat() if repository.created_at else None,
                "updated_at": repository.updated_at.isoformat() if repository.updated_at else None,
                "default_branch": repository.default_branch,
                "private": repository.private
            }
        except Exception as e:
            logger.error(f"Error fetching repository info: {e}")
            return {}
