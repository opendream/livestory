from django.db import models
from django.utils import simplejson as json

from common.utilities import capfirst
import urllib

class Location(models.Model):
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    
    # Optional
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)

    def __unicode__(self):
    	return '%s: %s' % (self.country, self.city)
    
    def save(self, *args, **kwargs):
        self.country = capfirst(self.country)
        self.city = capfirst(self.city)
        
        exist = Location.objects.filter(country=self.country, city=self.city)
        if exist.count():
            self.id = exist[0].id
        else:
            resp = urllib.urlopen('http://maps.googleapis.com/maps/api/geocode/json?address=%s,%s&sensor=false' % (self.country, self.city))
            data = json.load(resp)
            if data['status'] == 'OK':
                location = data['results'][0]
                self.lat = str(location['geometry']['location']['lat'])
                self.lng = str(location['geometry']['location']['lng'])
            else:
                self.lat = ''
                self.lng = ''
            
        super(Location, self).save(*args, **kwargs)