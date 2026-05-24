import json
from datetime import UTC, datetime
from functools import wraps
from typing import Any, ParamSpec, Protocol, TypeVar
from urllib.request import urlopen

INVALID_CRITICAL_COUNT = "Breaker count must be positive integer!"
INVALID_RECOVERY_TIME = "Breaker recovery time must be positive integer!"
VALIDATIONS_FAILED = "Invalid decorator args."
TOO_MUCH = "Too much requests, just wait."


P = ParamSpec("P")
R_co = TypeVar("R_co", covariant=True)


class CallableWithMeta(Protocol[P, R_co]):
    __name__: str
    __module__: str

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R_co: ...


class BreakerError(Exception):
    def __init__(self, func_name: str, block_time: datetime) -> None:
        super().__init__(TOO_MUCH)
        self.func_name = func_name
        self.block_time = block_time


def _validate_args(critical_count: int, time_to_recover: int) -> None:
    errors: list[ValueError] = []
    if not isinstance(critical_count, int) or critical_count <= 0:
        errors.append(ValueError(INVALID_CRITICAL_COUNT))
    if not isinstance(time_to_recover, int) or time_to_recover <= 0:
        errors.append(ValueError(INVALID_RECOVERY_TIME))
    if errors:
        raise ExceptionGroup(VALIDATIONS_FAILED, errors)


class CircuitBreaker:
    def __init__(
        self,
        critical_count: int = 5,
        time_to_recover: int = 30,
        triggers_on: type[Exception] = Exception,
    ) -> None:
        _validate_args(critical_count, time_to_recover)
        self._critical_count = critical_count
        self._time_to_recover = time_to_recover
        self._triggers_on = triggers_on
        self._failures = 0
        self._blocked_at: datetime | None = None

    def __call__(self, func: CallableWithMeta[P, R_co]) -> CallableWithMeta[P, R_co]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R_co:
            now = datetime.now(tz=UTC)
            if self._is_blocked(now):
                raise self._make_error(func)
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                self._handle_failure(func, exc)
                raise
            self._failures = 0
            return result

        return wrapper

    def _is_blocked(self, now: datetime) -> bool:
        if self._blocked_at is None:
            return False
        elapsed = (now - self._blocked_at).total_seconds()
        if elapsed >= self._time_to_recover:
            self._blocked_at = None
            self._failures = 0
            return False
        return True

    def _make_error(self, func: CallableWithMeta[P, R_co]) -> BreakerError:
        full_name = f"{func.__module__}.{func.__name__}"
        block_time = self._blocked_at or datetime.now(tz=UTC)
        return BreakerError(func_name=full_name, block_time=block_time)

    def _handle_failure(self, func: CallableWithMeta[P, R_co], exc: BaseException) -> None:
        if not isinstance(exc, self._triggers_on):
            return
        self._failures += 1
        if self._failures < self._critical_count:
            return
        self._blocked_at = datetime.now(tz=UTC)
        raise self._make_error(func) from exc


def get_comments(post_id: int) -> Any:
    """
    Получает комментарии к посту

    Args:
        post_id (int): Идентификатор поста

    Returns:
        list[dict[int | str]]: Список комментариев
    """
    response = urlopen(f"https://jsonplaceholder.typicode.com/comments?postId={post_id}")
    return json.loads(response.read())


if __name__ == "__main__":
    circuit_breaker = CircuitBreaker(5, 30, Exception)
    comments = circuit_breaker(get_comments)(1)
