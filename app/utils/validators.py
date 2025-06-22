from app.core.exceptions.user import InvalidTelegramID


def validate_telegram_id(telegram_id: int) -> None:
    """Валидация Telegram ID (должен быть положительным числом)"""

    if not isinstance(telegram_id, int) or telegram_id <= 0:
        raise InvalidTelegramID()

    # Telegram ID обычно от 9 до 10 цифр
    if not (100000000 <= telegram_id <= 9999999999):
        raise InvalidTelegramID()
