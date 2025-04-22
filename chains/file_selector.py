import os
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence  # Updated import
from langchain_openai import OpenAI  # Updated import
from dotenv import load_dotenv
from tools.repo_utils import clone_repository, gather_file_list

def predict_files_for_issue(issue_summary: str, repo: str, clone_dir: str = "repo_clone") -> list:
    """
    Given an issue summary and a GitHub repository name (owner/repo),
    this function clones the repo (if needed), gathers the file structure, 
    and uses an LLM to predict which files might need changes to resolve the issue.
    Returns the LLM's output (a list of file paths likely involved).
    """
    # Ensure repository is cloned to the specified directory
    clone_repository(repo, clone_dir)

    # Get the list of files in the repository
    file_list = gather_file_list(clone_dir)
    if not file_list:
        raise RuntimeError("Repository file list is empty or repository clone failed.")

    # Load the file selection prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "select_files.txt")
    with open(prompt_path, "r") as f:
        prompt_template_str = f.read()
    prompt = PromptTemplate(input_variables=["summary", "file_list"], template=prompt_template_str)

    # Prepare the file list as a string
    file_list_str = "\n".join(file_list)

    # Initialize the LLM (OpenAI model) via LangChain
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("Missing OPENAI_API_KEY. Please set it in your environment variables.")

    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)  # Pass the API key explicitly

    # Use RunnableSequence instead of LLMChain
    chain = RunnableSequence(first=prompt, last=llm)

    # Run the chain to get the predicted files using invoke
    result = chain.invoke({"summary": issue_summary, "file_list": file_list_str})
    return result.splitlines()