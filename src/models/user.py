from .question import Question
from .question_set_factory import QuestionSet, InitialQuestionSetFactory, ChooseQuestionSetFactory, DiabetesQuestionSetFactory
from vars import base_api_url

import time
import requests

from linebot import LineBotApi
from linebot.models import TextSendMessage


initial_question_set_factory = InitialQuestionSetFactory()
choose_question_set_factory = ChooseQuestionSetFactory()
diabetes_question_set_factory = DiabetesQuestionSetFactory()


class User(object):
    def __init__(self, timeout: float) -> None:
        self._question_set = initial_question_set_factory.generate()
        self._index = 0
        self._timeout = timeout
        self._last_answer_time = time.time()
        self._is_end = False
        self._is_ready = False

    @property
    def is_ready(self) -> bool:
        return self._is_ready
    
    def make_ready(self) -> None:
        self._is_ready = True

    @property
    def is_end(self) -> bool:
        return self._is_end

    @property
    def is_timeout(self) -> bool:
        return time.time() - self._last_answer_time > self._timeout
    
    def reset(self) -> None:
        self._question_set = initial_question_set_factory.generate()
        self._index = 0
        self._last_answer_time = time.time()
        self._is_end = False
        self._is_ready = False

    @property
    def arrived_at_last_question(self) -> bool:
        return self._index >= len(self._question_set.questions) - 1

    @property
    def current_question(self) -> Question:
        return self._question_set.questions[self._index]
    
    def goto_next_question(self) -> None:
        self._index += 1

    def finalize(self, line_bot_api: LineBotApi, reply_token: str) -> None:
        if self._question_set.key == QuestionSet.KEY_TEST:
            if self.current_question.ans == "0":
                self._is_end = True
            elif self.current_question.ans == "1":
                self._question_set = choose_question_set_factory.generate()
                self._index = 0
        elif self._question_set.key == QuestionSet.KET_CHOOSE:
            if self.current_question.ans == "1":
                self._question_set = diabetes_question_set_factory.generate()
                self._index = 0
            else:
                self._is_end = True
        elif self._question_set.key == QuestionSet.KEY_DIABETES:
            request_data = {(question.key, question.ans) for question in self._question_set.questions}
            api_url = f"{base_api_url}/predict/diabetes"
            try:
                response = requests.post(api_url, json=request_data, headers={'Content-type': 'application/json'})
                response.raise_for_status()

                response_data = response.json()

                have_diabetes = response_data.get('have_diabetes', None)
                diabetes_percentage = response_data.get('diabetes_percentage', None)

                if have_diabetes is None or diabetes_percentage is None:
                    raise ValueError("Response error!")

                result = "没有糖尿病" if have_diabetes is False else "有糖尿病"
                line_bot_api.reply_message(reply_token, [
                    TextSendMessage(text=f"{result}"),
                    TextSendMessage(text=f"糖尿病機率:{diabetes_percentage:.2f}%"),
                    TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔")
                ])
                self._is_end = True
            except (Exception, requests.HTTPError):
                line_bot_api.reply_message(reply_token, [
                    TextSendMessage(text="伺服端錯誤，請稍後再試。")
                ])