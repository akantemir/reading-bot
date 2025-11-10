import requests
import json

async def generate_motivation(text):
    try:
        url = 'https://api.gigachat.ru/api/v1/chat/completions'
        headers = {'Authorization': 'Bearer YOUR_AUTH_KEY'}
        payload = {'model': 'GigaChat', 'messages': [{'role': 'user', 'content': text}]}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return 'Keep going!'
    except:
        return 'Keep going!'
