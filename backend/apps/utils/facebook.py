import requests



class Proxy:
    def __init__(self, protocol, host, port, username=None, password=None, user_agent=None):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.user_agent = user_agent

    def get_proxy(self):
        return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"

    def __str__(self):
        return self.get_proxy()

        

class FacebookConversionAPI():
    def __init__(self, access_token, pixel_id, proxy: Proxy =None, api_version='v17.0'):
        self.access_token = access_token
        self.pixel_id = pixel_id
        self.proxy = proxy
        self.api_version = api_version

    def sendEvent(self, event_name, user_data=None, event_time=None)->dict:
        url = f"https://graph.facebook.com/{self.api_version}/{self.pixel_id}/events"
        payload = {
            'access_token': self.access_token,
            'data': [{'event_name': event_name}]
        }
        if user_data:
            payload['data'][0]['user_data'] = user_data

        if event_time:
            payload['data'][0]['event_time'] = event_time

        # if proxy send request with proxy 
        if self.proxy:
            proxies = {
                "http": self.proxy.get_proxy(),
                "https": self.proxy.get_proxy()
            }
            r = requests.post(url, json=payload, proxies=proxies, headers={'User-Agent': self.proxy.user_agent}, timeout=10)

        else:
            r = requests.post(url, json=payload)

        try:
            return r.json()
        except:
            return r.text
    

    


