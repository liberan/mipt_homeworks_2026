import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from app.core.errors import ConfigError


@dataclass
class Config:
    api_key: str
    api_host: str
    model: str
    limit_message: int
    limit_chars: int
    temperature: float
    system_prompt: str


DEFAULT_SYSTEM_PROMPT = 'You are a helpful AI assistant.'
DEFAULT_MODEL = 'gemma3:270m'


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigError(f'config.yaml должен быть словарём, а получили: {type(data).__name__}')
    return data


def _pick(env_key: str, yaml_data: dict, yaml_key: str) -> str | None:
    # env имеет приоритет над yaml
    value = os.environ.get(env_key)
    if value is not None and value != '':
        return value
    if yaml_key in yaml_data and yaml_data[yaml_key] is not None:
        return str(yaml_data[yaml_key])
    return None


def _to_int(value: str | None, name: str) -> int:
    if value is None:
        raise ConfigError(f'Не задан параметр {name}')
    try:
        return int(value)
    except ValueError as e:
        raise ConfigError(f'Параметр {name} должен быть целым числом, а получили: {value!r}') from e


def _to_float(value: str | None, name: str) -> float:
    if value is None:
        raise ConfigError(f'Не задан параметр {name}')
    try:
        return float(value)
    except ValueError as e:
        raise ConfigError(f'Параметр {name} должен быть числом, а получили: {value!r}') from e


def load_config(yaml_path: Path | None = None) -> Config:
    if yaml_path is None:
        yaml_path = Path('config.yaml')
    yaml_data = _read_yaml(yaml_path)

    # Если нет ни yaml ни переменных окружения вообще - сообщаем и выходим
    any_env = any(os.environ.get(k) for k in (
        'API_KEY', 'API_HOST', 'MODEL', 'LIMIT_MESSAGE', 'LIMIT_CHARS', 'TEMPERATURE',
    ))
    if not yaml_data and not any_env:
        raise ConfigError(
            'Не найдено ни переменных окружения, ни config.yaml. '
            'Задайте настройки одним из этих способов.'
        )

    api_key = _pick('API_KEY', yaml_data, 'api_key')
    if not api_key:
        raise ConfigError('Не задан API_KEY')

    api_host = _pick('API_HOST', yaml_data, 'api_host')
    if not api_host:
        raise ConfigError('Не задан API_HOST')

    model = _pick('MODEL', yaml_data, 'model') or DEFAULT_MODEL

    limit_message = _to_int(_pick('LIMIT_MESSAGE', yaml_data, 'limit_message'), 'LIMIT_MESSAGE')
    if limit_message <= 0:
        raise ConfigError('LIMIT_MESSAGE должен быть больше 0')

    limit_chars = _to_int(_pick('LIMIT_CHARS', yaml_data, 'limit_chars'), 'LIMIT_CHARS')
    if limit_chars <= 0:
        raise ConfigError('LIMIT_CHARS должен быть больше 0')

    temperature = _to_float(_pick('TEMPERATURE', yaml_data, 'temperature'), 'TEMPERATURE')
    if temperature < 0 or temperature > 1:
        raise ConfigError('TEMPERATURE должна быть от 0 до 1')

    # system_prompt берём только из yaml (env-вариант не предусмотрен заданием)
    system_prompt = yaml_data.get('system_prompt') or DEFAULT_SYSTEM_PROMPT
    if not isinstance(system_prompt, str):
        raise ConfigError('system_prompt должен быть строкой')

    return Config(
        api_key=api_key,
        api_host=api_host,
        model=model,
        limit_message=limit_message,
        limit_chars=limit_chars,
        temperature=temperature,
        system_prompt=system_prompt,
    )
