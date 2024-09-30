from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, PostbackEvent

import pandas as pd
import requests
import os
import logging
import asyncio

# 载入 .env 文件
load_dotenv()

app = Flask(__name__)

# Line API 驗證
access_token = os.getenv("LINE_ACCESS_TOKEN")
secret = os.getenv("LINE_SECRET")

base_api_url = os.getenv("BASE_API_URL").removesuffix("/")

line_bot_api = LineBotApi(access_token)  # token 確認
handler = WebhookHandler(secret)      # secret 確認

"""
接收並處理來自 Line 平台的 Webhook 請求。
獲取並驗證請求的簽名。
調用相應的處理函數處理請求數據。
在簽名驗證失敗時返回 400 錯誤碼。
"""
@app.route("/", methods=['POST'])
def webhook():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


# 定義 Question 類別, 方便問問題
class Question:
    def __init__(self, question_text):
        # 設定問題的文字內容
        self.question_text = question_text
    def ask_question(self, reply_token):
        raise NotImplementedError("這個方法應該在子類別實現")

class TextQuestion(Question):
    def __init__(self, question_text):
        # 初始化跟父類別相同
        super().__init__(question_text)

    def ask_question(self, reply_token):
        # 傳送文字問題
        message = TextSendMessage(text=self.question_text)
        # 使用 reply 方法傳送
        line_bot_api.reply_message(reply_token, message)
        
class ButtonQuestion(Question):
    def __init__(self, question_text, choices, introduction=None):
        super().__init__(question_text)
        self.introduction = introduction if introduction else "請選擇您的" + question_text
        self.choices = choices

    def ask_question(self, reply_token):
        actions = [PostbackAction(label=label, data=data) for label, data in self.choices]
        template_message = TemplateSendMessage(
            alt_text= "請輸入" + self.question_text,
            template=ButtonsTemplate(
                title=self.question_text,
                text=self.introduction,
                actions=actions
            )
        )
        line_bot_api.reply_message(reply_token, template_message)
class UserState:
    # 建構函式, 初始化用戶狀態, 紀錄 step, Question, data 
    def __init__(self, questions):
        self.step = 0
        self.questions = list(questions)
        self.data = []
        self.testType = None
# 紀錄用戶當前輸入狀態
user_state = {}
# 問題列表, 之後可以在更加簡化
introduction = ("您好，我是健康智能管家。\n"
                "您可以叫我阿瑄=U=\n"
                "請問是否進行疾病預測呢?")
introQuestions = [
    ButtonQuestion('是否進行疾病預測?', [('是', 'continue'), ('否', 'exit')], introduction),
    ButtonQuestion('請選擇預測項目', [('糖尿病', 'diabete'), ('中風', 'hypertension'), ('心臟病', 'heart_disease')])
]
diabeteQuestions = [
    ButtonQuestion('性別', [('男', '0'), ('女', '1')]),
    TextQuestion("請輸入年齡: "),
    TextQuestion("請輸入BMI: "),
    TextQuestion("請輸入HbA1c水平: "),
    TextQuestion("請輸入血糖水平: ")
]
hypertensionQuestions = [
    ButtonQuestion('性別', [('男', '0'), ('女', '1')]),
    TextQuestion("請輸入年齡: "),
    ButtonQuestion('是否有高血壓', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有心臟病', [('是', '1'), ('否', '0')]),
    ButtonQuestion('居住環境', [('鄉村', '1'), ('都市', '0')]),
    TextQuestion("請輸入血糖"),
    TextQuestion("請輸入BMI"),
    ButtonQuestion('抽菸史:', [('無', '0'), ('曾有', '1'), ('有', '2')] )
]
heartDiseaseQuestions = [
    ButtonQuestion('性別', [('男', '0'), ('女', '1')]),
    TextQuestion("請輸入年齡: "),
    TextQuestion("請輸入BMI: "),
    ButtonQuestion('是否有抽菸', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有飲酒(一個禮拜喝超過14杯)', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有中風', [('是', '1'), ('否', '0')]),
    ButtonQuestion('爬樓梯是否有困難', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有糖尿病', [('是', '1'), ('否', '0')]),
    ButtonQuestion('平常是否有進行工作外的身體活動', [('是', '1'), ('否', '0')]),
    TextQuestion("一天平均睡多少小時: "),
    ButtonQuestion('是否有氣喘', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有腎臟疾病', [('是', '1'), ('否', '0')]),
    ButtonQuestion('是否有皮膚癌', [('是', '1'), ('否', '0')])
]

# 初始化新的使用者
def initializeNewUser(reply_token, user_id):
    # 初始化
    user_state[user_id] = UserState(introQuestions)
    # 問第一個問題
    user_state[user_id].questions[0].ask_question(reply_token)
    
# 最後輸出, 根據使用者輸入預測結果
def process_final_input(reply_token, user_id):
    # 獲取使用者資料
    user_testType = user_state[user_id].testType
    user_data = user_state[user_id].data
    
    if user_testType == 'diabete':
        # 邏輯回歸預測
        user_input = {
            'gender': int(user_data[0]), 
            'age': int(user_data[1]), 
            'bmi': user_data[2], 
            'hba1c': user_data[3], 
            'blood_sugar': user_data[4]
        }

        # 傳至NAS並回傳預測結果
        api_url = f'{base_api_url}/predict/diabetes'
        try:
            response = requests.post(api_url, json=user_input, headers={'Content-type': 'application/json'})
            response.raise_for_status()

            response_data = response.json()
            logging.info(response_data)

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
        except (Exception, requests.HTTPError):
            line_bot_api.reply_message(reply_token, [
                TextSendMessage(text="伺服端錯誤，請稍後再試。")
            ])
    '''

    elif user_testType == 'hypertension':
        # 載入模型
        model = joblib.load('./stroke_prediction_model.pkl')

        
        #XGboost 預測
         #轉換成 DataFrame, 並加入標籤
        user_input = pd.DataFrame([user_data], columns=['gender', 
                                                        'age', 
                                                        'hypertension', 
                                                        'heart_disease', 
                                                        'Residence_type',
                                                        'avg_glucose_level',
                                                        'bmi',
                                                        'smoking_status'])
         # 全部轉換成 float 型態，以符合 xgboost 的輸入格式(不接受按鈕所產生的object值)
        user_input['gender'] = user_input['gender'].astype(float)
        user_input['hypertension'] = user_input['hypertension'].astype(float)
        user_input['heart_disease'] = user_input['heart_disease'].astype(float)
        user_input['Residence_type'] = user_input['Residence_type'].astype(float)
        user_input['smoking_status'] = user_input['smoking_status'].astype(float) 
         # 再轉換為 DMatrix 格式
        user_input = xgb.DMatrix(user_input)
        prediction_proba = model.predict(user_input)
        
        """
        # 傳至NAS並回傳預測結果
        api_url = 'http://120.107.172.113:8000/predict/hypertension'
        try:
            response = requests.post(api_url, json=user_input)#將字典型態的資料傳遞至NAS(因為json不接受DMatrix型態)
            response.raise_for_status()#在NAS部分先轉成DMatrix再丟入模型
            prediction_proba = response.json().get('prediction_proba', [0, 0])#最後回傳結果
        except requests.exceptions.RequestException as e:
            prediction_proba = [0, 0]  # 預設為[0, 0]，表示出錯錯
        """
        # 二分判斷
        result = "沒有中風" if prediction_proba[0] < 0.5 else "有中風" #prediction_proba[0] 是類別1的機率
        line_bot_api.reply_message(reply_token, [
            TextSendMessage(text=f"{result}"),
            TextSendMessage(text=f"中風機率:{prediction_proba[0] * 100:.2f}%"),
            TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔")
        ])


    elif user_testType == 'heart_disease':
        # 載入模型
        model = joblib.load('./HeartDisease_prediction_model.pkl')
        
        #年齡分布計算(AgeCategory位在user_data的第二個位置，所以index為1)
        if user_data[1] == 18 or user_data[1] == 19:
            user_data[1] = user_data[1] / 5 + 1
        elif user_data[1] >=80:
            user_data[1] = 16
        else:
            user_data[1] = user_data[1] / 5
        
        
        # 邏輯回歸預測
        user_input = pd.DataFrame([user_data], columns=['Sex',
                                                        'AgeCategory',
                                                        'BMI', 
                                                        'Smoking', 
                                                        'AlcoholDrinking', 
                                                        'Stroke', 
                                                        'DiffWalking',
                                                        'Diabetic',
                                                        'PhysicalActivity',
                                                        'SleepTime',
                                                        'Asthma',
                                                        'KidneyDisease',
                                                        'SkinCancer'])#轉成DataFrame格式
        prediction_proba = model.predict_proba(user_input)[0]#將轉成DataFrame格式的資料輸入進模型
        """
        # 傳至NAS並回傳預測結果
        api_url = 'http://120.107.172.113:8000/predict/heart_disease'
        try:
            response = requests.post(api_url, json=user_input)#將字典型態的資料傳遞至NAS(因為json不接受Dataframe型態)
            response.raise_for_status()#在NAS部分先轉成Dataframe再丟入模型
            prediction_proba = response.json().get('prediction_proba', [0, 0])#最後回傳結果
        except requests.exceptions.RequestException as e:
            prediction_proba = [0, 0]  # 預設為[0, 0]，表示出錯
        """
        # 二分判斷
        result = "没有心臟病" if prediction_proba[1] < 0.5 else "有心臟病"
        line_bot_api.reply_message(reply_token, [
            TextSendMessage(text=f"{result}"),
            TextSendMessage(text=f"心臟病機率:{prediction_proba[1]*100:.2f}%"),
            TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔")
        ])
    del user_state[user_id]
    '''
    
def EndPrediction(reply_token, user_id):
    line_bot_api.reply_message(reply_token, TextSendMessage(text="謝謝光臨!! 有需要都可以在叫我喔"))
    del user_state[user_id]

#下一個問題
def NextQuestion(reply_token, user_id):
    user_state[user_id].step += 1
    # 還沒到最後一個問題: 繼續問下一個問題
    if user_state[user_id].step < len(user_state[user_id].questions):
        user_state[user_id].questions[user_state[user_id].step].ask_question(reply_token)
    else:
        # 否則輸出最後結果
        process_final_input(reply_token, user_id)

# 正整數驗證
def validate_numeric_input(event, msg):
    try:
        msg_float = float(msg)
        if msg_float <= 0:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入大於 0 的有效數字"))
            return False
        return True
    except ValueError:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入正確的數字"))
        return False
    
# 用戶傳送訊息的時候做出的回覆
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    event_loop = asyncio.get_event_loop()
    fut = event_loop.run_in_executor(None, requests.get, base_api_url)
    ab = event_loop.run_until_complete(fut)

    logging.info(ab.content)

    user_id = event.source.user_id
    msg = event.message.text
    if msg == 'exit':
        EndPrediction(event.reply_token, user_id)
    # 初始化新的使用者 or 判斷輸入
    if user_id not in user_state:
        initializeNewUser(event.reply_token, user_id)
        return
    if isinstance(user_state[user_id].questions[user_state[user_id].step], ButtonQuestion):
        # 按鈕問題不應該輸入文字回答
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請選擇按鈕選項"))
        return
    # 數字驗證
    if not validate_numeric_input(event, msg):
        return
    # 將資料加入, 前往下一題
    # 驗證通過，加入正確資料，前往下一題目
    user_state[user_id].data.append(float(msg))
    NextQuestion(event.reply_token, user_id)
# 按鈕按下之後的回應
@handler.add(PostbackEvent)
def handle_postback(event):
    # 獲取使用者與回傳的按鈕資訊
    user_id = event.source.user_id
    postback_data = event.postback.data
    # 初始化新的使用者 or 判斷輸入
    if user_id not in user_state:
        initializeNewUser(event.reply_token, user_id)
        return
    if isinstance(user_state[user_id].questions[user_state[user_id].step], TextQuestion):
        # 文字問題不接受按鈕回答
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="請輸入數字"))
        return
    # 回答分支判斷, 可考慮建立一個讀路的函式處理
    if(postback_data == 'exit'):
        # 退出對話, 刪除使用者紀錄
        EndPrediction(event.reply_token, user_id)
    if(postback_data == 'diabete'):
        user_state[user_id].testType = 'diabete'
        user_state[user_id].questions.extend(diabeteQuestions)
        # 加入多個問題, 因此是 extend 而不是 append, 不需要使用指標解引用, python 會幫忙
    elif(postback_data == 'heart_disease'):
        user_state[user_id].testType = 'heart_disease'
        user_state[user_id].questions.extend(heartDiseaseQuestions)
    elif(postback_data == 'hypertension'):
        user_state[user_id].testType = 'hypertension'
        user_state[user_id].questions.extend(hypertensionQuestions)
    elif(postback_data != 'continue'):
        # 如果不是特別判斷的分支, 表示這是一般問題的回答, 將回傳的資料加入
        user_state[user_id].data.append(postback_data)
        
    NextQuestion(event.reply_token, user_id)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)