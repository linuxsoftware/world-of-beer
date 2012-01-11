# -*- coding: utf-8 -*-
import sys
import os

from cgi import FieldStorage
from wtforms import Form
from wtforms.ext.appengine.db import model_form
from wtforms.widgets import html_params, HTMLString
from wtforms.fields import Field
from google.appengine.ext import db

from data import world, Country, Brewery, Beer

__all__ = ( "CountryForm", "BreweryForm", "BeerForm" )

class ImageWidget(object):
    """
    Renders a file input chooser field.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        name = "%s.png" % field.name
        url = kwargs.get("url", "%s/%s" % (kwargs.get("path"), name))
        kwargs.setdefault("value", name)
        preview = HTMLString(u"<img %s />" % html_params(name="preview_"+name,
                                                         src=url))
        inputButton = HTMLString(u"<input %s  />" % html_params(name=field.name,
                                                                type=u"file",
                                                                **kwargs))
        return preview + inputButton

class ImageField(Field):
    widget = ImageWidget()

    def process_formdata(self, valuelist):
        if valuelist and isinstance(valuelist[0], FieldStorage):
            self.data = db.Blob(valuelist[0].value)
        # NB If we reset on no data then a image must always be rechosen
        # so we don't do that

    def _value(self):
        return self.name + ".png"

class WobForm(Form):
    """WobForm allows me to extend the wtforms.Form"""
    # I'm sure there's more clever ways to do this, but this works
    @classmethod
    def hasImageField(cls, name):
        fieldClass = getattr(getattr(cls, name, object), 'field_class', None)
        return fieldClass is ImageField

ModelCountryForm = model_form(Country, WobForm,
                              field_args = 
                              { 
                               "perCapBeer": { "label": "Beer consumed per capita" },
                               "totBeer":    { "label": "Total beer consumption" }, 
                              })
class CountryForm(ModelCountryForm):
    flag = ImageField(**ModelCountryForm.flag.kwargs)
    map  = ImageField(**ModelCountryForm.map.kwargs)

ModelBreweryForm = model_form(Brewery, WobForm)
class BreweryForm(ModelBreweryForm):
    logo = ImageField(**ModelBreweryForm.logo.kwargs)

ModelBeerForm = model_form(Beer, WobForm)
class BeerForm(ModelBeerForm):
    picture = ImageField(**ModelBeerForm.picture.kwargs)

