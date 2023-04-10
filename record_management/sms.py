import requests
import urllib.parse
from django.conf import settings

apikey = settings.SEMAPHORE_API_KEY
sendername = 'SEMAPHORE'

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
