from flask import Flask, request, Response
from feedgen.feed import FeedGenerator
import requests
import json
import re

app = Flask(__name__)



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
                        }
                    }]
                }
            },
            "from": 0,
            "size": 50,
            "sort": {
                "date_updated": "desc"
            }
        })
    )

    for entry in response.json()['hits']['hits']:
        fe = fg.add_entry()
        fe.title(entry['_source']['title'])
        fe.description(entry['_source']['description'])
        urls = entry['_source']['identifiers']
        link_url = osf_url(urls, service)
        fe.link(href=link_url)
        fe.id(link_url)

    return fg


@app.route("/")
def index():
    return "Feeds"


@app.route("/<service>.rss")
def socarxiv_rss(service=None):
    if service=='socarxiv':
        service = 'SocArXiv'
    fg = build_feed(request.url, service)
    response = Response(fg.rss_str(pretty=True))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response

if __name__ == "__main__":
    app.run()