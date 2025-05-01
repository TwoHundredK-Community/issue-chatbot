import logging
import chainlit as cl
import sys
import os
from dotenv import load_dotenv
import requests

def log_request_to_server(message: str):
    try:
        r = requests.post("http://localhost:4000/log", json={"message": message})
        if r.status_code == 429:
            return "Usage limit reached. Please come back in 24 hours."
    except Exception as e:
        print("Log server error:", e)

    return None

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

from agents.issue_agent import run_issue_analysis, IssueAgent

# Load environment variables
load_dotenv()
github_token = os.getenv("GITHUB_TOKEN")
issue_agent = IssueAgent(github_token=github_token)


@cl.on_message
async def main(message):
    block_message = log_request_to_server(message)
    if block_message:
        await cl.Message(content=block_message).send()
        return

    # Access the content of the message
    message_content = message.content
    print(f"Received message: {message_content}")
    
    # Accept a GitHub issue link from the user
    if not message_content.startswith("https://github.com/"):
        await cl.Message(content="Please provide a valid GitHub issue link.").send()
        return

    await cl.Message(content="Processing the GitHub issue...").send()
    # Call the agent logic
    try:
        # Extract repository and issue number from the URL
        parts = message_content.rstrip('/').split('/')
        repo_name = f"{parts[-4]}/{parts[-3]}"
        issue_number = parts[-1]

        # Run the issue analysis and stream reasoning steps
        async for step in run_issue_analysis(repo_name, issue_number):
            await cl.Message(content=step).send()

        # Send the final result
        await cl.Message(content="Analysis complete.").send()

    except Exception as e:
        logging.exception(e)
        await cl.Message(content=f"An error occurred: {str(e)}").send()
