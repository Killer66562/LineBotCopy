class AnswerStatus(object):
    def __init__(self, ans_is_valid: bool, err_msg: str = "") -> None:
        self._ans_is_valid = ans_is_valid
        self._err_msg = err_msg

    @property
    def ans_is_valid(self) -> bool:
        return self._ans_is_valid
    
    @property
    def err_msg(self) -> bool:
        return self._err_msg