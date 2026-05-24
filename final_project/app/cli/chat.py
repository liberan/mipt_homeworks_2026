import os
import sys
from pathlib import Path

from app.core.config import Config
from app.core.errors import AppError, FileTooBigError, LLMError
from app.services.chunks import ChunkOptions, iter_chunks, parse_command
from app.services.files import read_text_file, substitute_files
from app.services.history import History
from app.services.llm import LLMClient

PROMPT = '>>> '
EXIT_COMMAND = '\\q'
RESET_COMMAND = '/reset'
FILE_CHUNK_PREFIX = '/file_chunk'


def clear_screen() -> None:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def print_streamed(client: LLMClient, messages: list[dict]) -> str:
    # печатаем по мере поступления, возвращаем весь ответ полностью.
    parts: list[str] = []
    for piece in client.ask_stream(messages):
        sys.stdout.write(piece)
        sys.stdout.flush()
        parts.append(piece)
    sys.stdout.write('\n')
    sys.stdout.flush()
    return ''.join(parts)


def handle_chat_message(text: str, history: History, client: LLMClient, system_prompt: str) -> None:
    try:
        text_with_files = substitute_files(text)
    except (FileNotFoundError, FileTooBigError, OSError) as e:
        print(f'[Ошибка файла] {e}')
        return

    history.add_user(text_with_files)
    messages = [{'role': 'system', 'content': system_prompt}] + history.as_list()

    try:
        answer = print_streamed(client, messages)
    except KeyboardInterrupt:
        print('\n[Запрос прерван пользователем]')
        # уберём сообщение пользователя из истории - запрос не состоялся
        history.pop_last()
        return
    except LLMError as e:
        print(f'[Ошибка LLM] {e}')
        history.pop_last()
        return

    history.add_assistant(answer)


def ask_input(prompt: str = PROMPT) -> str:
    return input(prompt)


def run_file_chunk_mode(raw_command: str, client: LLMClient) -> None:
    try:
        options = parse_command(raw_command)
    except ValueError as e:
        print(f'[Ошибка параметров] {e}')
        return

    print('Введите путь до файла:')
    path_str = ask_input().strip()
    if path_str == EXIT_COMMAND:
        return
    try:
        text = read_text_file(Path(path_str))
    except (FileNotFoundError, FileTooBigError, OSError) as e:
        print(f'[Ошибка файла] {e}')
        return

    print('Принято. Что нужно сделать для каждого фрагмента (User Prompt)?')
    user_prompt = ask_input().strip()
    if user_prompt == EXIT_COMMAND:
        return
    if not user_prompt:
        print('[Ошибка] Пустой user prompt')
        return

    print('Принято. Начинаю обработку:')
    process_chunks(text, user_prompt, options, client)
    print('Обработка файла завершена.')


def process_chunks(text: str, user_prompt: str, options: ChunkOptions, client: LLMClient) -> None:
    for chunk in iter_chunks(text, options):
        messages = [
            {'role': 'user', 'content': f'{user_prompt}\n\n{chunk}'},
        ]
        try:
            print_streamed(client, messages)
        except KeyboardInterrupt:
            print('\n[Обработка прервана пользователем]')
            return
        except LLMError as e:
            print(f'[Ошибка LLM] {e}')
            return

        if options.auto:
            continue

        # ждём enter, либо \q для выхода
        try:
            command = ask_input()
        except EOFError:
            return
        if command.strip() == EXIT_COMMAND:
            return


def run_chat(config: Config) -> None:
    client = LLMClient(
        api_key=config.api_key,
        api_host=config.api_host,
        model=config.model,
        temperature=config.temperature,
    )
    history = History(limit_message=config.limit_message, limit_chars=config.limit_chars)

    print('GigaVibeMiptCode. Введите сообщение или команду (\\q для выхода).')

    while True:
        try:
            user_text = ask_input()
        except EOFError:
            print()
            return

        stripped = user_text.strip()
        if stripped == '':
            continue
        if stripped == EXIT_COMMAND:
            return
        if stripped == RESET_COMMAND:
            history.reset()
            clear_screen()
            continue
        if stripped.startswith(FILE_CHUNK_PREFIX):
            run_file_chunk_mode(stripped, client)
            continue

        handle_chat_message(user_text, history, client, config.system_prompt)


def main() -> int:
    from dotenv import load_dotenv

    from app.core.config import load_config
    from app.core.errors import ConfigError

    load_dotenv()
    try:
        config = load_config()
    except ConfigError as e:
        print(f'[Ошибка конфигурации] {e}')
        return 1
    try:
        run_chat(config)
    except AppError as e:
        print(f'[Ошибка] {e}')
        return 1
    return 0
