import os, sys
import requests
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
# Import the custom tools
from tools.github_issues import GetIssueTool
from tools.repo_utils import ListRepoFilesTool

def run_issue_analysis(repo_name: str, issue_number: str):
    """Run the issue analysis agent on a given repo and issue number."""
    # Initialize the language model (GPT-4, or use gpt-3.5-turbo if needed)
    llm = ChatOpenAI(
        model_name="gpt-4",
        temperature=0,
        verbose=False  # LLM itself won't print, we'll use agent verbose
    )
    # Prepare tools
    tools = [GetIssueTool(), ListRepoFilesTool()]
    # Initialize the agent with tools, using the ReAct chat agent type [oai_citation_attribution:13‡promptchap.com](https://promptchap.com/agents/#:~:text=tools%20%3D%20,)
    agent = initialize_agent(
        tools, llm,
        agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
    # Define the task prompt for the agent
    user_prompt = (
        f"You are an AI assistant helping with GitHub issue triaging.\n"
        f"Repository: {repo_name}\nIssue Number: {issue_number}\n\n"
        f"1. Summarize the GitHub issue.\n"
        f"2. Based on the issue description, identify which files in the repository are likely to be relevant for fixing the issue (from the list of repository files).\n"
        f"3. Estimate the effort required to fix the issue (in hours).\n\n"
        f"Provide the list of relevant file paths and the estimated effort in hours as your final answer."
    )
    # Run the agent on the prompt, which will invoke the tools as needed
    result = agent.run(user_prompt)
    return result

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python issue_agent.py <owner/repo> <issue_number>")
        sys.exit(1)
    repo = sys.argv[1]
    issue_num = sys.argv[2]
    output = run_issue_analysis(repo, issue_num)
    print("\n=== Final Output ===")
    print(output)


class IssueAgent:
    def __init__(self, github_token=None):
        """
        Initialize the IssueAgent with an optional GitHub token for authentication.
        """
        self.github_token = github_token

    def process_issue(self, issue_url):
        """
        Process a GitHub issue and generate context-based code.

        Args:
            issue_url (str): The URL of the GitHub issue.

        Returns:
            tuple: A tuple containing reasoning steps (list) and the generated result (str).
        """
        reasoning_steps = []

        # Step 1: Extract repository and issue details from the URL
        reasoning_steps.append("Extracting repository and issue details from the URL...")
        repo_owner, repo_name, issue_number = self._parse_issue_url(issue_url)
        reasoning_steps.append(f"Repository: {repo_owner}/{repo_name}, Issue Number: {issue_number}")

        # Step 2: Fetch issue details from GitHub
        reasoning_steps.append("Fetching issue details from GitHub...")
        issue_details = self._fetch_issue_details(repo_owner, repo_name, issue_number)
        reasoning_steps.append(f"Issue Title: {issue_details['title']}")
        reasoning_steps.append(f"Issue Body: {issue_details['body']}")

        # Step 3: Generate code based on the issue context
        reasoning_steps.append("Generating code based on the issue context...")
        generated_code = self._generate_code(issue_details)
        reasoning_steps.append("Code generation completed.")

        return reasoning_steps, generated_code

    def _parse_issue_url(self, issue_url):
        """
        Parse the GitHub issue URL to extract repository owner, name, and issue number.

        Args:
            issue_url (str): The URL of the GitHub issue.

        Returns:
            tuple: A tuple containing the repository owner, name, and issue number.
        """
        parts = issue_url.rstrip('/').split('/')
        repo_owner = parts[-4]
        repo_name = parts[-3]
        issue_number = parts[-1]
        return repo_owner, repo_name, issue_number

    def _fetch_issue_details(self, repo_owner, repo_name, issue_number):
        """
        Fetch issue details from the GitHub API.

        Args:
            repo_owner (str): The owner of the repository.
            repo_name (str): The name of the repository.
            issue_number (str): The issue number.

        Returns:
            dict: A dictionary containing issue details.
        """
        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}"
        headers = {}
        if self.github_token:
            headers['Authorization'] = f"token {self.github_token}"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _generate_code(self, issue_details):
        """
        Generate code based on the issue details.

        Args:
            issue_details (dict): A dictionary containing issue details.

        Returns:
            str: The generated code as a string.
        """
        # Example: Generate a simple function based on the issue title
        title = issue_details['title']
        body = issue_details['body']
        code = f"""
          # Auto-generated code based on the issue: {title}

          def generated_function():
              \"\"\"
              {body}
              \"\"\"
              pass
          """
        return code.strip()
