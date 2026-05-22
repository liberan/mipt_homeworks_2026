import pytest

from app.config import load_config
from app.errors import ConfigError


def test_no_config_at_all(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError):
        load_config()


def test_only_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'k')
    monkeypatch.setenv('API_HOST', 'http://h')
    monkeypatch.setenv('LIMIT_MESSAGE', '5')
    monkeypatch.setenv('LIMIT_CHARS', '100')
    monkeypatch.setenv('TEMPERATURE', '0.5')
    cfg = load_config()
    assert cfg.api_key == 'k'
    assert cfg.api_host == 'http://h'
    assert cfg.limit_message == 5
    assert cfg.limit_chars == 100
    assert cfg.temperature == 0.5


def test_yaml_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yaml').write_text(
        'api_key: kk\n'
        'api_host: http://h2\n'
        'limit_message: 10\n'
        'limit_chars: 200\n'
        'temperature: 0.7\n'
        'system_prompt: be nice\n',
        encoding='utf-8',
    )
    cfg = load_config()
    assert cfg.api_key == 'kk'
    assert cfg.system_prompt == 'be nice'
    assert cfg.limit_message == 10


def test_env_overrides_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yaml').write_text(
        'api_key: yaml_key\n'
        'api_host: http://from_yaml\n'
        'limit_message: 10\n'
        'limit_chars: 200\n'
        'temperature: 0.7\n',
        encoding='utf-8',
    )
    monkeypatch.setenv('API_KEY', 'env_key')
    cfg = load_config()
    assert cfg.api_key == 'env_key'
    assert cfg.api_host == 'http://from_yaml'  # из yaml


def test_invalid_temperature(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'k')
    monkeypatch.setenv('API_HOST', 'http://h')
    monkeypatch.setenv('LIMIT_MESSAGE', '5')
    monkeypatch.setenv('LIMIT_CHARS', '100')
    monkeypatch.setenv('TEMPERATURE', '1.5')
    with pytest.raises(ConfigError):
        load_config()


def test_invalid_limit_message(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'k')
    monkeypatch.setenv('API_HOST', 'http://h')
    monkeypatch.setenv('LIMIT_MESSAGE', '-1')
    monkeypatch.setenv('LIMIT_CHARS', '100')
    monkeypatch.setenv('TEMPERATURE', '0.5')
    with pytest.raises(ConfigError):
        load_config()


def test_non_numeric_limit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_KEY', 'k')
    monkeypatch.setenv('API_HOST', 'http://h')
    monkeypatch.setenv('LIMIT_MESSAGE', 'abc')
    monkeypatch.setenv('LIMIT_CHARS', '100')
    monkeypatch.setenv('TEMPERATURE', '0.5')
    with pytest.raises(ConfigError):
        load_config()


def test_missing_api_key(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('API_HOST', 'http://h')
    monkeypatch.setenv('LIMIT_MESSAGE', '5')
    monkeypatch.setenv('LIMIT_CHARS', '100')
    monkeypatch.setenv('TEMPERATURE', '0.5')
    with pytest.raises(ConfigError):
        load_config()


def test_yaml_not_dict(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'config.yaml').write_text('- 1\n- 2\n', encoding='utf-8')
    with pytest.raises(ConfigError):
        load_config()
