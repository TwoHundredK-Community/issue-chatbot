import os
import requests
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence  # Updated import
from langchain_openai import OpenAI  # Updated import
from dotenv import load_dotenv

def summarize_issue(repo: str, issue_number: int) -> str:
    """
    Fetches a GitHub issue by repo and issue number, then summarizes it using an LLM.
    Returns a concise summary of the issue.
    """
    # Prepare GitHub API request
    owner_repo = repo  # e.g. "octocat/Hello-World"
    api_url = f"https://api.github.com/repos/{owner_repo}/issues/{issue_number}"
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # Fetch the issue data (title and body)
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()  # raise error if any
    issue_data = response.json()
    title = issue_data.get("title", "")
    body = issue_data.get("body", "")

    # Load the summarization prompt template from file
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "summarize_issue.txt")
    with open(prompt_path, "r") as f:
        prompt_template_str = f.read()
    prompt = PromptTemplate(input_variables=["title", "body"], template=prompt_template_str)

    # Initialize the LLM (OpenAI model) via LangChain
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY. Please set it in your environment variables.")

    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)  # Pass the API key explicitly

    # Use RunnableSequence instead of LLMChain
    chain = RunnableSequence(first=prompt, last=llm)
    
    # Run the chain to get the summary using invoke
    summary = chain.invoke({"title": title, "body": body})
    return summary