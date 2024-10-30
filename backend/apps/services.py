import requests
from .maps import *
import json
import base64

trafficarmor_base_url = 'https://api.trafficarmor.com'


def image_bb_uploader(image):
    image_api_key = '28461bba74926f309479379d9cf2baad'
    api_image_url = 'https://api.imgbb.com/1/upload?expiration=60&key={}'.format(
        image_api_key)
    payload = {
        'image': base64.b64encode(image.read())
    }

    res = requests.post(
        api_image_url, payload)

    return res.json()['data']['url']  # return image url


def get_trafficarmor_campaigns(api_key):
    url = '{}/campaigns?api_key={}'.format(trafficarmor_base_url, api_key)
    trafficarmor_res = requests.get(url)
    campaigns_list = trafficarmor_res.json()['data']

    campaign_dict = {}
    for camp in campaigns_list:
        campaign_dict[camp['cloak_link_id']] = camp

    return campaign_dict
