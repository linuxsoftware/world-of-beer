# -*- coding: utf-8 -*-
import sys
import os
from os.path import join, dirname

from cgi import FieldStorage
from wtforms import Form
from wtforms.ext.appengine.db import model_form
from wtforms.widgets import html_params, HTMLString
from wtforms.fields import Field, _unset_value
from mako.template import Template
from google.appengine.ext import db
from google.appengine.api import memcache

from data import world, Country, Brewery, Beer

__all__ = ( "CountryForm", "BreweryForm", "BeerForm" )

class ImageWidget(object):
    """
    Very simple image selection widget
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
        if valuelist:
            if isinstance(valuelist[0], FieldStorage):
                data = valuelist[0].value
            else:
                data = valuelist[0]
            if data:
                self.data = db.Blob(data)
        # NB If we reset on no data then a image must always be rechosen
        # so we don't do that

    def _value(self):
        return self.name + ".png"
    
class ImagePreviewWidget(object):
    """
    Super dynamic image selection widget
    implemented as a Mako template
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault("path", "")
        template = Template(filename=join(dirname(__file__), 
                                          "templates",
                                          "preview.html"))
        return template.get_def("image").render(field=field, **kwargs)

class ImagePreviewField(ImageField):
    widget = ImagePreviewWidget()

    def process(self, formdata, data=_unset_value):
        self.process_errors = []
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
        try:
            self.process_data(data)
        except ValueError, e:
            self.process_errors.append(e.args[0])

        if formdata:
            try:
                self.raw_data = self._getRawData(formdata)
                self.process_formdata(self.raw_data)
            except ValueError, e:
                self.process_errors.append(e.args[0])

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError, e:
                self.process_errors.append(e.args[0])

    def _getRawData(self, formdata):
        if not self.name in formdata:
            return []
        rawData = formdata.getlist(self.name)
        if rawData and rawData[0] != u'':
            return rawData
        return self._getRawPreviewData(formdata)

    def _getRawPreviewData(self, formdata):
        previewName = "%sPreview" % self.name
        if not previewName in formdata:
            return []
        previewData = formdata.getlist(previewName)
        if not previewData:
            return []
        previewId = previewData[0]
        if not previewId:
            return []
        # TODO validation?
        image = memcache.get(previewId, namespace="ImagePreview")
        if not image:
            return []
        return [ image ]

class WobForm(Form):
    """WobForm allows me to extend the wtforms.Form"""
    # I'm sure there's more clever ways to do this, but this works
    @classmethod
    def hasImageField(cls, name):
        fieldClass = getattr(getattr(cls, name, object), 'field_class', None)
        return issubclass(fieldClass, ImageField)

ModelCountryForm = model_form(Country, WobForm,
                              field_args = 
                              { 
                               "perCapBeer": { "label": "Beer consumed per capita" },
                               "totBeer":    { "label": "Total beer consumption" }, 
                              })
class CountryForm(ModelCountryForm):
    flag = ImagePreviewField(**ModelCountryForm.flag.kwargs)
    map  = ImagePreviewField(**ModelCountryForm.map.kwargs)

ModelBreweryForm = model_form(Brewery, WobForm)
class BreweryForm(ModelBreweryForm):
    logo = ImagePreviewField(**ModelBreweryForm.logo.kwargs)

ModelBeerForm = model_form(Beer, WobForm)
class BeerForm(ModelBeerForm):
    picture = ImagePreviewField(**ModelBeerForm.picture.kwargs)

