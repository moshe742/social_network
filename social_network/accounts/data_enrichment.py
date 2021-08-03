from datetime import datetime as dt
from datetime import timedelta
import logging
import os
from time import sleep

import requests


logger = logging.getLogger(__name__)

EMAIL_API_KEY = os.environ.get('EMAIL_API_KEY')
GEO_API_KEY = os.environ.get('GEO_API_KEY')
HOLIDAY_API_KEY = os.environ.get('HOLIDAY_API_KEY')

RETRIES = 5


def is_valid_email(email):
    url = 'https://emailvalidation.abstractapi.com/v1/'
    params = {'api_key': EMAIL_API_KEY, 'email': email}
    response = requests.get(url, params=params)

    for _ in range(RETRIES):
        if response.status_code >= 500:
            sleep(1)
            response = requests.get(url, params=params)
        else:
            break
    else:
        # assuming the "safe" option
        return False

    if response.status_code >= 400:
        logger.exception(f'There is a problem with the request on our side- '
                         f'status code: {response.status_code}'
                         f'response json: {response.json()}')
        return False

    response_dict = response.json()
    return response_dict['is_valid_format']['value']


def enrich_geo(user):
    print('hello')
    url = 'https://ipgeolocation.abstractapi.com/v1/'
    params = {'api_key': GEO_API_KEY, 'ip_address': user.ip}
    res = requests.get(url, params=params)

    for _ in range(5):
        if res.status_code >= 500:
            sleep(1)
            continue
        geo_data = res.json()
        user.city = geo_data['city']
        user.region = geo_data['region']
        user.country = geo_data['country_code']
        # if we on localhost it doesn't really matter
        if user.ip == '127.0.0.1':
            geo_data['timezone'] = {'gmt_offset': 0}
        user.signup_at_holiday = is_holiday(user, geo_data['timezone']['gmt_offset'])
        user.save()


def is_holiday(user, gmt_offset):
    url = 'https://holidays.abstractapi.com/v1/'
    now = dt.now()
    user_date = now + timedelta(hours=gmt_offset)
    params = {'country': user.country, 'year': user_date.year, 'month': user_date.month,
              'day': user_date.day, 'api_key': HOLIDAY_API_KEY}
    res = requests.get(url, params=params)
    return bool(res.json())
