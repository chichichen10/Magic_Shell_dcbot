import datetime
from typing import Any


class BotRepository:
    def __init__(self, database: Any):
        self._db = database

    def _get(self, key: str, default: Any) -> Any:
        try:
            return self._db[key]
        except KeyError:
            self._db[key] = default
            return default

    def initialize(self, bot_name: str) -> None:
        self._db["bot_name"] = bot_name
        month = datetime.datetime.now().month
        token_state = self._get("token", [month, 0])
        if token_state[0] != month:
            self._db["token"] = [month, 0]
        self._get("mode", "1")

    def get_mode(self) -> str:
        return str(self._get("mode", "1"))

    def get_bot_name(self) -> str:
        return str(self._get("bot_name", "Unknown"))

    def get_token_usage(self) -> int:
        month = datetime.datetime.now().month
        token_state = list(self._get("token", [month, 0]))
        return int(token_state[1]) if token_state[0] == month else 0

    def get_nickname(self, display_name: str) -> str:
        key = "nickname_" + display_name
        try:
            return self._db[key]
        except KeyError:
            return display_name

    def add_token_usage(self, tokens: int) -> None:
        month = datetime.datetime.now().month
        token_state = list(self._get("token", [month, 0]))
        if token_state[0] != month:
            token_state = [month, 0]
        token_state[1] += tokens
        self._db["token"] = token_state

    def set_verbose_level(self, level: str) -> None:
        self._db["verbose"] = level
