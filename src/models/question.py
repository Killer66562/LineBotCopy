from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction

from .check_strategy import CheckStrategy


class Question(ABC):
    def __init__(self, title: str, key: str, ans_check_strategies: list[CheckStrategy] = []) -> None:
        self._title = title
        self._key = key
        self._ans_check_strategies = ans_check_strategies
        self._ans = None
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
        ans_tmp = str(ans)
        for strategy in self._ans_check_strategies:
            if not strategy.check(ans_tmp):
                line_bot_api.reply_message(reply_token=reply_token, messages=TextSendMessage(text=strategy.error_message))
                return False
            ans_tmp = strategy.transfer(ans_tmp)
        self._ans = ans_tmp
        return True


class TextQuestion(Question):
    def __init__(self, title: str, key: str, ans_check_strategies: list[CheckStrategy] = []) -> None:
        super().__init__(title, key, ans_check_strategies)

    def ask(self, line_bot_api: LineBotApi, reply_token: str):
        line_bot_api.reply_message(
            reply_token=reply_token, 
            messages=TextSendMessage(text="請輸入"+self._title)
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
    def __init__(self, title: str, key: str, introduction: str = "", options: list[ButtonQuestionOption] = [], ans_check_strategies: list[CheckStrategy] = []) -> None:
        super().__init__(title, key, ans_check_strategies)
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
        line_bot_api.reply_message(reply_token=reply_token, messages=template_message)
        self._is_asked = True