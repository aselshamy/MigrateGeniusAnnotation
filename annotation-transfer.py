import geniusconfig as config
import requests
import json
import urllib
from IPython import embed

#This needs to be reobtained everytime we want to run the whole flow
manually_obtained_code = config.manually_obtained_code

access_token_from_redirect = config.access_token_from_redirect

genius_url = 'https://api.genius.com'
access_token = config.access_token

client_id = config.client_id
client_secret = config.client_secret

from_url = 'http://ec2-34-226-4-23.compute-1.amazonaws.com/draft/en.wikipedia.org/wiki/Martin_Luther_King_Jr.'
from_canonical_url = 'Martin_Luther_King_Jr.'

to_url = 'http://ec2-34-226-4-23.compute-1.amazonaws.com/preview/en.wikipedia.org/wiki/Martin_Luther_King_Jr.'
to_canonical_url = 'Martin_Luther_King_Jr.'

def get_request(url):
    response = requests.get(url)
    return json.loads(response.text)

def post_request(url, data):
    response = requests.post(url, json=data)
    return response

def oauth_string(string):
    return urllib.quote(string, safe='')

def get_webpage_lookup(url, canonical_url):
    endpoint = '/web_pages/lookup'
    response = get_request('{api_url}{endpoint}?access_token={access_token}&canoncial_url={canonical_url}&raw_annotatable_url={raw_annotatable_url}'.format(
            api_url = genius_url,
            endpoint = endpoint,
            access_token = access_token,
            canonical_url = canonical_url,
            raw_annotatable_url = oauth_string(url)))
    # print 'Page lookup response:'
    # print response
    return response

def get_referents(website_id):
    endpoint = '/referents'
    response = get_request('{api_url}{endpoint}?access_token={access_token}&web_page_id={web_page_id}'.format(
            api_url = genius_url,
            endpoint = endpoint,
            access_token = access_token,
            web_page_id = website_id))
    # print 'Referents response:'
    # print response
    return response

def post_get_authentication():
    data = {"client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": "http://ec2-34-226-4-23.compute-1.amazonaws.com/",
            "response_type": "token",
            "scope": "create_annotation",
            "state": "good"
            }
    response = requests.get('{api_url}/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=create_annotation&state=good&response_type=token'.format(
            api_url = genius_url,
            client_id = client_id,
            redirect_uri = 'http://ec2-34-226-4-23.compute-1.amazonaws.com/'))

    response = requests.post('https://api.genius.com/authorizations', json=data)
    print "Authentication:"
    print response
    return response

def post_annotation(referent, access_code):
    endpoint = '/annotations'
    url = '{api_url}{endpoint}?access_token={access_token}'.format(
            api_url = genius_url,
            endpoint = endpoint,
            access_token = access_token_from_redirect)
    payload = referent.to_payload()
    response = post_request(url, payload)
    print 'Post Annotation:'
    print response
    return response

class Referent:
    def __init__(self, json):
        self.fragment = json['fragment']
        self.before_html = json['range']['before']
        self.after_html = json['range']['after']
        self.annotation_path = json['annotations'][0]['api_path']
        self.body = self.get_annotation_body()['response']['annotation']['body']['dom']['children'][0]['children'][0]

    def get_annotation_body(self):
        return get_request('{api_url}{annotation_path}?access_token={access_token}'.format(
            api_url = genius_url,
            annotation_path = self.annotation_path,
            access_token = access_token))

    def to_payload(self):
        return {
            "annotation": {
                "body": {
                    "markdown": self.body
                }
            },
            "referent": {
                "raw_annotatable_url": to_url,
                "fragment": self.fragment,
                "context_for_display": {
                    "before_html": self.before_html,
                    "after_html": self.after_html
                }
            },
            "web_page": {
                "canonical_url" : to_canonical_url
            }
        }

# if you need access code, uncomment the following line but also manually get another code for "manually_obtained_code"
# access_token_from_redirect = post_get_authentication()
#access_code = 'GdkVxUT8BoyqYL7NIZ2BvbCbOOEkTZVWAfLpOUDDadUFPoNx5cizrY157OZmhudj'
#access_code = ''

website_id = get_webpage_lookup(from_url, from_canonical_url)['response']['web_page']['id']

referents_json = get_referents(website_id)

referents = []

for referent in referents_json['response']['referents']:
    referents.append(Referent(referent))

response = post_annotation(referents[0], access_token_from_redirect)
