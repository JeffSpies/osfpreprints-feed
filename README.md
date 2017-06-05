# osfpreprints-feed

Code to create an RSS feed for an OSF Preprint Partner server (e.g., SocArXiv). The original intent of this was to be used by only a few clients in order to power partner Twitter feeds using this and IFTTT. If you'd like to see this support more users, please submit a PR that adds caching.

This repo includes the files necessary to run this on Heroku.

Note: in the URL, e.g.,

http://localhost:5000/SocArXiv.rss

SocArXiv can be replaced by the canonical names/spellings of any of the OSF Preprint servers--it is case-sensitive unless the correct spelling has been hard-coded in main.py.
