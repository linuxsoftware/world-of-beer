# -*- coding: utf-8 -*-
import sys
import os
from os.path import join, dirname
import time
import uuid

from google.appengine.api import memcache
from webapp2 import RequestHandler
from mako.lookup import Template, TemplateLookup
from mako import exceptions
from webob import exc

from data import world, Country, Brewery, Beer
from form import CountryForm, BreweryForm, BeerForm

lookup = TemplateLookup(directories = [join(dirname(__file__), "templates")],
                        input_encoding = "utf-8",
                        output_encoding = "utf-8",
                        filesystem_checks = True)

def renderTemplate(request, templateName, **data):
    write = request.response.out.write
    try:
        template = lookup.get_template(templateName)
        write(template.render(request=request, **data))
    except exceptions.TopLevelLookupException:
        request.response.status = 404
        write("Cant find template '%s'" % templateName)
    except:
        request.response.status = 500
        write(exceptions.html_error_template().render())

def getMap(request):
    renderTemplate(request, "map.html")

def getBeers(request):
    renderTemplate(request, "beers.html")

def postImagePreview(request):
    if request.method != "POST":
        raise exc.HTTPMethodNotAllowed()
    #TODO validation use ImageField?
    if request.get("qqfile"):
        image = request.body
        previewId = request.get('previewId')
    elif request.POST.get('qqfile'):
        image = request.POST.get("qqfile").value
        previewId = request.POST.get('previewId')
    else:
        image = ""
        raise RuntimeError("TODO")

    if not previewId:
        previewId = "/%s.png" % uuid.uuid4().hex
    timeout = 3600 # 1 hour
    if len(image) < memcache.MAX_VALUE_SIZE:
        # TODO check size in validation
        memcache.set(previewId, image, timeout, namespace="ImagePreview")
    request.response.headers['Content-Type'] = "text/plain"
    request.response.out.write("{previewId: '%s'}" % previewId)

def getImagePreview(request):
    if request.method != "GET":
        raise exc.HTTPMethodNotAllowed()
    request.path_info_pop() #/preview/
    previewId = request.path_info
    image = memcache.get(previewId, namespace="ImagePreview")
    if image:
        #TODO validation use ImageField?
        request.response.headers['Content-Type'] = "image/png"
        request.response.out.write(image)

class BaseHandler(RequestHandler):
    # TODO refactor getImage and err404 to funcs?

    def err404(self, msg):
        self.error(404)
        self.response.out.write(msg)

    def _findBrewery(self, name):
        # TODO
        #brewery = world.getBrewery(name)
        return None

    def _findBeer(self, name):
        # TODO
        return None

    def getImage(self, wobObj, field):
        if self.request.method != "GET":
            raise exc.HTTPMethodNotAllowed()
        image = getattr(wobObj, field, "")
        self.response.headers['Content-Type'] = "image/png"
        self.response.out.write(image)
        return None


class MainHandler(BaseHandler):
    """This is the main request handler for WoB"""

    def __init__(self, request, response):
        BaseHandler.__init__(self, request, response)

    def dispatch(self):
        name = self.request.path_info_pop()

        country = world.getCountry(name)
        if country:
            handler = CountryHandler(self.request, self.response, country)
            return handler.dispatch()
        
        brewery = self._findBrewery(name)
        if brewery:
            handler = BreweryHandler(self.request, self.response, brewery)
            return handler.dispatch()

        if not self.request.path_info_peek():
            # auto-create country if that is all that is on the path
            country = world.createCountry(name)
            handler = CountryHandler(self.request, self.response, country)
            return handler.dispatch()

        self.err404("Cannot find country or brewery '%s'" % name)
        return None


class CountryHandler(BaseHandler):
    """This is the request handler for a Country"""
    
    def __init__(self, request, response, country):
        BaseHandler.__init__(self, request, response)
        self.country = country

    def dispatch(self):
        # memories of bobo traverse
        # TODO ideally I'd like to refactor out all this common code
        name = self.request.path_info_pop()
        if name:
            if name.endswith('.png') and CountryForm.hasImageField(name[:-4]):
                return self.getImage(self.country, name[:-4])
            else:
                brewery = self._findBrewery(name)
                if brewery:
                    handler = BreweryHandler(self.request, self.response, brewery)
                    return handler.dispatch()
                self.err404("Cannot find brewery '%s'" % name)
                return None

        return BaseHandler.dispatch(self)

    def get(self):
        form = CountryForm(obj=self.country)
        if self.request.query_string == "edit":
            template = "edit_country.html"
        else:
            template = "country.html"
        renderTemplate(self.request, template,
                       form    = form,
                       country = self.country)

    def post(self):
        form = CountryForm(self.request.POST, self.country)
        if form.validate():
            self.error = "something"
            return self.get()

        form.populate_obj(self.country)
        self.country.put()
        return self.redirect(self.request.path)


class BreweryHandler(BaseHandler):
    """This is the request handler for a Brewery"""

    def __init__(self, request, response, brewery):
        BaseHandler.__init__(self, request, response)
        self.brewery = brewery

    def dispatch(self):
        # chaining my request handlers together to make them more zopeish
        name = self.request.path_info_pop()
        if name:
            if name.endswith('.png') and BreweryForm.hasImageField(name[:-4]):
                return self.getImage(self.brewery, name[:-4])
            else:
                beer = self._findBeer(name)
                if beer:
                    handler = BeerHandler(self.request, self.response, beer)
                    return handler.dispatch()
                self.err404("Cannot find beer '%s'" % name)
                return None

        return BaseHandler.dispatch(self)

    def get(self):
        form = None
        if self.request.query_string == "edit":
            template = "edit_brewery.html"
            form = BreweryForm(obj=self.brewery)
        else:
            template = "brewery.html"

        renderTemplate(self.request, template,
                       form    = form,
                       brewery = self.brewery)

    def post(self):
        form = BreweryForm(self.request.POST, self.brewery)
        if form.validate():
            self.error = "something"
            self.get()

        form.populate_obj(self.brewery)
        self.brewery.put()
        return self.redirect(self.request.path)


class BeerHandler(BaseHandler):
    """This is the request handler for a Beer"""

    def __init__(self, request, response, beer):
        BaseHandler.__init__(self, request, response)
        self.beer = beer

    def dispatch(self):
        # chaining my request handlers together to make them more zopeish
        name = self.request.path_info_pop()
        if name:
            if name.endswith('.png') and BeerForm.hasImageField(name[:-4]):
                return self.getImage(self.beer, name[:-4])
            else:
                self.err404("'%s' unknown" % name)
                return None

        return BaseHandler.dispatch(self)

    def get(self):
        form = None
        if self.request.query_string == "edit":
            template = "edit_beer.html"
            form = BeerForm(obj=self.beer)
        else:
            template = "beer.html"

        renderTemplate(self.request, template,
                       form = form,
                       beer = self.beer)

    def post(self):
        form = BeerForm(self.request.POST, self.country)
        if form.validate():
            self.error = "something"
            self.get()

        form.populate_obj(self.beer)
        self.beer.put()
        return self.redirect(self.request.path)
