import logging
from webapp2 import WSGIApplication
import web

logging.getLogger().setLevel(logging.DEBUG)

routes = [(r'/$|/map$',           web.getMap),
          (r'/beers$',            web.getBeers),
          (r'/preview$',          web.postImagePreview),
          (r'/preview/[\da-f]+$', web.getImagePreview),
          (r'/.+',                web.MainHandler),]
application = WSGIApplication(routes, debug=True)

