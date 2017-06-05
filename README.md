# osfpreprints-feed

Code to create an RSS feed server for an OSF Preprint partner server (e.g., SocArXiv, engrXiv). Also included are files necessary to run this on Heroku. The original intent was to create a server for only a few http clients in order to power partner Twitter feeds with IFTTT, e.g.,

https://twitter.com/socarxivpapers

If you'd like to see a single instance support more users, please submit a PR that adds caching. COS does run an instance on Heroku by request only. If you'd like access, shoot me an email.

Note: in the URL, e.g.,

http://localhost:5000/SocArXiv.rss

SocArXiv can be replaced by the canonical names/spellings of any of the OSF Preprint servers. It is case-sensitive unless the correct spelling has been hard-coded in main.py.
