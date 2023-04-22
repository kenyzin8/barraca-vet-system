import requests
import urllib.parse
import time
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta

api_key = os.getenv("SEMAPHORE_API_KEY")
sendername = 'SEMAPHORE'

def fetch_sms_data():
    current_time = int(time.time())
    last_request_time = cache.get('last_request_time', current_time)
    request_count = cache.get('request_count', 0)

    if current_time - last_request_time < 60 and request_count >= 30:
        return "You're on cooldown, please wait for 1 minute to request again. (API Cooldown)"

    current_date = datetime.now().date()
    start_date = current_date - timedelta(days=5)

    params = (
        ('apikey', api_key),
        ('limit', 100),
        ('startDate', start_date.strftime("%Y-%m-%d")),
        ('endDate', current_date.strftime("%Y-%m-%d")),
    )

    url = f"https://api.semaphore.co/api/v4/messages?" + urllib.parse.urlencode(params)
 
    response = requests.get(url)

    if response.status_code == 200:
        sms_data = response.json()

        if current_time - last_request_time < 60:
            cache.set('request_count', request_count + 1, 60)
        else:
            cache.set('request_count', 1, 60)
            cache.set('last_request_time', current_time, 60)

    else:
        sms_data = None

    return sms_data

def send_otp_sms(to_phone_number):
    message = "Your One Time Password is: {otp}. Please use it within 5 minutes."
    
    params = (
        ('apikey', api_key),
        ('sendername', sendername),
        ('message', message),
        ('number', to_phone_number)
    )

    url = 'https://semaphore.co/api/v4/otp?' + urllib.parse.urlencode(params)
    response = requests.post(url)

    if response.status_code == 200:
        otp_code = response.json()[0]["code"]
        print(f'OTP sent to {to_phone_number}')
        return otp_code
    else:
        print("Error sending OTP:", response.status_code, response.text)
        return None

def send_sms(to_phone_number, message):
    params = (
        ('apikey', api_key),
        ('sendername', sendername),
        ('message', message),
        ('number', to_phone_number)
    )

    url = 'https://semaphore.co/api/v4/messages?' + urllib.parse.urlencode(params)

    response = requests.post(url)

    if response.status_code == 200:
        print(f'Message sent to {to_phone_number}')
    else:
        print("Error sending message:", response.status_code, response.text)
