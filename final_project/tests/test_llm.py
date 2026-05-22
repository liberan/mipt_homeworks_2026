from unittest.mock import MagicMock

import pytest
from openai import OpenAIError

from app.errors import LLMError
from app.llm import LLMClient


def _make_response(content):
    msg = MagicMock()
    msg.content = content
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def _make_chunk(content):
    delta = MagicMock()
    delta.content = content
    choice = MagicMock()
    choice.delta = delta
    chunk = MagicMock()
    chunk.choices = [choice]
    return chunk


def test_ask_returns_content(monkeypatch):
    client = LLMClient('k', 'http://h', 'm', 0.5)
    fake = MagicMock()
    fake.chat.completions.create.return_value = _make_response('hello')
    client._client = fake  # noqa: SLF001
    assert client.ask([{'role': 'user', 'content': 'hi'}]) == 'hello'


def test_ask_empty_choices_raises():
    client = LLMClient('k', 'http://h', 'm', 0.5)
    fake = MagicMock()
    resp = MagicMock()
    resp.choices = []
    fake.chat.completions.create.return_value = resp
    client._client = fake  # noqa: SLF001
    with pytest.raises(LLMError):
        client.ask([])


def test_ask_openai_error_wrapped():
    client = LLMClient('k', 'http://h', 'm', 0.5)
    fake = MagicMock()
    fake.chat.completions.create.side_effect = OpenAIError('boom')
    client._client = fake  # noqa: SLF001
    with pytest.raises(LLMError):
        client.ask([])


def test_ask_stream_yields_pieces():
    client = LLMClient('k', 'http://h', 'm', 0.5)
    fake = MagicMock()
    fake.chat.completions.create.return_value = iter([
        _make_chunk('he'),
        _make_chunk('llo'),
    ])
    client._client = fake  # noqa: SLF001
    pieces = list(client.ask_stream([]))
    assert pieces == ['he', 'llo']


def test_ask_stream_openai_error():
    client = LLMClient('k', 'http://h', 'm', 0.5)
    fake = MagicMock()
    fake.chat.completions.create.side_effect = OpenAIError('boom')
    client._client = fake  # noqa: SLF001
    with pytest.raises(LLMError):
        list(client.ask_stream([]))
