import random
from typing import Sequence, TypeVar


T = TypeVar("T")


class TeamService:
    TEAM_SIZE = 5
    REQUIRED_PLAYERS = TEAM_SIZE * 2

    def split(self, players: Sequence[T]) -> tuple[list[T], list[T]]:
        if len(players) != self.REQUIRED_PLAYERS:
            raise ValueError(f"expected {self.REQUIRED_PLAYERS} players")
        shuffled = list(players)
        random.shuffle(shuffled)
        return shuffled[: self.TEAM_SIZE], shuffled[self.TEAM_SIZE :]

    def split_numbers(self) -> tuple[list[int], list[int]]:
        blue, red = self.split(range(1, self.REQUIRED_PLAYERS + 1))
        return sorted(blue), sorted(red)
