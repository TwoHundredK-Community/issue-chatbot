import os, sys
from langchain.chat_models import ChatOpenAI
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