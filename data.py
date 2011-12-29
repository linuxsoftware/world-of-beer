# -*- coding: utf-8 -*-

import os
import sys
import time
import datetime
from google.appengine.ext import db
from google.appengine.api import users

class WorldOfBeer(object):
    def getCountry(self, name):
        data = Country.get_by_key_name(name)
        return data
        #query = Country.gql("where name = :name", name=name)
        #results = query.fetch(1)
        #if results:
        #    return results[0]
        #else:
        #    return None

    def createCountry(self, shortName):
        longName = shortName.replace('-', ' ').title()
        longName = longName.replace('Of', 'of')
        longName = longName.replace('The', 'the')
        longName = longName.replace('And', 'and')
        longName = longName.replace("D'Ivoire", "d'Ivoire")
        longName = longName.replace("(Fyrom)", "")
        data = Country(key_name=shortName, name=longName)
        data.put()
        return data

    def getBrewery(self, name):
        # TODO
        pass

    def getBeer(self, name):
        # TODO
        pass

# access WorldOfBeer data through this object
world = WorldOfBeer()

class Country(db.Model):
    name        = db.StringProperty(required=True)
    flag        = db.BlobProperty()
    description = db.TextProperty()
    map         = db.BlobProperty()
    capital     = db.StringProperty()
    area        = db.IntegerProperty()
    population  = db.IntegerProperty()
    perCapBeer  = db.FloatProperty()
    totBeer     = db.IntegerProperty()
    #languages   = db.StringListProperty()
    languages   = db.StringProperty()
    climate     = db.StringProperty()
    #agriculture = db.StringListProperty()
    agriculture = db.StringProperty()
    #industry    = db.StringListProperty()
    industry    = db.StringProperty()
    government  = db.StringProperty()
    #borders     = db.StringListProperty()
    borders     = db.StringProperty()

class BeerRequest(db.Model):
    code        = db.StringProperty(required=True)
    name        = db.StringProperty(required=True)
    locRequest  = db.StringProperty(required=True)

class Brewery(db.Model):
    name        = db.StringProperty(required=True)
    logo        = db.BlobProperty()
    description = db.TextProperty()
    country     = db.ReferenceProperty(Country)

class Beer(db.Model):
    name        = db.StringProperty(required=True)
    picture     = db.BlobProperty()
    description = db.TextProperty()
    brewery     = db.ReferenceProperty(Brewery)

class Drinker(db.Model):
    name        = db.StringProperty(required=True)
    account     = db.UserProperty()

class Review(db.Model):
    when        = db.DateProperty()
    beer        = db.ReferenceProperty(Brewery)
    reviewer    = db.ReferenceProperty(Drinker)

