from __future__ import print_function

import base64
import re
from operator import itemgetter
from pprint import pprint

import arrow
import requests
from tabulate import tabulate

TIMESTAMP_FORMAT = 'ddd MMM DD HH:mm:ss Z YYYY'
MESSAGE_PATTERN = re.compile(
    r'(?P<time>\d{1,2}[.:]\d{2}) +'
    r'SERVICE UPDATE: (?P<message>[^\d]*(?P<delay>\d+).*)(?P<url>https?://\S+)')

THAMESLINK_SCREEN_NAME = 'tlrailuk'

CONSUMER_KEY = 'jMR9m3TNpJ96vstvFfH00nfNR'
CONSUMER_SECRET = 'tvsvVsD0fUQacb5lSOzy6xRDAUmsEeD1EjAaXZOtvth1Zwa96d'

# Get bearer token
consumer_credentials = '{key}:{secret}'.format(key=CONSUMER_KEY,
                                               secret=CONSUMER_SECRET)
bearer_token_credentials = base64.urlsafe_b64encode(consumer_credentials)
resp = requests.post(
    'https://api.twitter.com/oauth2/token',
    headers={'Authorization': 'Basic {}'.format(bearer_token_credentials),
             'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'},
    data='grant_type=client_credentials'
).json()
token_type = resp['token_type']
assert token_type == 'bearer', \
    "Expected 'bearer' token type but got '{}'!".format(token_type)
bearer_token = resp['access_token']

# Dummy request
resp = requests.get(
    'https://api.twitter.com/1.1/statuses/user_timeline.json',
    headers={'Authorization': 'Bearer {}'.format(bearer_token)},
    params=dict(screen_name=THAMESLINK_SCREEN_NAME, count=100,
                trim_user='true', exclude_replies='true', include_rts='false')
).json()
results = []
for tweet in resp:
    match = re.search(MESSAGE_PATTERN, tweet['text'])
    if match:
        timestamp = arrow.get(tweet['created_at'], TIMESTAMP_FORMAT).to('local')
        # print('{date} at {time} ({human})'.format(
        #     date=timestamp.format('ddd DD MMM YYYY'),
        #     time=timestamp.format('H:mm'),
        #     human=timestamp.humanize(locale='en_gb')))
        # pprint(match.groupdict())
        results.append((timestamp, match.groupdict()['delay']))
results.sort(key=itemgetter(0))
formatted_results = ((timestamp.format('ddd DD/MM @ HH:mm'), delay)
                     for timestamp, delay in results)
print(tabulate(formatted_results, headers=('timestamp', 'delay'),
               tablefmt='simple'))
