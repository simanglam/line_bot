import json
import requests

from weather import forecast, nearest_weather

def daily_weather(token, ):

    headers = {'Authorization':f'Bearer {token}','Content-Type':'application/json'}    
    body = {
        "to": "Ue81ff6c316b6ebe482264e577453b1da",
        'messages':[
            {
                'type': 'text',
                "text": "HI"
            }
        ]
    }

    req = requests.request('POST', 'https://api.line.me/v2/bot/message/push', headers=headers, data=json.dumps(body).encode('utf-8'))
    print(req.status_code)

