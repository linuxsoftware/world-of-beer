# -*- coding: utf-8 -*-
import sys
import os
from os.path import join, dirname
import time

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
    if len(image) < memcache.MAX_VALUE_SIZE:
        # TODO check size in validation
        timeout = 3600 # 1 hour
        memcache.set(previewId, image, timeout, namespace="ImagePreview")
    request.response.headers['Content-Type'] = "text/plain"
    request.response.out.write("{previewId: '%s'}" % previewId)


def getImagePreview(request):
    if request.method != "GET":
        raise exc.HTTPMethodNotAllowed()
    request.path_info_pop() #/preview
    request.path_info_pop() #/time
    previewId = request.path_info
    image = memcache.get(previewId, namespace="ImagePreview")
    if image:
        #TODO validation use ImageField?
        headers = request.response.headers
        headers["Expires"]        = "Sat, 26 Jul 1997 05:00:00 GMT"
        headers["Cache-Control"]  = "no-store, no-cache, must-revalidate"
        headers['Content-Type']   = "image/png"
        request.response.out.write(image)


class WobHandler(RequestHandler):
    """This is a generic WoB request handler"""
    Form = None
    view = None
    edit = None
    
    def __init__(self, request, response, wobObj=None):
        RequestHandler.__init__(self, request, response)
        self.wobObj = wobObj

    def dispatch(self):
        # memories of bobo traverse
        name = self.request.path_info_pop()
        if name:
            if name.endswith('.png') and self.Form.hasImageField(name[:-4]):
                return self.getImage(self.wobObj, name[:-4])
            else:
                return self.traverseTo(name)

        return RequestHandler.dispatch(self)

    def get(self):
        if self.request.query_string == "edit":
            form = self.Form(obj=self.wobObj)
            template = "edit_%s.html" % self.name
        else:
            form = self.Form()
            template = "%s.html" % self.name
        kwargs = { "form":    form,
                   self.name: self.wobObj }
        renderTemplate(self.request, template, **kwargs)

    def post(self):
        form = self.Form(self.request.POST, self.wobObj)
        if form.validate():
            self.error = "something"
            return self.get()
        form.populate_obj(self.wobObj)
        self.wobObj.put()
        return self.redirect(self.request.path)

    def getImage(self, wobObj, field):
        if self.request.method != "GET":
            raise exc.HTTPMethodNotAllowed()
        image = getattr(wobObj, field, "")
        self.response.headers['Content-Type'] = "image/png"
        self.response.out.write(image)
        return None

    def _findBrewery(self, name):
        # TODO
        #brewery = world.getBrewery(name)
        return None

    def _findBeer(self, name):
        # TODO
        return None

    def err404(self, msg):
        self.error(404)
        self.response.out.write(msg)


class MainHandler(WobHandler):
    def __init__(self, request, response):
        WobHandler.__init__(self, request, response)

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


class CountryHandler(WobHandler):
    Form = CountryForm
    name = "country"
    
    def traverseTo(self, name):
        brewery = self._findBrewery(name)
        if brewery:
            handler = BreweryHandler(self.request, self.response, brewery)
            return handler.dispatch()
        self.err404("Cannot find brewery '%s'" % name)
        return None


class BreweryHandler(WobHandler):
    Form = BreweryForm
    name = "brewery"

    def traverseTo(self, name):
        beer = self._findBeer(name)
        if beer:
            handler = BeerHandler(self.request, self.response, beer)
            return handler.dispatch()
        self.err404("Cannot find beer '%s'" % name)
        return None


class BeerHandler(WobHandler):
    Form = BeerForm
    name = "beer"

    def traverseTo(self, name):
        self.err404("'%s' unknown" % name)
        return None

