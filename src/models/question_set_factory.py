from abc import ABC, abstractmethod
from .question import ButtonQuestionOption, Question, TextQuestion, ButtonQuestion
from .check_strategy import IntCheckStrategy, FloatCheckStrategy, InListCheckStrategy, CompareCheckStrategy, CompareMethod


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
        return self._questions


class QuestionSetFactory(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def generate(self) -> QuestionSet:
        pass


class InitialQuestionSetFactory(QuestionSetFactory):
    __INITIAL_QUES_ANS_CHECK_STRATEGY = [InListCheckStrategy(["0", "1"])]
    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> QuestionSet:
        options = [ButtonQuestionOption(label="是", data="1"), ButtonQuestionOption(label="否", data="0")]
        questions = [ButtonQuestion(title="是否進行疾病預測", key="", introduction="您好，我是健康智能管家。\n請問是否進行疾病預測呢?", options=options, 
                                    ans_check_strategies=self.__INITIAL_QUES_ANS_CHECK_STRATEGY)]
        return QuestionSet(
            key=QuestionSet.KEY_TEST, 
            questions=questions
        )
    

class ChooseQuestionSetFactory(QuestionSetFactory):
    __CHOOSE_QUES_ANS_CHECK_STRATEGIES = [InListCheckStrategy(["1", "2", "3"])]
    def __init__(self) -> None:
        super().__init__()
    
    def generate(self) -> QuestionSet:
        options = [ButtonQuestionOption(label="糖尿病", data="1"), ButtonQuestionOption(label="高血壓", data="2"), ButtonQuestionOption(label="心臟病", data="3")]
        questions = [ButtonQuestion(title="要預測的疾病", key="", introduction="請選擇要預測的疾病", options=options,
                                    ans_check_strategies=self.__CHOOSE_QUES_ANS_CHECK_STRATEGIES)]
        return QuestionSet(
            key=QuestionSet.KET_CHOOSE, 
            questions=questions
        )
    

class DiabetesQuestionSetFactory(QuestionSetFactory):
    __GENDER_QUEST_ANS_CHECK_STRATEGIES = [IntCheckStrategy(), InListCheckStrategy([0, 1])]
    __AGE_QUEST_ANS_CHECK_STRATEGIES = [IntCheckStrategy(), CompareCheckStrategy(method=CompareMethod.BT, value=0)]
    __BMI_QUEST_ANS_CHECK_STRATEGIES = [FloatCheckStrategy(), CompareCheckStrategy(method=CompareMethod.BT, value=0)]
    __HBA1C_QUEST_ANS_CHECK_STRATEGIES = [FloatCheckStrategy(), CompareCheckStrategy(method=CompareMethod.BT, value=0)]
    __BS_QUEST_ANS_CHECK_STRATEGIES = [IntCheckStrategy(), CompareCheckStrategy(method=CompareMethod.BT, value=0)]
    def __init__(self) -> None:
        super().__init__()

    def generate(self) -> QuestionSet:
        gender_options = [ButtonQuestionOption(label="男", data="0"), ButtonQuestionOption(label="女", data="1")]
        gender_question = ButtonQuestion(title="性別", key="gender", introduction="請選擇性別", options=gender_options,
                                         ans_check_strategies=self.__GENDER_QUEST_ANS_CHECK_STRATEGIES)
        age_question = TextQuestion(title="年齡", key="age",
                                    ans_check_strategies=self.__AGE_QUEST_ANS_CHECK_STRATEGIES)
        bmi_question = TextQuestion(title="BMI", key="bmi",
                                    ans_check_strategies=self.__BMI_QUEST_ANS_CHECK_STRATEGIES)
        hba1c_question = TextQuestion(title="hba1c(%)", key="hba1c",
                                      ans_check_strategies=self.__HBA1C_QUEST_ANS_CHECK_STRATEGIES)
        blood_sugar_question = TextQuestion(title="血糖值(mg/dL)", key="blood_sugar",
                                            ans_check_strategies=self.__BS_QUEST_ANS_CHECK_STRATEGIES)
        questions=[gender_question, age_question, bmi_question, hba1c_question, blood_sugar_question]
        return QuestionSet(
            key=QuestionSet.KEY_DIABETES, 
            questions=questions
        )