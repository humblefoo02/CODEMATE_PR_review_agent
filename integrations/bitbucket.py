import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)

class BitbucketIntegration:
    def __init__(self, config: dict):
        self.base_url = "https://api.bitbucket.org/2.0"
        self.username = config["bitbucket"]["username"]
        self.password = config["bitbucket"]["password"]
        self.auth = HTTPBasicAuth(self.username, self.password)

    def fetch_pr(self, repo: str, pr_id: int) -> Dict[str, Any]:
        """Fetch pull request data from Bitbucket with comprehensive error handling"""
        try:
            # Get PR details
            pr_url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_id}"
            pr_response = requests.get(pr_url, auth=self.auth)
            
            if pr_response.status_code == 404:
                logger.error(f"PR #{pr_id} not found in repository {repo}")
                raise ValueError(f"PR #{pr_id} not found in repository {repo}")
            elif pr_response.status_code == 403:
                logger.error(f"Access forbidden to repository {repo}. Check credentials.")
                raise PermissionError(f"Access forbidden to repository {repo}. Check credentials.")
            elif pr_response.status_code == 401:
                logger.error("Invalid Bitbucket credentials")
                raise ValueError("Invalid Bitbucket credentials")
            
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            logger.info(f"Fetched PR #{pr_id}: {pr_data.get('title', 'No title')}")
            
            # Get PR diff
            diff_url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_id}/diff"
            diff_response = requests.get(diff_url, auth=self.auth)
            diff_response.raise_for_status()
            
            # Parse diff to extract file information
            diffs = self._parse_diff(diff_response.text)
            
            # Get additional PR metadata
            pr_metadata = {
                "id": pr_data.get("id"),
                "title": pr_data.get("title"),
                "description": pr_data.get("description"),
                "author": pr_data.get("author", {}).get("username", "unknown"),
                "author_id": pr_data.get("author", {}).get("uuid"),
                "author_name": pr_data.get("author", {}).get("display_name"),
                "state": pr_data.get("state"),
                "created_at": pr_data.get("created_on"),
                "updated_at": pr_data.get("updated_on"),
                "merged_at": pr_data.get("merge_commit", {}).get("date") if pr_data.get("state") == "MERGED" else None,
                "source_branch": pr_data.get("source", {}).get("branch", {}).get("name"),
                "target_branch": pr_data.get("destination", {}).get("branch", {}).get("name"),
                "source_commit": pr_data.get("source", {}).get("commit", {}).get("hash"),
                "target_commit": pr_data.get("destination", {}).get("commit", {}).get("hash"),
                "close_source_branch": pr_data.get("close_source_branch", False),
                "merge_strategy": pr_data.get("merge_commit", {}).get("message") if pr_data.get("state") == "MERGED" else None,
                "reviewers": [reviewer.get("username") for reviewer in pr_data.get("reviewers", [])],
                "participants": [participant.get("username") for participant in pr_data.get("participants", [])],
                "commits": pr_data.get("commits", 0),
                "additions": pr_data.get("additions", 0),
                "deletions": pr_data.get("deletions", 0),
                "changed_files": len(diffs),
                "diffs": diffs
            }
            
            logger.info(f"Successfully fetched PR data: {len(diffs)} files")
            return pr_metadata
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bitbucket API error: {e}")
            raise Exception(f"Bitbucket API error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching PR: {e}")
            raise Exception(f"Unexpected error fetching PR: {e}")

    def _parse_diff(self, diff_text: str) -> List[Dict[str, Any]]:
        """Parse diff text to extract file information"""
        diffs = []
        current_file = None
        current_diff = []
        
        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                # Save previous file if exists
                if current_file and current_diff:
                    diffs.append({
                        "file": current_file,
                        "status": "modified",
                        "additions": sum(1 for l in current_diff if l.startswith('+') and not l.startswith('+++')),
                        "deletions": sum(1 for l in current_diff if l.startswith('-') and not l.startswith('---')),
                        "changes": '\n'.join(current_diff),
                        "patch": '\n'.join(current_diff)
                    })
                
                # Start new file
                parts = line.split()
                if len(parts) >= 4:
                    current_file = parts[3].split('/')[-1]  # Get filename from path
                else:
                    current_file = "unknown"
                current_diff = [line]
            else:
                if current_diff is not None:
                    current_diff.append(line)
        
        # Save last file
        if current_file and current_diff:
            diffs.append({
                "file": current_file,
                "status": "modified",
                "additions": sum(1 for l in current_diff if l.startswith('+') and not l.startswith('+++')),
                "deletions": sum(1 for l in current_diff if l.startswith('-') and not l.startswith('---')),
                "changes": '\n'.join(current_diff),
                "patch": '\n'.join(current_diff)
            })
        
        return diffs

    def get_pr_reviews(self, repo: str, pr_id: int) -> List[Dict[str, Any]]:
        """Get existing reviews for a pull request"""
        try:
            # Get PR comments
            comments_url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_id}/comments"
            response = requests.get(comments_url, auth=self.auth)
            response.raise_for_status()
            
            comments_data = response.json()
            review_data = []
            
            for comment in comments_data.get("values", []):
                review_data.append({
                    "id": comment.get("id"),
                    "author": comment.get("user", {}).get("username"),
                    "body": comment.get("content", {}).get("raw", ""),
                    "created_at": comment.get("created_on"),
                    "updated_at": comment.get("updated_on"),
                    "inline": comment.get("inline", False),
                    "file": comment.get("inline", {}).get("path") if comment.get("inline") else None,
                    "line": comment.get("inline", {}).get("to") if comment.get("inline") else None
                })
            
            return review_data
            
        except Exception as e:
            logger.error(f"Error fetching PR reviews: {e}")
            return []

    def create_review_comment(self, repo: str, pr_id: int, file_path: str, line: int, body: str) -> bool:
        """Create a review comment on a specific line"""
        try:
            # Create inline comment
            comment_url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_id}/comments"
            
            comment_data = {
                "content": {
                    "raw": body
                },
                "inline": {
                    "path": file_path,
                    "to": line
                }
            }
            
            response = requests.post(comment_url, json=comment_data, auth=self.auth)
            response.raise_for_status()
            
            logger.info(f"Created review comment on {file_path}:{line}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating review comment: {e}")
            return False

    def get_repo_info(self, repo: str) -> Dict[str, Any]:
        """Get repository information"""
        try:
            repo_url = f"{self.base_url}/repositories/{repo}"
            response = requests.get(repo_url, auth=self.auth)
            response.raise_for_status()
            
            repo_data = response.json()
            return {
                "name": repo_data.get("name"),
                "full_name": repo_data.get("full_name"),
                "description": repo_data.get("description"),
                "language": repo_data.get("language"),
                "stars": repo_data.get("size"),  # Bitbucket doesn't have stars
                "forks": repo_data.get("forks_count", 0),
                "open_issues": repo_data.get("open_issues_count", 0),
                "created_at": repo_data.get("created_on"),
                "updated_at": repo_data.get("updated_on"),
                "default_branch": repo_data.get("mainbranch", {}).get("name"),
                "private": repo_data.get("is_private", False),
                "has_issues": repo_data.get("has_issues", False),
                "has_wiki": repo_data.get("has_wiki", False)
            }
        except Exception as e:
            logger.error(f"Error fetching repository info: {e}")
            return {}

    def get_pr_commits(self, repo: str, pr_id: int) -> List[Dict[str, Any]]:
        """Get commits for a pull request"""
        try:
            commits_url = f"{self.base_url}/repositories/{repo}/pullrequests/{pr_id}/commits"
            response = requests.get(commits_url, auth=self.auth)
            response.raise_for_status()
            
            commits_data = response.json()
            commit_list = []
            
            for commit in commits_data.get("values", []):
                commit_list.append({
                    "id": commit.get("hash"),
                    "short_id": commit.get("hash", "")[:7],
                    "title": commit.get("message", "").split('\n')[0],
                    "message": commit.get("message"),
                    "author_name": commit.get("author", {}).get("user", {}).get("display_name"),
                    "author_email": commit.get("author", {}).get("user", {}).get("email"),
                    "created_at": commit.get("date"),
                    "web_url": commit.get("links", {}).get("html", {}).get("href")
                })
            
            return commit_list
            
        except Exception as e:
            logger.error(f"Error fetching PR commits: {e}")
            return []
