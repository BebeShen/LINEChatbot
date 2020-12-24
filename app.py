from flask import Flask, request, abort 
# 代表著從flask這個module中引入Flask, request, abort
# REF:https://github.com/twtrubiks/python-notes/tree/master/configparser_tutorial
# import configparser
# config = configparser.ConfigParser()
# config.read("config.ini")
import os
import sys
import psycopg2
import model 
from dotenv import load_dotenv
load_dotenv()
import messageObeject
# from secret_settings import *

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, PostbackEvent, FollowEvent
)

app = Flask(__name__)

channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
DATABASE_URL = os.getenv("DATABASE_URL", None)
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
# conn.close()
# cur = conn.cursor()
# line_bot_api = LineBotApi(config['DEFAULT']['LINE_CHANNEL_ACCESS_TOKEN']) # 貼上你的line bot channel token
# handler = WebhookHandler(config['DEFAULT']['LINE_CHANNEL_SECRET'])
@app.route("/", methods=['GET'])
def hello_world():
		# 有人觸發了 / 這個路徑的時候就會呼叫此function並且執行
    return 'Hello World!'

# 此為 Webhook callback endpoint
@app.route("/callback", methods=['POST']) # 代表我們宣告了/callback這個路徑 只要有人訪問這個路徑系統就會進行處理
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
        # print(f"\nFSM STATE: {machine.state}")
        # print(f"REQUEST BODY: \n{body}")
        # response = machine.advance(event)
        # if response == False:
        #     send_text_message(event.reply_token, "Not Entering any State")
    return 'OK'
@handler.add(FollowEvent)
def handle_follow(event):
    app.logger.info("Got Follow event from:" + event.source.user_id)
    # Event day's greeting
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"歡迎使用子揚幫你點名小幫手，\n這個機器人可以幫你防疫點名，\n省去掃QRCode的時間！")
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    # 點名系統
    line_bot_api.push_message(
            event.source.user_id, TextSendMessage(text="進入點名系統")
        )
    app.logger.info("event.postback.data:" +  event.postback.data)
    if event.postback.data == '資訊系館65304':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data)
        )
    elif event.postback.data == '資訊系館65405':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data)
        )
    elif event.postback.data == '資訊系館4263':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data)
        )
    elif event.postback.data == '測量系館經緯廳':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data)
        )
    elif event.postback.data == '新增地點':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.postback.data)
        )
    # 修改完成後，回到initial state
    model.update_user_state_by_lineid("initial",event.user_line_id)
    

# decorator 負責判斷 event 為 MessageEvent 實例，event.message 為 TextMessage 實例。所以此為處理 TextMessage 的 handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 決定要回傳什麼 Component 到 Channel
    # ref:https://github.com/line/line-bot-sdk-python#linebotapi
    # print(event.source.user_id)
    user_line_id = event.source.user_id
    profile = line_bot_api.get_profile(user_line_id) # get profile by user's line_id(user_id)
    user_info = model.find_user_by_line_id(user_line_id)
    if user_info == "Not found":
        # 沒有資料的情況，不管輸入甚麼都會出現下列回應
        model.create_user_info(user_line_id)
        model.update_user_state_by_lineid("add student info",user_line_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"嗨，{profile.display_name}！\n你好像是第一次使用我唷><\n為了完整使用子揚小幫手點名功能，\n請輸入你的成功入口 學號/密碼以進行防疫點名登入。\n子揚只會將你的資訊用來點名，請放心:)\n輸入格式範例：\n學號:F74072235\n密碼:password"
            )
        )
    else:
        app.logger.info("Got Follow event from:" + user_info['state'])
        if user_info['state'] == "update student info":
            # 要求使用者輸入帳號密碼的state
            txt = event.message.text
            try:
                txt = txt.split("\n")
                number = txt[0].split(":")[1] # 學號
                psw = txt[1].split(":")[1] # 密碼
                info = dict(zip(['userId','student_number','student_password'],[user_line_id,number,psw]))
                model.update_user_student_by_lineid(info)
                model.update_user_state_by_lineid("initial",user_line_id)
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請按照正確格式輸入~\n輸入格式範例：\n學號:F74072235\n密碼:password")
                )
        elif user_info['state'] == "initial":
            # 登入後的state，可以透過輸入"點名"進入rollcall state
            # 或是輸入"更改資訊"進入add student info
            line_bot_api.push_message(
                event.user_line_id,
                FlexSendMessage(
                    alt_text="Test",
                    contents=messageObeject.actionChoice
                )
            )
            if "點名" in event.message.text:
                # 送出教室選單
                line_bot_api.reply_message(
                    event.user_line_id,
                    FlexSendMessage(
                        alt_text="Test",
                        contents=messageObeject.flex_msg
                    )
                )
            elif "修改" in event.message.text:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{profile.display_name}，聽說你要修改東西嗎？\n請輸入下列格式範例：\n學號:F74072235\n密碼:password"
                    )
                )
                model.update_user_state_by_lineid("initial",user_line_id)
        # elif user_info['state'] == "rollcall":
            # 此處選擇要點名的教室
            # After rollcall go to initial state or go to update student info
            # line_bot_api.push_message(
            #         event.user_line_id,
            #         TextSendMessage(text="請選擇要點名的教室\n目前有:\n資訊系館4263\n資訊系館65304\n資訊系館65405\n測量系館經緯廳")
            #     )
            
            
        
        # profile = line_bot_api.get_profile(user_line_id)

    


if __name__ == "__main__":
    app.run()
    # port = os.environ.get("PORT", 8000)
    # app.run(host="0.0.0.0", port=port, debug=True)