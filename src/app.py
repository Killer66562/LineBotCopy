from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import WebhookHandler, LineBotApi
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, PostbackEvent

import os

from models import UserBoard, TextQuestion, ButtonQuestion
from vars import access_token, secret

# 载入 .env 文件
load_dotenv()

app = Flask(__name__)

base_api_url = os.getenv("BASE_API_URL").removesuffix("/")

line_bot_api = LineBotApi(access_token)  # token 確認
handler = WebhookHandler(secret)      # secret 確認

user_board = UserBoard()

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
    
# 用戶傳送訊息的時候做出的回覆
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = str(event.source.user_id)
    msg = str(event.message.text)
    reply_token = str(event.reply_token)

    if msg == 'exit' and user_board.is_user_exist(user_id):
        user_board.remove_user(user_id)
        return None
    
    #使用者不存在時，新增一名使用者。
    if not user_board.is_user_exist(user_id):
        user_board.add_user(user_id)
        
    user = user_board.get_user(user_id)

    #使用者回答問題的間隔過長或已結束一次預測時，重設使用者狀態。
    if user.is_timeout or user.is_end:
        user.reset()

    '''
    如果使用者當前的問題尚未被問出
    讓機器人先問問題
    待下一次使用者回應時
    再對該問題進行回覆
    '''
    if not user.current_question.is_asked:
        user.current_question.ask(line_bot_api=line_bot_api, reply_token=reply_token)
        return None

    if isinstance(user.current_question, ButtonQuestion):
        # 按鈕問題不應該輸入文字回答
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請選擇按鈕選項"))
        return None
    
    ans_is_valid = user.current_question.answer(line_bot_api=line_bot_api, reply_token=reply_token, ans=msg)
    if not ans_is_valid:
        return None
    
    if not user.arrived_at_last_question:
        user.goto_next_question()
    else:
        user.finalize(line_bot_api=line_bot_api, reply_token=reply_token)
        if not user.is_end:
            user.current_question.ask(line_bot_api=line_bot_api, reply_token=reply_token)
   
# 按鈕按下之後的回應
@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    # 獲取使用者與回傳的按鈕資訊
    postback_data = str(event.postback.data)
    user_id = str(event.source.user_id)
    reply_token = str(event.reply_token)

    if postback_data == 'exit' and user_board.is_user_exist(user_id):
        user_board.remove_user(user_id)
        return None
    
    if not user_board.is_user_exist(user_id):
        return None
        
    user = user_board.get_user(user_id)

    #使用者回答問題的間隔過長或已結束一次預測時，重設使用者狀態。
    if user.is_timeout or user.is_end:
        user.reset()

    '''
    如果使用者當前的問題尚未被問出
    讓機器人先問問題
    待下一次使用者回應時
    再對該問題進行回覆
    '''

    if not user.current_question.is_asked:
        user.current_question.ask(line_bot_api=line_bot_api, reply_token=reply_token)
        return None

    if isinstance(user.current_question, TextQuestion):
        # 文字問題不應該按按鈕回答
        line_bot_api.reply_message(reply_token, TextSendMessage(text="請輸入文字"))
        return None
    
    ans_is_valid = user.current_question.answer(line_bot_api=line_bot_api, reply_token=reply_token, ans=postback_data)
    if not ans_is_valid:
        return None
    
    if not user.arrived_at_last_question:
        user.goto_next_question()
    else:
        user.finalize(line_bot_api=line_bot_api, reply_token=reply_token)
        if not user.is_end:
            user.current_question.ask(line_bot_api=line_bot_api, reply_token=reply_token)
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)