import os
from typing import Annotated
from azure.core.exceptions import AzureError
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature, DocumentContentFormat, AnalyzeResult
from azure.identity import DefaultAzureCredential

class DocumentParserPlugin:
    """A plugin that is used to parse documents."""

    def _analyze_document(self, file_name: str, client: DocumentIntelligenceClient) -> str:
        # Build the full file path
        print("Processing file = ", file_name)
        document_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', file_name)
        with open(document_path, "rb") as f:
            poller = client.begin_analyze_document(
                "prebuilt-layout",
                body=f,
                features=[DocumentAnalysisFeature.STYLE_FONT],
                output_content_format=DocumentContentFormat.MARKDOWN
            )
        parsed_result: AnalyzeResult = poller.result()
        return parsed_result.content

    @kernel_function(description="Reads in policy documents and returns the parsed output in markdown format.")
    def parse_documents(
        self, 
        underlier: Annotated[str, "The file name of the underlier policy document to parse."],
        master: Annotated[str, "The file name of the master policy document to parse."]
    ) -> Annotated[str, "Returns the content parsed from the documents in markdown format."]:
        try:
            document_intelligence_endpoint = os.environ['DOCUMENT_INTELLIGENCE_ENDPOINT']
            #document_intelligence_api_key = os.environ['DOCUMENT_INTELLIGENCE_API_KEY']
            credential = DefaultAzureCredential()
            print(f"Document Intelligence Endpoint: {document_intelligence_endpoint}")
            print("calling doc intel api")
            client = DocumentIntelligenceClient(
                document_intelligence_endpoint,
                credential=credential
            )
            print("underlier path = ",underlier)
            print("master path = ",master)
            underlier_content = self._analyze_document(underlier, client)
            master_content = self._analyze_document(master, client)
            print("doc intel api called")
        except FileNotFoundError:
            return "Error: The specified document file was not found."
        except AzureError as e:
            return f"Error: An error occurred with the Azure Document Intelligence service: {e}"
        except Exception as e:
            return f"Error: An unexpected error occurred: {e}"

        return f"<underlier_policy>\n{underlier_content}\n</underlier_policy>\n<master_policy>\n{master_content}</master_policy>"