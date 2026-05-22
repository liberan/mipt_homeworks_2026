from pathlib import Path

from app.errors import FileTooBigError

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ


def read_text_file(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f'Файл не найден: {p}')
    if not p.is_file():
        raise FileNotFoundError(f'Это не файл: {p}')
    size = p.stat().st_size
    if size > MAX_FILE_SIZE:
        raise FileTooBigError(
            f'Файл слишком большой ({size} байт), лимит {MAX_FILE_SIZE} байт'
        )
    # читаем как текст в utf-8
    return p.read_text(encoding='utf-8', errors='replace')


def extract_file_paths(text: str) -> list[str]:
    # ищем все вхождения @::...::
    result = []
    i = 0
    while True:
        start = text.find('@::', i)
        if start == -1:
            break
        end = text.find('::', start + 3)
        if end == -1:
            break
        path = text[start + 3:end]
        if path:
            result.append(path)
        i = end + 2
    return result


def substitute_files(text: str) -> str:
    # заменяем @::path:: на содержимое файла, разделяем переносами строк.
    paths = extract_file_paths(text)
    if not paths:
        return text

    # удаляем все @::path:: из текста
    cleaned = text
    for path in paths:
        cleaned = cleaned.replace(f'@::{path}::', '')
    cleaned = cleaned.strip()

    parts = [cleaned] if cleaned else []
    for path in paths:
        content = read_text_file(path)
        parts.append(content)
    return '\n'.join(parts)
