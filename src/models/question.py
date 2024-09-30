from abc import ABC, abstractmethod
from typing import Any

from linebot import LineBotApi
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent

from models.listener import Listener
from utils import is_int, is_float


class QuestionMetadata(object):
    def __init__(self, title: str, key: str) -> None:
        self._title = title
        self._key = key

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def key(self) -> str:
        return self._key


class TextQuestionMetadata(QuestionMetadata):
    def __init__(self, title: str, key: str) -> None:
        super().__init__(title, key)


class ButtonQuestionOption(object):
    def __init__(self, label: str, value: str) -> None:
        self._label = label
        self._value = value

    @property
    def label(self) -> str:
        return self._label
    
    @property
    def value(self) -> str:
        return self._value


class ButtonQuestionMetadata(QuestionMetadata):
    def __init__(self, title: str, introduction: str, key: str, options: list[ButtonQuestionOption]) -> None:
        super().__init__(title, key)
        self._introduction = introduction
        self._options = options

    @property
    def introduction(self) -> str:
        return self._introduction
    
    @property
    def options(self) -> list[ButtonQuestionOption]:
        return self._options
    

class Question(ABC):
    def __init__(self, metadata: QuestionMetadata, line_bot_api: LineBotApi) -> None:
        super().__init__()
        self._metadata = metadata
        self._line_bot_api = line_bot_api
        self._value: Any = None
        self._listeners: list[Listener] = []

    @property
    def title(self) -> str:
        return self._metadata.title

    @property
    def key(self) -> str:
        return self._metadata._key
    
    @property
    def value(self) -> Any:
        return self._value

    @abstractmethod
    def ask(self, reply_token: str) -> None:
        pass

    @abstractmethod
    def answer(self, value: str, reply_token: str) -> None:
        pass

    def add_listener(self, listener: Listener):
        if listener not in self._listeners:
            self._listeners.append(listener)


class TextQuestion(Question):
    def __init__(self, metadata: TextQuestionMetadata, line_bot_api: LineBotApi) -> None:
        super().__init__(metadata, line_bot_api)
        self._metadata = metadata


class ButtonQuestion(Question):
    def __init__(self, metadata: ButtonQuestionMetadata, line_bot_api: LineBotApi) -> None:
        super().__init__(metadata, line_bot_api)
        self._metadata = metadata

    @property
    def introduction(self) -> str:
        return self._metadata.introduction
    
    @property
    def options(self) -> list[ButtonQuestionOption]:
        return self._metadata.options

    def ask(self, reply_token: str) -> None:
        actions = [PostbackAction(label=option.label, data=option.value) for option in self.options]
        template_message = TemplateSendMessage(
            alt_text=f"請選擇{self.title}",
            template=ButtonsTemplate(
                title=self.title,
                text=self.introduction,
                actions=actions
            )
        )
        self._line_bot_api.reply_message(reply_token, template_message)

    def answer(self, value: str, reply_token: str, check_int: bool = False, check_float: bool = False) -> None:
        if check_float is True:
            if is_float(value) is False:
                pass
        
        if check_int is True:
            if is_int(value) is False:
                pass

        for listener in self._listeners:
            listener.on_called(reply_token)

   
class PredictOrNotQuestion(ButtonQuestion):
    def __init__(self, line_bot_api: LineBotApi, title: str, introduction: str, key: str, options: list[ButtonQuestionOption]) -> None:
        super().__init__(line_bot_api, title, introduction, key, options)
        self._introduction = "您好，我是健康智能管家。\n您可以叫我阿瑄=U=\n請問是否進行疾病預測呢?"
        self._options = [
            ButtonQuestionOption(label="是", value="0"), 
            ButtonQuestionOption(label="是", value="1"), 
        ]

    

        
