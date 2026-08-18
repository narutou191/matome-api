from unittest.mock import MagicMock, patch

import anthropic
import httpx
import pytest

from core.vision_client import extract, VisionExtractionError


def _fake_response(text):
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


def _fake_httpx_response(status_code):
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    return httpx.Response(status_code=status_code, request=request)


@patch("core.vision_client.Anthropic")
def test_extract_parses_json_from_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response(
        'Aqui está o JSON:\n{"rent_text": "42,000円", "property_type": "アパート"}'
    )
    mock_anthropic_cls.return_value = mock_client

    result = extract([(b"fake-image-bytes", "image/png")], api_key="test-key")

    assert result == {"rent_text": "42,000円", "property_type": "アパート"}
    mock_client.messages.create.assert_called_once()


@patch("core.vision_client.Anthropic")
def test_extract_sends_all_images_plus_prompt(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response("{}")
    mock_anthropic_cls.return_value = mock_client

    extract(
        [(b"img-one", "image/png"), (b"img-two", "image/jpeg")],
        api_key="test-key",
    )

    _, kwargs = mock_client.messages.create.call_args
    content = kwargs["messages"][0]["content"]
    assert len(content) == 3  # 2 images + 1 text prompt
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1]["source"]["media_type"] == "image/jpeg"
    assert content[2]["type"] == "text"


@patch("core.vision_client.Anthropic")
def test_extract_raises_when_no_json_found(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response(
        "desculpe, não consegui ler a imagem"
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Não consegui extrair"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


def test_extract_raises_when_no_images():
    with pytest.raises(VisionExtractionError):
        extract([], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_authentication_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.AuthenticationError(
        "invalid api key", response=_fake_httpx_response(401), body=None
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="configuração do servidor"):
        extract([(b"fake-image-bytes", "image/png")], api_key="bad-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_rate_limit_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.RateLimitError(
        "rate limited", response=_fake_httpx_response(429), body=None
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Limite de requisições"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_timeout_error(mock_anthropic_cls):
    mock_client = MagicMock()
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    mock_client.messages.create.side_effect = anthropic.APITimeoutError(request=request)
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Demorou muito"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_raises_when_json_is_malformed(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = _fake_response("{invalid json")
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Não consegui extrair"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_maps_generic_api_error(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = anthropic.InternalServerError(
        "internal server error", response=_fake_httpx_response(500), body=None
    )
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Erro ao consultar a Claude API"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


def test_extract_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(VisionExtractionError, match="configuração do servidor"):
        extract([(b"img", "image/png")], api_key=None)


@patch("core.vision_client.Anthropic")
def test_extract_raises_when_response_content_is_empty(mock_anthropic_cls):
    mock_client = MagicMock()
    response = MagicMock()
    response.content = []
    mock_client.messages.create.return_value = response
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Claude não retornou"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")


@patch("core.vision_client.Anthropic")
def test_extract_skips_leading_thinking_block(mock_anthropic_cls):
    """Extended-thinking-capable models can return a ThinkingBlock (type='thinking',
    no usable .text) before the actual TextBlock — extract() must find the text
    block instead of assuming content[0] is always text.
    """
    thinking_block = MagicMock()
    thinking_block.type = "thinking"
    del thinking_block.text  # ThinkingBlock has no .text attribute in the real SDK

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = '{"rent_text": "82,500円"}'

    response = MagicMock()
    response.content = [thinking_block, text_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = response
    mock_anthropic_cls.return_value = mock_client

    result = extract([(b"fake-image-bytes", "image/png")], api_key="test-key")

    assert result == {"rent_text": "82,500円"}


@patch("core.vision_client.Anthropic")
def test_extract_raises_when_only_thinking_blocks_present(mock_anthropic_cls):
    thinking_block = MagicMock()
    thinking_block.type = "thinking"
    del thinking_block.text

    response = MagicMock()
    response.content = [thinking_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = response
    mock_anthropic_cls.return_value = mock_client

    with pytest.raises(VisionExtractionError, match="Claude não retornou"):
        extract([(b"fake-image-bytes", "image/png")], api_key="test-key")
