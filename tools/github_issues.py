from langchain.tools import BaseTool
from github import Github
import os

class GetIssueTool(BaseTool):
    name: str = "get_issue"
    description: str = "Fetches details of a GitHub issue. Input should be a string in the format 'owner/repo#issue_number'."

    def _run(self, input: str):
        # Parse the input
        try:
            repo, issue_number = input.split("#")
            owner, repo_name = repo.split("/")
        except ValueError:
            raise ValueError("Input must be in the format 'owner/repo#issue_number'.")

        # Initialize PyGithub with the GitHub token
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("Missing GITHUB_TOKEN. Please set it in your environment variables.")
        github = Github(github_token)

        # Fetch the repository and issue
        full_repo_name = f"{owner}/{repo_name}"
        repo = github.get_repo(full_repo_name)
        issue = repo.get_issue(int(issue_number))

        # Return issue details as a dictionary
        return {
            "title": issue.title,
            "body": issue.body,
            "state": issue.state,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "url": issue.html_url,
        }

    async def _arun(self, input: str):
        raise NotImplementedError("GetIssueTool does not support async operations.")