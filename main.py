from langchain_openai import OpenAI
import os
from dotenv import load_dotenv

success = load_dotenv(dotenv_path=".env")
print(f"Environment variables loaded: {success}")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Loaded API Key: {OPENAI_API_KEY}")

def main():
    llm = OpenAI(openai_api_key=OPENAI_API_KEY)
    result = llm.invoke("What is the capital of France?")
    print(result)

if __name__ == "__main__":
    main()
