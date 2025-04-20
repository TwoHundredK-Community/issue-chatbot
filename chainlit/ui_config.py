import chainlit as cl

cl.set_config(
    title="GitHub Issue Bot",
    description="Interact with GitHub issues, analyze them, and generate solutions.",
    theme="light",  # Options: 'light', 'dark'
    input_placeholder="Paste a GitHub issue link here...",
    default_message="Welcome to the GitHub Issue Bot! Paste a GitHub issue link to get started."
)
