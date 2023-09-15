import os

from flask import Flask, request, abort
from dotenv import load_dotenv
from weather import nearest_weather, forecast
from weather.daily import daily_weather
from washing import check_washing


from apscheduler.schedulers.background import BackgroundScheduler

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LocationMessageContent
)

from linebot.v3.messaging.models.push_message_request import PushMessageRequest
from linebot.v3.messaging.models.push_message_response import PushMessageResponse

load_dotenv()
app = Flask(__name__)
scheduler = BackgroundScheduler()

# scheduler.add_job(send_message,  '{time}', {time_arg}, args=[chat_id, text], id=)

LINE_CHANNEL = os.getenv('LINE_CHANNEL')
LINE_SCRECT = os.getenv('LINE_SECRET')

handler = WebhookHandler(LINE_SCRECT)
configuration = Configuration(access_token=LINE_CHANNEL)
with ApiClient(configuration) as api_client:
    line_bot_api = MessagingApi(api_client)

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event.message.text.startswith("洗衣服"):
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=check_washing())]
            )
        )

@handler.add(MessageEvent, message=LocationMessageContent)
def handle_message(event):
    line_bot_api.reply_message_with_http_info(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=nearest_weather(event.message.longitude, event.message.latitude) + "\n\n" + forecast(event.message.address.replace('台','臺')))]
        )
    )

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=4000)