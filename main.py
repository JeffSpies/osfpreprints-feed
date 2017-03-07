from flask import Flask, request, Response
from feedgen.feed import FeedGenerator
import requests
import json

app = Flask(__name__)


def osf_url(urls):
    for url in urls:
        if 'osf' in url:
            return url.replace('preprints/socarxiv/', '')
    return ''


def build_feed(url, service="SocArXiV"):
    fg = FeedGenerator()
    fg.id('http://osf.io/preprints/' + service)
    fg.title(service + ' Preprints')
    fg.author({'name': service})
    fg.link(href=url, rel='self')
    fg.link(href='https://osf.io/preprints/' + service, rel='alternate')
    fg.subtitle('Preprints submitted to ' + service + ' at https://osf.io/preprints/' + service)

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
        link_url = osf_url(urls)
        fe.link(href=link_url)
        fe.id(link_url)

    return fg


@app.route("/")
def index():
    return "Feeds"


@app.route("/socarxiv.rss")
def socarxiv_rss():
    fg = build_feed(request.url)
    response = Response(fg.rss_str(pretty=True))
    response.headers['Content-Type'] = 'application/rss+xml'
    return response


# @app.route("/socarxiv.atom")
# def socarxiv_atom():
#     fg = build_feed(request.url)
#     response = Response(fg.atom_str(pretty=True))
#     response.headers['Content-Type'] = 'application/atom+xml'
#     return response

if __name__ == "__main__":
    app.run()