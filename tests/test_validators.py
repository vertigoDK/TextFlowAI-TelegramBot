import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.utils.validators import validate_telegram_id
from app.core.exceptions.user import InvalidTelegramID


def test_validate_telegram_id_valid():
    """Valid telegram IDs should not raise an exception."""
    # Typical valid 9- and 10-digit IDs
    validate_telegram_id(123456789)
    validate_telegram_id(1234567890)


@pytest.mark.parametrize(
    "telegram_id",
    [
        -1,  # negative
        0,  # zero
        12345678,  # too short (8 digits)
        12345678901,  # too long (11 digits)
        "123456789",  # not an int
        123.456,  # float
    ],
)
def test_validate_telegram_id_invalid(telegram_id):
    """Invalid telegram IDs should raise InvalidTelegramID."""
    with pytest.raises(InvalidTelegramID):
        validate_telegram_id(telegram_id)
