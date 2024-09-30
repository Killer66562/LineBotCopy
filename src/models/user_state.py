from typing import Any

from models.question import TextQuestionMetadata, ButtonQuestionMetadata, TextQuestion, ButtonQuestion, Question
from .listener import Listener


class UserState(Listener):
    def __init__(self, line_bot_api) -> None:
        super().__init__()
        self._line_bot_api = line_bot_api
        self._questions = []
        self._index = 0
        self._kv_metadata = {}

    @property
    def current_question(self) -> Question:
        return self._questions[self._index]
    
    @property
    def no_more_questions(self) -> bool:
        return self._index >= len(self._questions)
    
    def _goto_next_question(self) -> None:
        self._index += 1

    def register_key_value(self, key: str, value: Any, metadatas):
        if self._kv_metadata.get(key) is None:
            self._kv_metadata[key] = {}
        self._kv_metadata[key][value] = metadatas

    def add_question(self, metadata) -> bool:
        if isinstance(metadata, TextQuestionMetadata):
            question = TextQuestion(metadata, self._line_bot_api)
            question.add_listener(self)
            self._questions.append(question)
            return True
        elif isinstance(metadata, ButtonQuestionMetadata):
            question = ButtonQuestion(metadata, self._line_bot_api)
            question = TextQuestion(metadata, self._line_bot_api)
            question.add_listener(self)
            return True
        else:
            return False
        
    def on_called(self, reply_token) -> None:
        for key in self._kv_metadata:
            small_table = self._kv_metadata[key]
            if self.current_question.key == key:
                for key in small_table:
                    if self.current_question.value == key:
                        for metadata in small_table[key]:
                            self.add_question(metadata, self._line_bot_api)
        self._goto_next_question()
        self.current_question.ask(reply_token)

            

    