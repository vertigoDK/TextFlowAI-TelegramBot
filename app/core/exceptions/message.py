from .base import TextFlowException


class MessageNotFound(TextFlowException):
    """Исключение при попытке найти несуществующее сообщение"""

    pass


class InvalidMessageData(TextFlowException):
    """Исключение при некорректных данных сообщения"""

    pass


class MessageProcessingError(TextFlowException):
    """Исключение при ошибке обработки сообщения AI"""

    pass


class ContextTooLarge(TextFlowException):
    """Исключение когда контекст диалога превышает лимиты"""

    pass
