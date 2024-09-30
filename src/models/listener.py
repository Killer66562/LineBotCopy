from abc import ABC, abstractmethod

class Listener(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def on_called(self) -> None:
        pass