import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def pytest_configure(config):  # noqa: ARG001
    # подчищаем env, чтобы тесты не зависели от окружения разработчика.
    for key in ('API_KEY', 'API_HOST', 'MODEL', 'LIMIT_MESSAGE', 'LIMIT_CHARS', 'TEMPERATURE'):
        os.environ.pop(key, None)
