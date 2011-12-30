# -*- coding: utf-8 -*-

import os
from os import path
import sys
import time
import webapp2
from google.appengine.api import users
from google.appengine.ext import db
from mako.lookup import Template, TemplateLookup
from mako import exceptions
from wtforms.ext.appengine.db import model_form
from data import world

#TODO move this out to data or a new dataedit module
from data import Country
CountryForm = model_form(Country)


class MakoRenderer(object):
    _lookup = TemplateLookup(directories=[path.join(path.dirname(__file__),
                                                    "templates")],
                             input_encoding='utf-8',
                             output_encoding='utf-8',
                             filesystem_checks=True)

    def _renderTemplate(self, templateName, **data):
        write = self.response.out.write
        try:
            template = MakoRenderer._lookup.get_template(templateName)
            try:
                #write(template.render(reqvars=self.__dict__))
                write(template.render(**data))
            except:
                self.error(500)
                write(exceptions.html_error_template().render())
        except exceptions.TopLevelLookupException:
            self.error(404)
            write("Cant find template '%s' for '%s'" % (templateName,
                                                        self.request.path))
        except:
            self.error(500)
            write(exceptions.html_error_template().render())


# TODO merge Map and Beers into Main?
class Map(webapp2.RequestHandler, MakoRenderer):
    def get(self):
        self._renderTemplate("map.html")

class Beers(webapp2.RequestHandler, MakoRenderer):
    def get(self):
        self._renderTemplate("beers.html")

class Main(webapp2.RequestHandler, MakoRenderer):
    """This is the main webui class for WoB"""

    def initialize(self, request, response):
        webapp2.RequestHandler.initialize(self, request, response)
        self.country = None
        self.brewery = None
        self.beer    = None
        if request.path_info:
            component = unicode(request.path_info_peek(), 'utf-8')
            self._findCountry(component)
            if self.country:
                request.path_info_pop()
        if request.path_info:
            component = unicode(request.path_info_peek(), 'utf-8')
            self._findBrewery(request.path_info_peek())
            if self.brewery:
                request.path_info_pop()
        if request.path_info:
            component = unicode(request.path_info_peek(), 'utf-8')
            self._findBeer(component)
        if not self.country and request.path_info:
            component = unicode(request.path_info_peek(), 'utf-8')
            self.country = world.createCountry(component)

    def _findCountry(self, name):
        self.country = world.getCountry(name)

    def _findBrewery(self, name):
        # TODO
        #self.brewery = name
        pass

    def _findBeer(self, name):
        # TODO
        #self.beer = name
        pass

    def get(self):
        template = ''
        form = None
        if self.request.query_string == "edit":
            template = 'edit_'
            #TODO move this out to data or a new dataedit module
            form = CountryForm(obj=self.country)
        if self.beer:
            template += 'beer.html'
        elif self.brewery:
            template += 'brewery.html'
        elif self.country:
            template += 'country.html'
        #self.template = template;
        #template = 'debug1.html';

        if template:
            self._renderTemplate(template,
                                 form=form,
                                 url=self.request.url,
                                 reqvars = self.__dict__,
                                 country = self.country,
                                 brewery = self.brewery,
                                 beer    = self.beer)
        else:
            self.error(404)
            self.response.out.write("Cant find country for '%s'" %
                                    self.request.path)

    def post(self):
        #TODO move this out to data or a new dataedit module
        form = CountryForm(self.request.str_POST, self.country)
        if form.validate():
            form.populate_obj(self.country)
            self.country.put()

        template = ''
        if self.request.query_string == "edit":
            template = 'edit_'
            #TODO move this out to data or a new dataedit module
        if self.beer:
            template += 'beer.html'
        elif self.brewery:
            template += 'brewery.html'
        elif self.country:
            template += 'country.html'
        #self.template = template;
        #template = 'debug1.html';

        if template:
            self._renderTemplate(template,
                                 form=form,
                                 url=self.request.url,
                                 reqvars = self.__dict__,
                                 country = self.country,
                                 brewery = self.brewery,
                                 beer    = self.beer)
        else:
            self.error(404)
            self.response.out.write("Cant find country for '%s'" %
                                    self.request.path)

