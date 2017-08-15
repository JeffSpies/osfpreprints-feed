from flask import Flask, request, Response
from feedgen.feed import FeedGenerator
from unidecode import unidecode
import requests
import json
import re

app = Flask(__name__)

# This mapping doesn't need to exist, but it does make the app more robust, i.e., url.com/feed/EngrXiv would work
# even though the actual term is engriXiv.
# TODO: SHARE reallly just needs to make these terms case-insensitive.
services_list = [
    'engrXiv',
    'PsyArXiv',
    'SocArXiv',
    'BITSS',
    'AgriXiv',
    'LawArXiv'
]

services = { service.lower():service for service in services_list }

def valid_xml(text):
    # I added unidecode to the following
    #   https://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
    return re.sub(u'[^\u0020-\uD7FF\u0009\u000A\u000D\uE000-\uFFFD\u10000-\u10FFFF]+', '', unidecode(text))

def osf_url(urls, service):
    r = re.compile('preprints/{0}/'.format(service.lower()), re.IGNORECASE)
    for url in urls:
        if 'osf' in url:
            return r.sub('', url)
    return ''


def build_feed(url, service):
    fg = FeedGenerator()
    fg.id('http://osf.io/preprints/{0}'.format(service.lower()))
    fg.title('{0} Preprints'.format(service))
    fg.author({'name': service})
    fg.link(href=url, rel='self')
    fg.link(href='https://osf.io/preprints/{0}'.format(service.lower()), rel='alternate')
    fg.subtitle('Preprints submitted to {0} at https://osf.io/preprints/{1}'.format(service, service.lower()))

    headers = {'Content-Type': 'application/json'}

    response = requests.post(
        'https://share.osf.io/api/v2/search/creativeworks/_search',
        headers=headers,

        data=json.dumps({
            "query": {
                "bool": {
                    "must": {
                        "query_string": {
                            "query": "*"
                        }
                    },
                    "filter": [{
                        "term": {
                            "sources": service
                        },
                        "term": {
                            "types": "preprint",
                        }
                    }]
                }
            },
            "from": 0,
            "size": 50,
            "sort": {
                "date_created": "desc"
            }
        })
    )

    for entry in response.json()['hits']['hits']:
        fe = fg.add_entry()
        fe.title(valid_xml(entry['_source']['title']))
        fe.description(valid_xml(entry['_source']['description']))
        urls = entry['_source']['identifiers']
        link_url = osf_url(urls, service)
        fe.link(href=link_url)
        fe.id(link_url)

    return fg


@app.route("/")
def index():
    return "Feeds"


@app.route("/<service>.rss")
def rss(service=None):
    lowercase_service = service.lower()
    if lowercase_service in services:
        service = services[lowercase_service]
    fg = build_feed(request.url, service)
    print(fg.rss_str(pretty=True))
    response = Response(fg.rss_str(pretty=True))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response

if __name__ == "__main__":
    app.run()
