import gitlab
from gitlab.exceptions import GitlabError
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class GitLabIntegration:
    def __init__(self, config: dict):
        self.url = config["gitlab"]["url"]
        self.token = config["gitlab"]["token"]
        self.client = gitlab.Gitlab(self.url, private_token=self.token)
        self.client.auth()

    def fetch_pr(self, repo: str, pr_id: int) -> Dict[str, Any]:
        """Fetch merge request data from GitLab with comprehensive error handling"""
        try:
            # Get project
            project = self.client.projects.get(repo)
            logger.info(f"Fetched project: {repo}")
            
            # Get merge request
            mr = project.mergerequests.get(pr_id)
            logger.info(f"Fetched MR !{pr_id}: {mr.title}")
            
            # Get changes
            changes = mr.changes()["changes"]
            diffs = []
            
            for change in changes:
                file_info = {
                    "file": change.get("new_path", change.get("old_path", "unknown")),
                    "status": change.get("new_file", False) and "added" or 
                             change.get("deleted_file", False) and "deleted" or "modified",
                    "additions": change.get("diff", "").count("\n+") - 1,  # Approximate
                    "deletions": change.get("diff", "").count("\n-") - 1,  # Approximate
                    "changes": change.get("diff", ""),
                    "patch": change.get("diff", ""),
                    "old_path": change.get("old_path"),
                    "new_path": change.get("new_path")
                }
                diffs.append(file_info)
            
            # Get additional MR metadata
            mr_data = {
                "id": mr.iid,
                "title": mr.title,
                "description": mr.description,
                "author": mr.author["username"],
                "author_id": mr.author["id"],
                "author_name": mr.author["name"],
                "author_email": mr.author["email"],
                "state": mr.state,
                "created_at": mr.created_at,
                "updated_at": mr.updated_at,
                "merged_at": mr.merged_at,
                "source_branch": mr.source_branch,
                "target_branch": mr.target_branch,
                "source_project_id": mr.source_project_id,
                "target_project_id": mr.target_project_id,
                "work_in_progress": mr.work_in_progress,
                "merge_status": mr.merge_status,
                "labels": mr.labels,
                "assignees": [assignee["username"] for assignee in mr.assignees],
                "reviewers": [reviewer["username"] for reviewer in mr.reviewers],
                "commits": len(mr.commits()),
                "additions": sum(change.get("diff", "").count("\n+") - 1 for change in changes),
                "deletions": sum(change.get("diff", "").count("\n-") - 1 for change in changes),
                "changed_files": len(changes),
                "diffs": diffs
            }
            
            logger.info(f"Successfully fetched MR data: {len(diffs)} files")
            return mr_data
            
        except GitlabError as e:
            if e.response_code == 404:
                logger.error(f"MR !{pr_id} not found in project {repo}")
                raise ValueError(f"MR !{pr_id} not found in project {repo}")
            elif e.response_code == 403:
                logger.error(f"Access forbidden to project {repo}. Check token permissions.")
                raise PermissionError(f"Access forbidden to project {repo}. Check token permissions.")
            elif e.response_code == 401:
                logger.error("Invalid GitLab token")
                raise ValueError("Invalid GitLab token")
            else:
                logger.error(f"GitLab API error: {e}")
                raise Exception(f"GitLab API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching MR: {e}")
            raise Exception(f"Unexpected error fetching MR: {e}")

    def get_mr_reviews(self, repo: str, mr_id: int) -> List[Dict[str, Any]]:
        """Get existing reviews for a merge request"""
        try:
            project = self.client.projects.get(repo)
            mr = project.mergerequests.get(mr_id)
            
            # Get discussions (reviews in GitLab)
            discussions = mr.discussions.list()
            
            review_data = []
            for discussion in discussions:
                for note in discussion.attributes["notes"]:
                    review_data.append({
                        "id": note["id"],
                        "author": note["author"]["username"],
                        "body": note["body"],
                        "created_at": note["created_at"],
                        "resolved": note.get("resolved", False),
                        "system": note.get("system", False)
                    })
            
            return review_data
            
        except Exception as e:
            logger.error(f"Error fetching MR reviews: {e}")
            return []

    def create_review_comment(self, repo: str, mr_id: int, file_path: str, line: int, body: str) -> bool:
        """Create a review comment on a specific line"""
        try:
            project = self.client.projects.get(repo)
            mr = project.mergerequests.get(mr_id)
            
            # Create a discussion on the MR
            discussion = mr.discussions.create({
                'body': f"**{file_path}:{line}**\n\n{body}"
            })
            
            logger.info(f"Created review comment on {file_path}:{line}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating review comment: {e}")
            return False

    def get_project_info(self, repo: str) -> Dict[str, Any]:
        """Get project information"""
        try:
            project = self.client.projects.get(repo)
            return {
                "name": project.name,
                "path": project.path,
                "description": project.description,
                "language": project.language,
                "stars": project.star_count,
                "forks": project.forks_count,
                "open_issues": project.open_issues_count,
                "created_at": project.created_at,
                "updated_at": project.last_activity_at,
                "default_branch": project.default_branch,
                "visibility": project.visibility,
                "archived": project.archived
            }
        except Exception as e:
            logger.error(f"Error fetching project info: {e}")
            return {}

    def get_mr_commits(self, repo: str, mr_id: int) -> List[Dict[str, Any]]:
        """Get commits for a merge request"""
        try:
            project = self.client.projects.get(repo)
            mr = project.mergerequests.get(mr_id)
            commits = mr.commits()
            
            commit_data = []
            for commit in commits:
                commit_data.append({
                    "id": commit.id,
                    "short_id": commit.short_id,
                    "title": commit.title,
                    "message": commit.message,
                    "author_name": commit.author_name,
                    "author_email": commit.author_email,
                    "created_at": commit.created_at,
                    "web_url": commit.web_url
                })
            
            return commit_data
            
        except Exception as e:
            logger.error(f"Error fetching MR commits: {e}")
            return []
