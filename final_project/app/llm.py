from collections.abc import Iterator

from openai import OpenAI, OpenAIError

from app.errors import LLMError


class LLMClient:
    def __init__(self, api_key: str, api_host: str, model: str, temperature: float) -> None:
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(api_key=api_key, base_url=api_host)

    def ask(self, messages: list[dict]) -> str:
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.temperature,
            )
        except OpenAIError as e:
            raise LLMError(f'Ошибка обращения к LLM: {e}') from e
        if not response.choices:
            raise LLMError('LLM вернул пустой ответ')
        content = response.choices[0].message.content
        if content is None:
            return ''
        return content

    def ask_stream(self, messages: list[dict]) -> Iterator[str]:
        try:
            stream = self._client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                temperature=self.temperature,
                stream=True,
            )
        except OpenAIError as e:
            raise LLMError(f'Ошибка обращения к LLM: {e}') from e
        try:
            for chunk in stream:
                if not chunk.choices:  # type: ignore[union-attr]
                    continue
                delta = chunk.choices[0].delta  # type: ignore[union-attr]
                if delta and delta.content:
                    yield delta.content
        except OpenAIError as e:
            raise LLMError(f'Ошибка стриминга от LLM: {e}') from e
