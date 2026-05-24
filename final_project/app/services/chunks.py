from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class ChunkOptions:
    # как именно бить на чанки. по умолчанию по абзацам.
    paragraphs: int = 1
    length: int | None = None
    auto: bool = False


def parse_command(raw: str) -> ChunkOptions:
    # парсим что-то вроде "/file_chunk paragraph=3 -y" или "/file_chunk len=150"
    options = ChunkOptions()
    parts = raw.strip().split()
    for part in parts[1:]:
        if part == '-y':
            options.auto = True
        elif part.startswith('paragraph='):
            value = part[len('paragraph='):]
            try:
                options.paragraphs = int(value)
            except ValueError as e:
                raise ValueError(f'paragraph должен быть числом: {value!r}') from e
            if options.paragraphs <= 0:
                raise ValueError('paragraph должен быть больше 0')
        elif part.startswith('len='):
            value = part[len('len='):]
            try:
                options.length = int(value)
            except ValueError as e:
                raise ValueError(f'len должен быть числом: {value!r}') from e
            if options.length <= 0:
                raise ValueError('len должен быть больше 0')
        else:
            raise ValueError(f'Неизвестный параметр: {part}')
    return options


def split_by_paragraphs(text: str, n: int) -> Iterator[str]:
    # бьём по пустым строкам, потом склеиваем по n абзацев.
    parts = [p.strip() for p in text.split('\n') if p.strip() != '']
    if not parts:
        return
    bucket: list[str] = []
    for p in parts:
        bucket.append(p)
        if len(bucket) >= n:
            yield '\n'.join(bucket)
            bucket = []
    if bucket:
        yield '\n'.join(bucket)


def split_by_length(text: str, n: int) -> Iterator[str]:
    if n <= 0:
        return
    i = 0
    while i < len(text):
        yield text[i:i + n]
        i += n


def iter_chunks(text: str, options: ChunkOptions) -> Iterator[str]:
    if options.length is not None:
        yield from split_by_length(text, options.length)
    else:
        yield from split_by_paragraphs(text, options.paragraphs)
