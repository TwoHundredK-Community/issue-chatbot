# Issue Bot

A chatbot that interacts with GitHub issues, analyzes them, and generates pull requests to solve the issues. Built using LangChain, Chainlit, and LLMs.

## Features
- Fetch GitHub issues and analyze them.
- Ask and answer questions about the repository and issues.
- Predict relevant files and generate code solutions.
- Automatically create pull requests with the generated solutions.

## File Structure
```
issue-bot/
├── main.py                      # Entry point: fallback or testing entry
├── config.py                    # API keys, repo settings, model configs
├── requirements.txt             # Dependencies (including chainlit, langchain, etc.)
├── README.md                    # Project overview & setup instructions
├── .env                         # Secrets (OpenAI key, GitHub token)

├── chainlit_app/
│   ├── __init__.py
│   ├── app.py                   # Chainlit entry point (main chatbot logic)
│   └── ui_config.py             # Optional: configure chatbot UI behavior

├── agents/
│   └── issue_agent.py           # LangChain agent logic (registered in Chainlit)

├── chains/
│   ├── issue_understanding.py   # LLMChain: analyze & ask about issue
│   ├── file_selector.py         # LLMChain: predict relevant files
│   └── code_generator.py        # LLMChain: generate code solution

├── tools/
│   ├── github_issues.py         # Fetch issue metadata from GitHub
│   ├── github_pr.py             # Tool to open pull requests
│   ├── repo_utils.py            # Clone, read files, write changes
│   └── test_runner.py           # Run tests or validate output

├── prompts/
│   ├── summarize_issue.txt      # Prompt for understanding
│   ├── select_files.txt         # Prompt for file path prediction
│   └── generate_patch.txt       # Prompt for code gen

├── data/
│   └── repo/                    # Local copy of GitHub repo
```

## Setup Instructions
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd issue-bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Create a `.env` file with the following:
     ```
     OPENAI_API_KEY=<your-openai-api-key>
     GITHUB_TOKEN=<your-github-token>
     ```

4. Run the chatbot:
   ```bash
   chainlit run chainlit_app/app.py -w
   ```

## Requirements
- Python 3.8+
- OpenAI API key
- GitHub token
