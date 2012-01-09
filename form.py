# -*- coding: utf-8 -*-
import sys
import os

from cgi import FieldStorage
from wtforms.ext.appengine.db import model_form
from wtforms.widgets import html_params, HTMLString
from wtforms.fields import Field
from google.appengine.ext import db

from data import world, Country, Brewery, Beer

class ImageWidget(object):
    """
    Renders a file input chooser field.
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        name = field.name + ".png"
        kwargs.setdefault("value", name)
        preview = HTMLString(u"<img %s/>" % html_params(name="preview_"+name,
                                                        src=name))
        inputButton = HTMLString(u"<input %s/>" % html_params(name=field.name,
                                                              type=u"file",
                                                              **kwargs))
        return preview + inputButton

class ImageField(Field):
    """
    Can render a file-upload field.  Will take any passed filename value, if
    any is sent by the browser in the post params.  This field will NOT
    actually handle the file upload portion, as wtforms does not deal with
    individual frameworks' file handling capabilities.
    """
    widget = ImageWidget()

    def process_formdata(self, valuelist):
        if valuelist and isinstance(valuelist[0], FieldStorage):
            self.data = db.Blob(valuelist[0].value)
        else:
            self.data = db.Blob('')

    def _value(self):
        return self.name + ".png"

class CountryForm(model_form(Country)):
    flag = ImageField("flag")
    map  = ImageField("map")

BreweryForm = model_form(Brewery)
BeerForm = model_form(Beer)

