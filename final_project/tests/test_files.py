import pytest

from app.errors import FileTooBigError
from app.files import extract_file_paths, read_text_file, substitute_files


def test_extract_one_path():
    text = 'посмотри в @::/tmp/a.txt::'
    assert extract_file_paths(text) == ['/tmp/a.txt']


def test_extract_many_paths():
    text = '@::/a.txt:: и ещё @::/b.txt:: тут'
    assert extract_file_paths(text) == ['/a.txt', '/b.txt']


def test_extract_no_paths():
    assert extract_file_paths('обычный текст без файлов') == []


def test_extract_empty_path_ignored():
    # @:::: - пустой путь между двоеточиями
    assert extract_file_paths('@::::') == []


def test_substitute_no_files():
    text = 'привет мир'
    assert substitute_files(text) == 'привет мир'


def test_substitute_file_content(tmp_path):
    p = tmp_path / 'a.txt'
    p.write_text('print(1/0)', encoding='utf-8')
    text = f'в чём ошибка? @::{p}::'
    result = substitute_files(text)
    assert 'в чём ошибка?' in result
    assert 'print(1/0)' in result


def test_substitute_multiple_files(tmp_path):
    a = tmp_path / 'a.txt'
    b = tmp_path / 'b.txt'
    a.write_text('AAA', encoding='utf-8')
    b.write_text('BBB', encoding='utf-8')
    text = f'смотри @::{a}:: и @::{b}::'
    result = substitute_files(text)
    assert 'AAA' in result
    assert 'BBB' in result
    # старые маркеры должны быть удалены
    assert '@::' not in result


def test_read_text_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_text_file(tmp_path / 'nope.txt')


def test_read_text_file_too_big(tmp_path, monkeypatch):
    p = tmp_path / 'big.txt'
    p.write_text('x' * 100, encoding='utf-8')
    # имитируем маленький лимит
    monkeypatch.setattr('app.files.MAX_FILE_SIZE', 10)
    with pytest.raises(FileTooBigError):
        read_text_file(p)


def test_read_text_file_directory(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_text_file(tmp_path)


def test_read_text_file_ok(tmp_path):
    p = tmp_path / 'a.txt'
    p.write_text('hello', encoding='utf-8')
    assert read_text_file(p) == 'hello'
