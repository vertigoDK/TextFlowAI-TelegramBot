from typing import Any

def tryToInt(string_number: str) -> int | None:
    try:
        return int(string_number)
    except ValueError:
        return None

def greet(name: str) -> str:
    return "fds"

response: Any = greet(name="Denis")

print(tryToInt(response))