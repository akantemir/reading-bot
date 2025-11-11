import requests
import logging
import uuid
from config import GIGACHAT_AUTH_URL, GIGACHAT_API_URL, GIGACHAT_AUTH_KEY, GIGACHAT_SCOPE

logger = logging.getLogger(__name__)

def get_access_token():
    """
    Получить Access Token для GigaChat API через OAuth2
    """
    try:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {GIGACHAT_AUTH_KEY}",
            "RqUID": str(uuid.uuid4())
        }
        data = {"scope": GIGACHAT_SCOPE}

        response = requests.post(GIGACHAT_AUTH_URL, headers=headers, data=data, verify=False)
        response.raise_for_status()

        token = response.json().get("access_token")
        logger.info("✓ Access token получен успешно")
        return token
    except Exception as e:
        logger.error(f"✗ Ошибка при получении токена: {e}")
        return None

def generate_motivation(prompt):
    """
    Генерировать мотивирующее сообщение через GigaChat API
    """
    try:
        token = get_access_token()
        if not token:
            logger.warning("Не удалось получить токен GigaChat")
            return None
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "model": "GigaChat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты - мотивационный тренер. Твоя задача давать короткие, мотивирующие сообщения (1-2 предложения) на русском языке. Не используй смайлики."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        response = requests.post(GIGACHAT_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        
        result = response.json()
        message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if message:
            logger.info(f"✓ Получено сообщение от GigaChat: {message[:50]}...")
            return message
        else:
            logger.warning("Пустой ответ от GigaChat")
            return None
            
    except Exception as e:
        logger.error(f"✗ Ошибка при запросе к GigaChat: {e}")
        return None
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
