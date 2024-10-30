import requests


class TikTokConversionAPI():
    def __init__(self, access_token, pixel_id):
        self.access_token = access_token
        self.pixel_id = pixel_id

    def sendEvent(self, event_name, user_data=None, event_time=None):
        url = "https://api.tiktok.com/marketing_api/events/pixel/"
        payload = {
            'access_token': self.access_token,
            'data': [{'event_name': event_name}]
        }
        if user_data:
            payload['data'][0]['user_data'] = user_data

        if event_time:
            payload['data'][0]['event_time'] = event_time

        r = requests.post(url, json=payload)
        return r