from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str


class History:
    def __init__(self, limit_message: int, limit_chars: int) -> None:
        self.limit_message = limit_message
        self.limit_chars = limit_chars
        self._messages: list[Message] = []

    def add_user(self, text: str) -> None:
        self._add(Message('user', text))

    def add_assistant(self, text: str) -> None:
        self._add(Message('assistant', text))

    def reset(self) -> None:
        self._messages = []

    def pop_last(self) -> None:
        if self._messages:
            self._messages.pop()

    def __len__(self) -> int:
        return len(self._messages)

    def as_list(self) -> list[dict]:
        return [{'role': m.role, 'content': m.content} for m in self._messages]

    def _add(self, msg: Message) -> None:
        # сначала добавляем, потом подрезаем
        self._messages.append(msg)
        self._trim_by_count()
        self._trim_by_chars()

    def _trim_by_count(self) -> None:
        if len(self._messages) > self.limit_message:
            extra = len(self._messages) - self.limit_message
            self._messages = self._messages[extra:]

    def _trim_by_chars(self) -> None:
        # сначала удаляем самые старые сообщения, пока не уложимся в лимит.
        # если последнее само длиннее лимита - режем его слева.
        while len(self._messages) > 1 and self._total_chars() > self.limit_chars:
            self._messages.pop(0)
        if self._messages and self._total_chars() > self.limit_chars:
            last = self._messages[-1]
            keep = self.limit_chars
            if keep < 0:
                keep = 0
            last.content = last.content[-keep:]
            self._messages[-1] = last

    def _total_chars(self) -> int:
        total = 0
        for m in self._messages:
            total += len(m.content)
        return total
