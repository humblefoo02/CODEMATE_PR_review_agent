from integrations.github import GitHubIntegration
from integrations.gitlab import GitLabIntegration
from integrations.bitbucket import BitbucketIntegration

class PRFetcher:
    def __init__(self, server: str, config: dict):
        self.server = server
        self.config = config

        if server == "github":
            self.client = GitHubIntegration(config)
        elif server == "gitlab":
            self.client = GitLabIntegration(config)
        elif server == "bitbucket":
            self.client = BitbucketIntegration(config)
        else:
            raise ValueError("Unsupported server")

    def get_pr(self, repo: str, pr_id: int):
        return self.client.fetch_pr(repo, pr_id)
