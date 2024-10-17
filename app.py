from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json
import requests
import os

app = Flask(__name__)

# Line Messaging API 配置
line_bot_api = LineBotApi('KPmIJHzvRdy4zg8SwwYmLPoMmD+t47r25eXLoxQcuVsrYadFmFAhd/+5Nthn7EJOMPHaR81G7I8I51hhGKdq8tu3KNDC/GG2tWWf1GVY8P+R3AuGrOu/Jlx53df1JbbviMwV9CxaN6ehsMhVGzef2wdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d2cafc2d4e340f2928f994e2fcfc315a')

# Google Drive API 配置
credentials_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS']
credentials_info = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(credentials_info)
drive_service = build('drive', 'v3', credentials=credentials)

# 上传文件到 Google Drive
def upload_to_drive(file_path, file_name):
    file_metadata = {'name': file_name, 'parents': ['1Cxe6g70FqTPolyLHFVVWiu6k0Mqippc8']}
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

# Line Webhook 路由
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

# 处理接收到的图片消息
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    message_content = line_bot_api.get_message_content(event.message.id)
    file_path = f"./{event.message.id}.jpg"
    
    with open(file_path, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)
    
    # 上传图片到 Google Drive
    file_id = upload_to_drive(file_path, f"{event.message.id}.jpg")
    os.remove(file_path)

    # 回复用户
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"图片已上传到 Google Drive: {file_id}"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
