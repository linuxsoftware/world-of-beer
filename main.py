import logging
import os
import webapp2
import web

logging.getLogger().setLevel(logging.DEBUG)
application = webapp2.WSGIApplication([(r'/$|/map$', web.Map),
                                       (r'/beers$',  web.Beers),
                                       (r'/.+',      web.Main)],
                                       debug=True)
