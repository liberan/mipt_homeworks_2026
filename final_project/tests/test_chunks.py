import pytest

from app.chunks import (
    ChunkOptions,
    iter_chunks,
    parse_command,
    split_by_length,
    split_by_paragraphs,
)


def test_parse_default():
    options = parse_command('/file_chunk')
    assert options.paragraphs == 1
    assert options.length is None
    assert options.auto is False


def test_parse_paragraph():
    options = parse_command('/file_chunk paragraph=3')
    assert options.paragraphs == 3
    assert options.length is None


def test_parse_len():
    options = parse_command('/file_chunk len=150')
    assert options.length == 150


def test_parse_auto_flag():
    options = parse_command('/file_chunk paragraph=2 -y')
    assert options.paragraphs == 2
    assert options.auto is True


def test_parse_bad_value():
    with pytest.raises(ValueError):
        parse_command('/file_chunk paragraph=zzz')


def test_parse_negative_value():
    with pytest.raises(ValueError):
        parse_command('/file_chunk paragraph=0')


def test_parse_unknown():
    with pytest.raises(ValueError):
        parse_command('/file_chunk foo=bar')


def test_split_by_paragraphs_one():
    text = 'a\nb\nc'
    chunks = list(split_by_paragraphs(text, 1))
    assert chunks == ['a', 'b', 'c']


def test_split_by_paragraphs_two():
    text = 'a\nb\nc\nd\ne'
    chunks = list(split_by_paragraphs(text, 2))
    assert chunks == ['a\nb', 'c\nd', 'e']


def test_split_by_paragraphs_skips_empty_lines():
    text = 'a\n\nb\n\nc'
    chunks = list(split_by_paragraphs(text, 1))
    assert chunks == ['a', 'b', 'c']


def test_split_by_length():
    text = 'abcdefghij'
    assert list(split_by_length(text, 3)) == ['abc', 'def', 'ghi', 'j']


def test_iter_chunks_paragraphs():
    options = ChunkOptions(paragraphs=2)
    chunks = list(iter_chunks('1\n2\n3\n4', options))
    assert chunks == ['1\n2', '3\n4']


def test_iter_chunks_length():
    options = ChunkOptions(length=2)
    chunks = list(iter_chunks('abcd', options))
    assert chunks == ['ab', 'cd']
