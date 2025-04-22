from langchain.tools import BaseTool
from github import Github
import os

class GetIssueTool(BaseTool):
    """Tool to fetch a GitHub issue's title and body given repo and issue number."""
    name: str = "get_issue"
    description: str = (
        "Retrieve a GitHub issue's title and body. "
        "Use this when given a repository name (owner/repo) and an issue number."
    )

    def _run(self, repo_name: str, issue_number: str) -> str:
        # Initialize GitHub client (use token for higher rate limits/private repos)
        token = os.getenv("GITHUB_TOKEN", None)
        github_client = Github(login_or_token=token) if token else Github()
        try:
            # Get the repository and then the specific issue by number
            repo = github_client.get_repo(repo_name)
        except Exception as e:
            return f"Error: Failed to access repository '{repo_name}' - {e}"
        # Convert issue_number to int if possible
        try:
            issue_num = int(issue_number)
        except Exception:
            return "Error: Issue number must be an integer."
        try:
            issue = repo.get_issue(number=issue_num)  # Fetch issue [oai_citation_attribution:3‡pygithub.readthedocs.io](https://pygithub.readthedocs.io/en/latest/examples/Issue.html#get-issue%23:~:text=%253E%253E%253E%2520repo%2520%253D%2520g.get_repo%2528,number%253D874)
        except Exception as e:
            return f"Error: Could not fetch issue #{issue_num} - {e}"
        # Format the output with title and body
        title = issue.title or "(no title)"
        body = issue.body or "(no description)"
        result = f"Issue Title: {title}\nIssue Body:\n{body}"
        return result

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("GetIssueTool does not support async")