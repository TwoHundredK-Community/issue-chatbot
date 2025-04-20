import chainlit as cl
from agents.issue_agent import IssueAgent

# Initialize the agent
issue_agent = IssueAgent()

@cl.on_message
async def main(message: str):
    # Accept a GitHub issue link from the user
    if not message.startswith("https://github.com/"):
        await cl.Message(content="Please provide a valid GitHub issue link.").send()
        return

    await cl.Message(content="Processing the GitHub issue...").send()

    # Call the agent logic
    try:
        reasoning_steps, result = issue_agent.process_issue(message)

        # Stream reasoning steps
        for step in reasoning_steps:
            await cl.Message(content=step).send()

        # Send the final result
        await cl.Message(content=f"Result: {result}").send()

    except Exception as e:
        await cl.Message(content=f"An error occurred: {str(e)}").send()
