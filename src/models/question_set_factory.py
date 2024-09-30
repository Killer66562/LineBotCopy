from abc import ABC, abstractmethod
from .question import ButtonQuestionOption, Question, TextQuestion, ButtonQuestion


class QuestionSet(object):
    KEY_TEST = "test"
    KET_CHOOSE = "choose"
    KEY_DIABETES = "diabetes"
    KEY_HEART_DISEASE = "heart_disease"
    KEY_HYPERTENSION = "hypertension"
    def __init__(self, key: str, questions: list[Question]) -> None:
        self._key = key
        self._questions = questions

    @property
    def key(self) -> str:
        return self._key

    @property
    def questions(self) -> list[Question]:
        return self.questions


class QuestionSetFactory(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self) -> QuestionSet:
        pass


class InitialQuestionSetFactory(QuestionSetFactory):
    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> QuestionSet:
        options=[ButtonQuestionOption(label="是", data="1"), ButtonQuestionOption(label="否", data="0")], 
        questions=[ButtonQuestion(title="是否進行疾病預測", key="", introduction="您好，我是健康智能管家。\n請問是否進行疾病預測呢?", options=options)]
        return QuestionSet(
            key=QuestionSet.KEY_TEST, 
            questions=questions
        )
    

class ChooseQuestionSetFactory(QuestionSetFactory):
    def __init__(self) -> None:
        super().__init__()
    
    def generate(self) -> QuestionSet:
        options=[ButtonQuestionOption(label="糖尿病", data="1"), ButtonQuestionOption(label="高血壓", data="2"), ButtonQuestionOption(label="心臟病", data="3")]
        questions=[ButtonQuestion(title="要預測的疾病", key="", introduction="請選擇要預測的疾病", options=options)]
        return QuestionSet(
            key=QuestionSet.KET_CHOOSE, 
            questions=questions
        )
    

class DiabetesQuestionSetFactory(QuestionSetFactory):
    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> QuestionSet:
        gender_options = [ButtonQuestionOption(label="男", data="0"), ButtonQuestionOption(label="女", data="1")]
        gender_question = ButtonQuestion(title="性別", key="gender", introduction="請選擇性別", allowed_ans_list=[0, 1], check_int=True, options=gender_options)
        age_question = TextQuestion(title="年齡", key="age", check_int=True, check_positive=True)
        bmi_question = TextQuestion(title="BMI", key="bmi", check_float=True, check_positive=True)
        blood_sugar_question = TextQuestion(title="血糖值(mg/dL)", check_int=True, check_positive=True)
        questions=[gender_question, age_question, bmi_question, blood_sugar_question]
        return QuestionSet(
            key=QuestionSet.KEY_DIABETES, 
            questions=questions
        )