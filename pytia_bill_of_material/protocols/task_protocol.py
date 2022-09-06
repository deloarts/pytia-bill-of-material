from typing import Protocol


class TaskProtocol(Protocol):
    def run(self) -> None:
        ...
