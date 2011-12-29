import logging
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import web

def main():
    logging.getLogger().setLevel(logging.DEBUG)
    application = webapp.WSGIApplication([(r'/$|/map$', web.Map),
                                          (r'/beers$',  web.Beers),
                                          (r'/.+',      web.Main)],
                                         debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

