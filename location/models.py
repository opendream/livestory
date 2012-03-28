from django.db import models
from django.utils import simplejson as json

from common import ucwords
import urllib

class Location(models.Model):
    country = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    
    # Optional
    lat = models.CharField(max_length=50)
    lng = models.CharField(max_length=50)

    def __unicode__(self):
    	return '%s: %s' % (self.country, self.city)
    
    def save(self):
        self.country = ucwords(self.country)
        self.city = ucwords(self.city)
        
        if not self.lat or not self.lng:
            resp = urllib.urlopen('http://maps.googleapis.com/maps/api/geocode/json?address=%s,%s&sensor=false' % (self.country, self.city))
            data = json.load(resp)
            if data['status'] == 'OK':
                match_country = False
                match_city = False
                
                location = data['results'][0]
                for com in location['address_components']:
                    if not match_country and 'country' in com['types']:
                        self.country = com['long_name']
                        match_country = True
                    elif not match_city and 'country' not in com['types']:
                        if 'locality' in com['types']:
                            self.city = com['long_name']
                            match_city = True
                        elif 'administrative_area_level_1' in com['types']:
                            self.city = com['long_name']
                            match_city = True
                        
                if not match_country or not match_city:
                    raise self.DoesNotExist
                    
                
                exist = Location.objects.filter(country=self.country, city=self.city)
                if exist.count():
                    self.id = exist[0].id
                    
                self.lat = str(location['geometry']['location']['lat'])
                self.lng = str(location['geometry']['location']['lng'])
                
            elif data['status'] == 'ZERO_RESULTS':
                raise self.DoesNotExist
                
            else:
                # TODO: error can not connection
                self.lat = '0'
                self.lng = '0'
            
        super(Location, self).save()