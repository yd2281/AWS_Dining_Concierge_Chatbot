from requests_aws4auth import AWS4Auth
import boto3
import requests
from datetime import datetime
import json
from decimal import *
from urllib.parse import quote
import socket
from requests_aws4auth import AWS4Auth

# yelp api details
API_KEY = "<API_KEY>"
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

# Defaults for our simple example.
DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'manhattan'
SEARCH_LIMIT = 50

#host = 'https://search-yelp-restaurants-domain-fisoghxvlz63b5skhjjsiixg4m.us-east-1.es.amazonaws.com'
host = 'https://search-restaurant-gkgknrtvkb4drescojoawsqwnm.us-east-1.es.amazonaws.com'
index = 'restaurants'
type = 'Restaurant'

url = host + '/' + index + '/' + type + '/'
print(url)
headers = { "Content-Type": "application/json" }

# function to make an api request
def request(host, path, api_key, url_params=None):
    hostname = socket.gethostname()    
    IPAddr = socket.gethostbyname(hostname)    
    print("Your Computer Name is:" + hostname)    
    print("Your Computer IP Address is:" + IPAddr) 
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    print(u'Querying {0} ...'.format(url), url_params)

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

# function to use the search API
def search(api_key, term, location, offset):
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'offset': offset,
        'radius':40000
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)

# function to get required fields
def handle_response(businesses, cuisine):
    documents = []
    for item in businesses:
        restaurant = {
            "Business ID": item["id"],
            "cuisine": cuisine
        }
        documents.append(restaurant)
    return json.loads(json.dumps(documents), parse_float=Decimal)

# function to push data into dynamoDB
def push_data(businesses):
    access_key='<ACCESS_KEY>'
    secret_key='<SECRET_KEY>'
    token='<TOKEN>'
    awsauth = AWS4Auth(access_key, secret_key, 'us-east-1', 'es', session_token=token)
    for business in businesses:
        payload = business
        my_es_id = payload["Business ID"]
        print("try")
        r = requests.post(url+str(my_es_id), auth = awsauth, json=payload, headers=headers)
        print(r.text)

cuisines =     cuisines = ['Turkish']

manhattan_neighbourhoods = ['Lower East Side, Manhattan',
                   'Upper East Side, Manhattan',
                   'Upper West Side, Manhattan',
                   'Washington Heights, Manhattan',
                   'Central Harlem, Manhattan',
                   'Chelsea, Manhattan',
                   'Manhattan',
                   'East Harlem, Manhattan',
                   'Gramercy Park, Manhattan',
                   'Greenwich, Manhattan',
                   'Lower Manhattan, Manhattan',
                   'Columbus Circle, Manhattan'
                   'Times Square, Manhattan',
                   'Hells Kitchen, Manhattan',
                   'Midtown, Manhattan',
                   'Union Square, Manhattan']


cusine_counters = []

# for each cuisine
for cuisine in cuisines:
    cuisine_counter = 0
    # do two passes for each neighbourhood with offset 
    for i in range(0, 4):
        for neighbourhood in manhattan_neighbourhoods:
            try:
                response = search(API_KEY, cuisine, neighbourhood, i * 50)
                business_data = response['businesses']
                businesses = handle_response(business_data, cuisine)
                push_data(businesses)  
                cuisine_counter += len(businesses)
            except:
                print('Fail')
    # print(cuisine, cuisine_counter)
    cusine_counters.append({'cuisine':cuisine, 'count':cuisine_counter})

print(cusine_counters)
