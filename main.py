from flask import Flask, request
from feedgen.feed import FeedGenerator
import requests
import json

app = Flask(__name__)


def osf_url(urls):
    for url in urls:
        if 'osf' in url:
            return url.replace('preprints/socarxiv/', '')
    return ''


def build_feed(url):
    fg = FeedGenerator()
    fg.id('http://osf.io/preprints/socarxiv')
    fg.title('SocArXiV')
    fg.author({'name': 'SocArXiv'})
    fg.link(href=url, rel='self')
    fg.link(href='http://osf.io/preprints/socarxiv', rel='alternate')
    fg.subtitle('Updates to SocArXiv')

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
                            "sources": "SocArXiv"
                        }
                    }]
                }
            },
            "from": 0,
            "aggregations": {
                "sources": {
                    "terms": {
                        "field": "sources",
                        "size": 500
                    }
                }
            }
        })
    )

    for entry in response.json()['hits']['hits']:
        fe = fg.add_entry()
        fe.title(entry['_source']['title'])
        fe.description(entry['_source']['description'])
        urls = entry['_source']['identifiers']
        url = osf_url(urls)
        fe.link(href=url, rel='self')
        fe.id(url)

    return fg


@app.route("/")
def index():
    return "Feeds"


@app.route("/socarxiv.rss")
def socarxiv_rss():
    fg = build_feed(request.url)
    return fg.rss_str(pretty=True)


@app.route("/socarxiv.atom")
def socarxiv_atom():
    fg = build_feed(request.url)
    return fg.atom_str(pretty=True)

if __name__ == "__main__":
    app.run()