class NoKeyError(Exception):
    """Наследую исключение для конкретной задачи."""

    def __init__(self, *args):
        """Вызывается при создании экземпляра."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Вызывается при выводе экземпляра на экран."""
        if self.message:
            return 'NoKeyError, {0} '.format(self.message)
        else:
            return 'NoKeyError, ключ не найден'


class NoConnectionError(Exception):
    """Наследую исключение для конкретной задачи."""

    def __init__(self, *args):
        """Вызывается при создании экземпляра."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Вызывается при выводе экземпляра на экран."""
        if self.message:
            return 'NoConnectionError {0} '.format(self.message)
        else:
            return 'NoConnectionError, не упешный запрос ресурса'


class No200Error(Exception):
    """Наследую исключение для конкретной задачи."""

    def __init__(self, *args):
        """Вызывается при создании экземпляра."""
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        """Вызывается при выводе экземпляра на экран."""
        if self.message:
            return 'No200Error{0} '.format(self.message)
        else:
            return 'No200Error, код ответа отличен от 200'
