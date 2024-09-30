from abc import ABC
from .user import User


class UserBoard(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._users: dict[str, User] = {}

    def is_user_exist(self, user_id: str) -> bool:
        return False if self._users.get(user_id) is None else True

    def add_user(self, user_id: str):
        self._users[user_id] = User(timeout=300)

    def get_user(self, user_id: str) -> User:
        return self._users.get(user_id)
    
    def remove_user(self, user_id: str) -> None:
        user = self.get_user(user_id=user_id)
        if user is not None:
            self._users.pop(user_id)
    
