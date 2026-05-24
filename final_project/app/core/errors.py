class AppError(Exception):
    pass


class ConfigError(AppError):
    pass


class FileTooBigError(AppError):
    pass


class LLMError(AppError):
    pass
