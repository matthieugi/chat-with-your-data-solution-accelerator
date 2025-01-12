import ssl
import pytest
from pytest_httpserver import HTTPServer
from tests.functional.backend_api.app_config import AppConfig
import trustme


@pytest.fixture(scope="session")
def ca():
    """
    This fixture is required to run the http mock server with SSL.
    https://pytest-httpserver.readthedocs.io/en/latest/howto.html#running-an-https-server
    """
    return trustme.CA()


@pytest.fixture(scope="session")
def httpserver_ssl_context(ca):
    """
    This fixture is required to run the http mock server with SSL.
    https://pytest-httpserver.readthedocs.io/en/latest/howto.html#running-an-https-server
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    localhost_cert = ca.issue_cert("localhost")
    localhost_cert.configure_cert(context)
    return context


@pytest.fixture(scope="session")
def httpclient_ssl_context(ca):
    """
    This fixture is required to run the http mock server with SSL.
    https://pytest-httpserver.readthedocs.io/en/latest/howto.html#running-an-https-server
    """
    with ca.cert_pem.tempfile() as ca_temp_path:
        return ssl.create_default_context(cafile=ca_temp_path)


@pytest.fixture(scope="function", autouse=True)
def setup_default_mocking(httpserver: HTTPServer, app_config: AppConfig):
    httpserver.expect_request(
        f"/openai/deployments/{app_config.get('AZURE_OPENAI_EMBEDDING_MODEL')}/embeddings",
        method="POST",
    ).respond_with_json(
        {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "embedding": [0.018990106880664825, -0.0073809814639389515],
                    "index": 0,
                }
            ],
            "model": "text-embedding-ada-002",
        }
    )

    httpserver.expect_request(
        f"/indexes('{app_config.get('AZURE_SEARCH_INDEX')}')",
        method="GET",
    ).respond_with_json({}, status=404)

    httpserver.expect_request(
        "/indexes",
        method="POST",
    ).respond_with_json({}, status=201)

    httpserver.expect_request(
        f"/indexes('{app_config.get('AZURE_SEARCH_CONVERSATIONS_LOG_INDEX')}')",
        method="GET",
    ).respond_with_json({})

    httpserver.expect_request(
        "/contentsafety/text:analyze",
        method="POST",
    ).respond_with_json(
        {
            "blocklistsMatch": [],
            "categoriesAnalysis": [],
        }
    )

    httpserver.expect_request(
        f"/openai/deployments/{app_config.get('AZURE_OPENAI_MODEL')}/chat/completions",
        method="POST",
    ).respond_with_json(
        {
            "id": "chatcmpl-6v7mkQj980V1yBec6ETrKPRqFjNw9",
            "object": "chat.completion",
            "created": 1679072642,
            "model": app_config.get("AZURE_OPENAI_MODEL"),
            "usage": {
                "prompt_tokens": 58,
                "completion_tokens": 68,
                "total_tokens": 126,
            },
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "42 is the meaning of life",
                    },
                    "finish_reason": "stop",
                    "index": 0,
                }
            ],
        }
    )

    httpserver.expect_request(
        f"/indexes('{app_config.get('AZURE_SEARCH_CONVERSATIONS_LOG_INDEX')}')/docs/search.index",
        method="POST",
    ).respond_with_json(
        {
            "value": [
                {"key": "1", "status": True, "errorMessage": None, "statusCode": 201}
            ]
        }
    )

    httpserver.expect_request(
        f"/indexes('{app_config.get('AZURE_SEARCH_INDEX')}')/docs/search.post.search",
        method="POST",
    ).respond_with_json(
        {
            "value": [
                {
                    "@search.score": 0.02916666865348816,
                    "id": "doc_1",
                    "content": "content",
                    "content_vector": [
                        -0.012909674,
                        0.00838491,
                    ],
                    "metadata": '{"id": "doc_1", "source": "https://source", "title": "/documents/doc.pdf", "chunk": 95, "offset": 202738, "page_number": null}',
                    "title": "/documents/doc.pdf",
                    "source": "https://source",
                    "chunk": 95,
                    "offset": 202738,
                }
            ]
        }
    )

    httpserver.expect_request(
        "/sts/v1.0/issueToken",
        method="POST",
    ).respond_with_data("speech-token")

    yield

    httpserver.check()
