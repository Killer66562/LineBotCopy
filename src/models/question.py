from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction

from utils import is_int, is_float


class Question(ABC):
    def __init__(self, title: str, key: str, allowed_ans_list: list[Any] = [], check_float: bool = False, check_int: bool = False, check_positive: bool = False) -> None:
        self._title = title
        self._key = key
        self._ans = None
        self._allowed_ans_list = allowed_ans_list
        self._check_float = check_float
        self._check_int = check_int
        self._check_positive = check_positive
        self._is_asked = False

    @property
    def is_asked(self) -> bool:
        return self._is_asked

    @property
    def key(self) -> str:
        return self._key

    @property
    def ans(self) -> Any:
        return self._ans

    @abstractmethod
    def ask(self, line_bot_api: LineBotApi, reply_token: str):
        pass

    def answer(self, line_bot_api: LineBotApi, reply_token: str, ans: str) -> bool:
        '''
        Return True if the answer if valid else False
        '''
        if self._check_float:
            if not is_float(ans):
                try:
                    line_bot_api.reply_message(
                        reply_token=reply_token, 
                        messages=[TextSendMessage(text="請輸入一個數字")]
                    )
                    return False
                except:
                    return False
            
            ans = float(ans)

            if self._check_positive and not ans > 0:
                try:
                    line_bot_api.reply_message(
                        reply_token=reply_token, 
                        messages=[TextSendMessage(text="請輸入一個正數")]
                    )
                    return False
                except:
                    return False

        elif self._check_int:
            if not is_int(ans):
                try:
                    line_bot_api.reply_message(
                        reply_token=reply_token, 
                        messages=[TextSendMessage(text="請輸入一個整數")]
                    )
                    return False
                except:
                    return False
            
            ans = int(ans)

            if self._check_positive and not ans > 0:
                try:
                    line_bot_api.reply_message(
                        reply_token=reply_token, 
                        messages=[TextSendMessage(text="請輸入一個正整數")]
                    )
                    return False
                except:
                    return False

        if self._allowed_ans_list and ans not in self._allowed_ans_list:
            try:
                line_bot_api.reply_message(
                    reply_token=reply_token, 
                    messages=[TextSendMessage(text="請輸入一個正整數")]
                )
                return False
            except Exception:
                return False
        
        self._ans = ans
        return True


class TextQuestion(Question):
    def __init__(self, title: str, key: str, allowed_ans_list: list[Any] = [], check_float: bool = False, check_int: bool = False, check_positive: bool = False) -> None:
        super().__init__(title, key, allowed_ans_list, check_float, check_int, check_positive)

    def ask(self, line_bot_api: LineBotApi, reply_token: str):
        line_bot_api.reply_message(
            reply_token=reply_token, 
            messages=[TextSendMessage(text=self._title)]
        )
        self._is_asked = True


class ButtonQuestionOption(object):
    def __init__(self, label: str, data: str) -> None:
        self._label = label
        self._data = data

    @property
    def label(self) -> str:
        return self._label
    
    @property
    def data(self) -> str:
        return self._data
    

class ButtonQuestion(Question):
    def __init__(self, title: str, key: str, introduction: str = "", options: list[ButtonQuestionOption] = [], allowed_ans_list: list[Any] = [], check_float: bool = False, check_int: bool = False, check_positive: bool = False) -> None:
        super().__init__(title, key, allowed_ans_list, check_float, check_int, check_positive)
        self._introduction = introduction
        self._options = options

    def ask(self, line_bot_api: LineBotApi, reply_token: str):
        actions = [PostbackAction(label=option.label, data=option.data) for option in self._options]
        template_message = TemplateSendMessage(
            alt_text= "請輸入" + self._title,
            template=ButtonsTemplate(
                title=self._title,
                text=self._introduction,
                actions=actions
            )
        )
        line_bot_api.reply_message(reply_token=reply_token, messages=[template_message])
        self._is_asked = True