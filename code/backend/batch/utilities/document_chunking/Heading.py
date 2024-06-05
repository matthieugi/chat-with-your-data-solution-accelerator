from typing import List
from .DocumentChunkingBase import DocumentChunkingBase
from langchain.text_splitter import MarkdownHeaderTextSplitter, TokenTextSplitter
from ..helpers.EnvHelper import EnvHelper
from .Strategies import ChunkingSettings
from ..common.SourceDocument import SourceDocument


class HeadingDocumentChunking(DocumentChunkingBase):
    def __init__(self) -> None:
        pass

    def chunk(
        self, documents: List[SourceDocument], chunking: ChunkingSettings
    ) -> List[SourceDocument]:
        env_helpder = EnvHelper()

        full_document_content = "".join(
            list(map(lambda document: document.content, documents))
        )
        document_url = documents[0].source

        # Split on Level X of Header
        markdown_split_level = int(env_helpder.MARKDOWN_SPLIT_LEVEL)

        headers_to_split_on = []
        for i in range(1, markdown_split_level):
            headers_to_split_on.append([f"{'#' * i}", f"Header {i}"])

        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,
            return_each_line=False,
        )

        markdown_chunked_content_list = markdown_splitter.split_text(
            full_document_content
        )

        # Split on fixed size if needed
        token_splitter = TokenTextSplitter.from_tiktoken_encoder(
            chunk_size=chunking.chunk_size, chunk_overlap=chunking.chunk_overlap
        )

        chunked_content_list = token_splitter.create_documents(
            [x.page_content for x in markdown_chunked_content_list]
        )

        # Create document for each chunk
        documents = []
        chunk_offset = 0
        for idx, chunked_document in enumerate(chunked_content_list):
            documents.append(
                SourceDocument.from_metadata(
                    content=chunked_document.page_content,
                    document_url=document_url,
                    metadata={"offset": chunk_offset},
                    idx=idx,
                )
            )

            chunk_offset += len(chunked_document.page_content)
        return documents
