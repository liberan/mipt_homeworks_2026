from app.history import History


def test_add_user_and_assistant():
    h = History(limit_message=10, limit_chars=1000)
    h.add_user('hi')
    h.add_assistant('hello')
    messages = h.as_list()
    assert messages == [
        {'role': 'user', 'content': 'hi'},
        {'role': 'assistant', 'content': 'hello'},
    ]


def test_trim_by_message_count():
    h = History(limit_message=3, limit_chars=10000)
    for i in range(5):
        h.add_user(f'msg{i}')
    # после 5 добавлений в истории должно быть 3 самых свежих
    assert len(h) == 3
    contents = [m['content'] for m in h.as_list()]
    assert contents == ['msg2', 'msg3', 'msg4']


def test_trim_by_chars_removes_old():
    h = History(limit_message=100, limit_chars=10)
    h.add_user('aaaaa')   # 5
    h.add_user('bbbbb')   # 10 - суммарно
    h.add_user('ccccc')   # 15 - перевалили, должны удалить старое
    contents = [m['content'] for m in h.as_list()]
    assert 'aaaaa' not in contents
    assert 'ccccc' in contents


def test_trim_by_chars_single_long_message_cut_left():
    h = History(limit_message=100, limit_chars=5)
    h.add_user('abcdefghij')  # длина 10, лимит 5
    contents = [m['content'] for m in h.as_list()]
    assert contents == ['fghij']


def test_reset():
    h = History(limit_message=10, limit_chars=1000)
    h.add_user('1')
    h.add_assistant('2')
    h.reset()
    assert h.as_list() == []
    assert len(h) == 0


def test_pop_last():
    h = History(limit_message=10, limit_chars=1000)
    h.add_user('x')
    h.pop_last()
    assert h.as_list() == []
    # pop на пустой истории не должен падать
    h.pop_last()
