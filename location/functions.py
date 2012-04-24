
from common.utilities import capfirst

from models import Location

def persist_location(city, country):
    try:
        location = Location.objects.get(country=capfirst(country), city=capfirst(city))
    except Location.DoesNotExist:
        return Location.objects.create(country=capfirst(country), city=capfirst(city))

    # For unittest maybe create duplicate location
    except Location.MultipleObjectsReturned:
        location = Location.objects.filter(country=ucwords(country), city=ucwords(city)).order_by('-id')[0]

    return location