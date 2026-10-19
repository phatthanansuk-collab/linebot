import os
import logging
from flask import Flask, request, abort

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

handler = WebhookHandler(os.environ["LINE_CHANNEL_SECRET"])
config = Configuration(access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

@app.route("/")
def home():
    return "LINE Webhook is running"

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.warning("Invalid signature")
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text
    app.logger.info(f"Received message: {user_text}")

    reply_text = f"คุณพิมพ์ว่า: {user_text}\n\nสวัสดีครับ LINE Bot ทำงานแล้ว"

    with ApiClient(config) as api_client:
        api = MessagingApi(api_client)
        api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )

if __name__ == "__main__":
    app.run(port=5000, debug=True)
