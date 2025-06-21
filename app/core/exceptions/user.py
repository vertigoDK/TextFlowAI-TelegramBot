from .base import TextFlowException


class UserNotFound(TextFlowException):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")


class UserLimitExceeded(TextFlowException):
    def __init__(self, user_requests_count: int, limit_requests: int) -> None:
        self.user_request_count = user_requests_count
        self.limit_requests = limit_requests
        super().__init__(
            f"User requests count {user_requests_count} exceeded limit {limit_requests}"
        )


class InvalidTelegramID(TextFlowException):
    def __init__(self) -> None:
        super().__init__("Telegram ID must be a 10 signs number")
