from abc import ABC, abstractmethod
from typing import Any
from enum import Enum


class CompareMethod(Enum):
    ST = "st"
    STE = "ste"
    BT = "be"
    BTE = "bte"
    EQ = "qu"
    

class CheckStrategy(ABC):
    @abstractmethod
    def check(self, value: Any) -> bool:
        pass

    @abstractmethod
    def transfer(self, value) -> Any:
        pass

    @property
    @abstractmethod
    def error_message(self) -> str:
        pass


class IntCheckStrategy(CheckStrategy):
    def check(self, value: Any) -> bool:
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def transfer(self, value: Any) -> Any:
        return int(value)
    
    @property
    def error_message(self) -> str:
        return "請輸入一個整數"
        

class FloatCheckStrategy(CheckStrategy):
    def check(self, value: Any) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False

    def transfer(self, value: Any) -> Any:
        return float(value)
    
    @property
    def error_message(self) -> str:
        return "請輸入一個浮點數"
        

class InListCheckStrategy(CheckStrategy):
    def __init__(self, check_list: list[Any]) -> None:
        super().__init__()
        self._check_list = check_list

    def check(self, value: Any) -> bool:
        return value in self._check_list
    
    def transfer(self, value) -> Any:
        return value
    
    @property
    def error_message(self) -> str:
        check_str = ", ".join(map(str, self._check_list))
        return f"請輸入[{check_str}]中的其中一個值"
    

class CompareCheckStrategy(CheckStrategy):
    def __init__(self, method: CompareMethod, value: int | float) -> None:
        self._method = method
        self._value = value

    def check(self, value: Any) -> bool:
        print(type(value))
        print(value)
        if not isinstance(value, int) or not isinstance(value, float):
            return False
        if self._method == CompareMethod.EQ and not value == self._value:
            return False
        if self._method == CompareMethod.BT and not value > self._value:
            return False
        if self._method == CompareMethod.BTE and not value >= self._value:
            return False
        if self._method == CompareMethod.ST and not value < self._value:
            return False
        if self._method == CompareMethod.STE and not value <= self._value:
            return False
        return True
    
    def transfer(self, value) -> Any:
        return value

    @property
    def error_message(self) -> str:
        if self._method == CompareMethod.EQ:
            return f"請輸入{self._value}"
        if self._method == CompareMethod.BT:
            return f"請輸入大於{self._value}的值"
        if self._method == CompareMethod.BTE:
            return f"請輸入大於等於{self._value}的值"
        if self._method == CompareMethod.ST:
            return f"請輸入小於{self._value}的值"
        if self._method == CompareMethod.STE:
            return f"請輸入小於等於{self._value}的值"
        return "無法比較"
        