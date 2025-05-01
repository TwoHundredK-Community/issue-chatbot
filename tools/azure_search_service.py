from azure.core.exceptions import ResourceExistsError
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import os
from langchain.tools import BaseTool, tool
from langchain_community.document_loaders import GitLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tempfile

load_dotenv()
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_ADMIN_KEY = os.getenv("AZURE_ADMIN_KEY")
AZURE_QUERY_KEY = os.getenv("AZURE_QUERY_KEY")
ALLOWED_INDEX_NUMBER = os.getenv("ALLOWED_INDEX_NUMBER", 3)
ALLOW_AZURE_AI_SEARCH = os.getenv("ALLOW_AZURE_AI_SEARCH", "false").lower() == "true"

class AzureSearchService():
    def __init__(self):
        if not ALLOW_AZURE_AI_SEARCH:
            raise ValueError("Azure AI Search is not enabled. Set ALLOW_AZURE_AI_SEARCH to true to use this feature.")
        self.endpoint = AZURE_SEARCH_ENDPOINT
        self.admin_key = AZURE_ADMIN_KEY
        self.query_key = AZURE_QUERY_KEY

        # Use AzureKeyCredential for admin and query keys if provided
        admin_credential = AzureKeyCredential(self.admin_key) if self.admin_key else DefaultAzureCredential()
        query_credential = AzureKeyCredential(self.query_key) if self.query_key else DefaultAzureCredential()

        self.index_client = SearchIndexClient(endpoint=self.endpoint, credential=admin_credential)
        self.search_client = SearchClient(endpoint=self.endpoint, index_name="repos", credential=query_credential)

    def check_index_exists(self, repo_name):
        indexes = self.index_client.list_indexes()
        return any(index.name == repo_name for index in indexes)

    def delete_oldest_index(self):
        indexes = list(self.index_client.list_indexes())
        if len(indexes) >= int(ALLOWED_INDEX_NUMBER):
            # Delete the first index in the list as a fallback
            oldest_index = indexes[0]
            self.index_client.delete_index(oldest_index.name)

    def create_index(self, repo_name):
        try:
            print(f"Attempting to create index: {repo_name}")
            index = SearchIndex(name=repo_name, fields=[
                {"name": "id", "type": "Edm.String", "key": True},
                {"name": "content", "type": "Edm.String"}
            ])
            response = self.index_client.create_index(index)
            print(f"Index '{repo_name}' created successfully. Response: {response}")
        except ResourceExistsError:
            print(f"Index '{repo_name}' already exists.")
        except Exception as e:
            print(f"Error creating index '{repo_name}': {e}")
            raise

    def upload_documents(self, repo_name, documents):
        # Ensure the index exists before uploading documents
        if not self.check_index_exists(repo_name):
            print(f"Index '{repo_name}' does not exist. Creating it now.")
            self.create_index(repo_name)
        else:
            print(f"Index '{repo_name}' already exists. Proceeding to upload documents.")
        try:
            response = self.search_client.upload_documents(documents)
            print(f"Documents uploaded successfully to index '{repo_name}'. Response: {response}")
        except Exception as e:
            print(f"Error uploading documents to index '{repo_name}': {e}")
            raise

@tool
def azure_ai_search(repo_url: str, issue_text: str, k: int = 5):
    """Finds the most relevant files or functions in a GitHub repo based on an issue description using Azure AI Search Service.
    Args:
        repo_url (str): The URL of the GitHub repository.
        issue_text (str): The text of the GitHub issue.
        k (int): The number of relevant code snippets to return.
    Returns:
        List[Dict]: A list of dictionaries containing the source file and a snippet of the relevant code.
    """
    if not ALLOW_AZURE_AI_SEARCH:
        raise ValueError("Azure AI Search is not enabled. Set ALLOW_AZURE_AI_SEARCH to true to use this feature.")

    azure_service = AzureSearchService()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Load and split the codebase
        loader = GitLoader(clone_url=repo_url, repo_path=tmpdir)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
        chunks = splitter.split_documents(docs)

        # Upload documents to Azure AI Search Service
        repo_name = repo_url.split('/')[-1]
        if not azure_service.check_index_exists(repo_name):
            azure_service.delete_oldest_index()
            azure_service.create_index(repo_name)
            documents = [
                {"id": str(i), "content": chunk.page_content}
                for i, chunk in enumerate(chunks)
            ]
            azure_service.upload_documents(repo_name, documents)

        # Query Azure AI Search Service for relevant documents
        query_results = azure_service.search_client.search(issue_text, top=k)
        relevant_docs = [
            {
                "source": result["id"],
                "snippet": result["content"][:300]
            }
            for result in query_results
        ]

        return relevant_docs

def test_azure_search_service():
    """Test function for AzureSearchService."""
    try:
        # Initialize the AzureSearchService
        azure_service = AzureSearchService()

        # Test index creation
        print("Testing index creation...")
        azure_service.create_index("test_repo")

        # Test document upload
        print("Testing document upload...")
        documents = [
            {"id": "1", "content": "This is a test document."},
            {"id": "2", "content": "Another test document."}
        ]
        azure_service.upload_documents("test_repo", documents)

        # Test search functionality
        print("Testing search functionality...")
        query_results = azure_service.search_client.search("test", top=2)
        for result in query_results:
            print(f"Found document: {result['id']} with content: {result['content']}")

        print("All tests passed successfully.")
    except Exception as e:
        print(f"Test failed: {e}")


