from flask import Flask, request, abort 
# 代表著從flask這個module中引入Flask, request, abort
# REF:https://github.com/twtrubiks/python-notes/tree/master/configparser_tutorial
import os
import sys
import psycopg2
import model 
import sele
from dotenv import load_dotenv
load_dotenv()
import messageObeject

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

# secret settings
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
DATABASE_URL = os.getenv("DATABASE_URL", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)
@app.route("/", methods=['GET'])
def hello_world():
		# 有人觸發了 / 這個路徑的時候就會呼叫此function並且執行
    return request.url_root
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
    return 'OK'
@handler.add(FollowEvent)
def handle_follow(event):
    app.logger.info("Got Follow event from:" + event.source.user_id)
    # Join's greeting
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"歡迎使用子揚幫你點名小幫手，\n這個機器人可以幫你防疫點名，\n省去掃QRCode的時間！\n\n隨便輸入甚麼來開啟我的功能吧><")
    )

@handler.add(PostbackEvent)
def handle_postback(event):
    # 點名系統
    line_bot_api.push_message(
            event.source.user_id, TextSendMessage(text="進入點名系統")
        )
    app.logger.info("event.postback.data:" +  event.postback.data)
    if event.postback.data == '新增地點':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text="目前沒有這個功能哈哈哈，子揚就爛")
        )
    classrooms = ['資訊系館65304','資訊系館65405','資訊系館4263','測量系館經緯廳']
    classroom = ""
    if event.postback.data in classrooms:
        classroom = event.postback.data
    student = model.find_user_by_line_id(event.source.user_id)
    if sele.login(classroom,student['student_number'],student['student_password']) == False:
        line_bot_api.push_message(
            event.source.user_id,
            TextSendMessage(text="帳號/密碼錯誤囉，請重新設定")
        )
        model.update_user_state_by_lineid("add student info",event.source.user_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="請按照正確格式輸入~\n輸入格式範例(半型冒號)：\n學號:F74072235\n密碼:password")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="點名成功了喇，你這個翹課的小壞蛋。")
        )
    # 修改完成後，回到initial state
        model.update_user_state_by_lineid("initial",event.source.user_id)
    

# decorator 負責判斷 event 為 MessageEvent 實例，event.message 為 TextMessage 實例。所以此為處理 TextMessage 的 handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 決定要回傳什麼 Component 到 Channel
    # ref:https://github.com/line/line-bot-sdk-python#linebotapi
    # print(event.source.user_id)
    user_line_id = event.source.user_id
    # app.logger.info("Got msg event from:" + user_line_id)
    profile = line_bot_api.get_profile(user_line_id) # get profile by user's line_id(user_id)
    # app.logger.info("Profile: ",profile,type(profile))
    user_info = model.find_user_by_line_id(user_line_id)
    if user_info == "Not found":
        # 沒有資料的情況，不管輸入甚麼都會出現下列回應
        app.logger.info("NOT found")
        model.create_user_info(profile)
        model.update_user_state_by_lineid("add student info",user_line_id)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"嗨，{profile.display_name}！\n你好像是第一次使用我唷><\n為了完整使用子揚小幫手點名功能，\n請輸入你的成功入口 學號/密碼以進行防疫點名登入。\n子揚只會將你的資訊用來點名，請放心:)\n輸入格式範例：\n學號:F74072235\n密碼:password"
            )
        )
    else:
        app.logger.info("Found user:" + user_info['state'])
        if user_info['state'] == "add student info":
            # 要求使用者輸入帳號密碼的state
            txt = event.message.text
            try:
                txt = txt.split("\n")
                number = txt[0].split(":")[1] # 學號
                psw = txt[1].split(":")[1] # 密碼
                # app.logger.info(txt,number,psw)
                info = dict(zip(['userId','student_number','student_password'],[user_line_id,number,psw]))
                model.update_user_student_by_lineid(info)
                model.update_user_state_by_lineid("initial",user_line_id)
                # 送出選項
                line_bot_api.push_message(
                    user_line_id,
                    TextSendMessage(text="修改成功")
                )
                line_bot_api.push_message(
                    user_line_id,
                    FlexSendMessage(
                        alt_text="Test",
                        contents=messageObeject.actionChoice
                    )
                )
            except:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請按照正確格式輸入~\n輸入格式範例(半型冒號)：\n學號:F74072235\n密碼:password")
                )
        elif user_info['state'] == "initial":
            # 登入後的state，可以透過輸入"點名"進入rollcall state
            # 或是輸入"更改資訊"進入add student info
            if "點名" in event.message.text:
                # 送出教室選單
                line_bot_api.reply_message(
                    event.reply_token,
                    FlexSendMessage(
                        alt_text="Test",
                        contents=messageObeject.flex_msg
                    )
                )
            elif "修改" in event.message.text:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f"{profile.display_name}，聽說你要修改東西嗎？\n請輸入下列格式範例(半型冒號)：\n學號:F74072235\n密碼:password"
                    )
                )
                model.update_user_state_by_lineid("add student info",user_line_id)
            else:
                # 一勞永逸後的狀況
                line_bot_api.push_message(
                        user_line_id,
                        TextSendMessage(text="Hi~又是我子揚喇哈哈哈，\n是不是又想翹課了，\n哎，真拿你沒辦法\n我就順手幫你點名吧")
                    )
                url = request.url_root + '/static/mohado.jpg'
                line_bot_api.reply_message(
                    event.reply_token,
                    {
                        "type": "image",
                        "originalContentUrl": url,
                        "previewImageUrl": url
                    }
                )
                line_bot_api.push_message(
                        user_line_id,
                        FlexSendMessage(
                            alt_text="Test",
                            contents=messageObeject.actionChoice
                        )
                    )
            
            
        
        # profile = line_bot_api.get_profile(user_line_id)

    


if __name__ == "__main__":
    # app.run()
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)