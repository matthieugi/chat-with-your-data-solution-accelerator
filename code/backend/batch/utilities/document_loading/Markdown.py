import requests
from typing import List

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, ContentFormat

from .DocumentLoadingBase import DocumentLoadingBase
from ..common.SourceDocument import SourceDocument

from ..helpers.EnvHelper import EnvHelper


class MarkdownLoading(DocumentLoadingBase):
    def __init__(self) -> None:
        super().__init__()

    def load(self, document_url: str) -> List[SourceDocument]:
        env_helper: EnvHelper = EnvHelper()

        document_intelligence_client = DocumentIntelligenceClient(
            endpoint=env_helper.AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(env_helper.AZURE_FORM_RECOGNIZER_KEY),
            api_version="2024-02-29-preview",
            headers={
                "x-ms-useragent": "chat-with-your-data-solution-accelerator/1.0.0"
            },
        )

        poller = None

        with requests.get(document_url, timeout=30) as response:
            response.raise_for_status()

            poller = document_intelligence_client.begin_analyze_document(
                "prebuilt-layout",
                AnalyzeDocumentRequest(bytes_source=response.content),
                output_content_format=ContentFormat.MARKDOWN,
            )

        result = poller.result()

        document = [SourceDocument(content=result.content, source=document_url)]

        return document
