import requests
import urllib.parse
from django.conf import settings

apikey = settings.SEMAPHORE_API_KEY
sendername = 'SEMAPHORE'

def send_otp_sms(to_phone_number):
    message = "Your One Time Password is: {otp}. Please use it within 5 minutes."
    
    params = (
        ('apikey', apikey),
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
        ('apikey', apikey),
        ('sendername', sendername),
        ('message', message),
        ('number', to_phone_number)
    )

    url = 'https://semaphore.co/api/v4/messages?' + urllib.parse.urlencode(params)
    print(url)
    response = requests.post(url)

    if response.status_code == 200:
        print(f'Message sent to {to_phone_number}')
    else:
        print("Error sending message:", response.status_code, response.text)
