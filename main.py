import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate, HumanMessagePromptTemplate
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

class Country(BaseModel):
    name: str = Field(description="The name of the county.")
    capital: str = Field(description="The capital of the county.")

success = load_dotenv(dotenv_path=".env")
print(f"Environment variables loaded: {success}")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-3.5-turbo"
PROMPT_COUNTRY_INFO = """
Provide information about {country}
{format_instructions}
"""


def main():
    llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model=OPENAI_MODEL)
    parser = PydanticOutputParser(pydantic_object=Country)

    country = input("Enter the country name: ")

    message = HumanMessagePromptTemplate.from_template(PROMPT_COUNTRY_INFO)
    chat_prompt = ChatPromptTemplate.from_messages([message])
    prompt = chat_prompt.format_prompt(country=country, format_instructions=parser.get_format_instructions())

    response = llm(prompt.to_messages())
    data = parser.parse(response.content)
    print(f"Country: {data.name}")
    print(f"Capital: {data.capital}")

if __name__ == "__main__":
    main()
