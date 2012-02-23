from django import template
from django.utils import simplejson as json

from location.models import Location

register = template.Library()

@register.simple_tag()
def location_js():
    locations = Location.objects.all()
    countries = []
    cities = {}
    for location in locations:
        if location.country not in countries:
            countries.append(location.country)
        if not cities.get(location.country):
            cities[location.country] = []
        cities[location.country].append(location.city)

    countries_str = '","'.join(countries)
    cities_arr = []
    for country, _cities in cities.iteritems():
        cities_arr.append('"%s": ["%s"]' % (country, '","'.join(_cities)))
    inline_js = "<script>\n\
$(document).ready(function() {\n\
  var data = {'countries': [\"%s\"], 'cities': {%s}}\n\
  var $country = $('#id_country');\n\
  var $city = $('#id_city');\n\
  var country_val = $country.val();\n\
  var cityTypeahead = function(country) {\n\
    if ($city.data('typeahead')) {\n\
      var cities = [];\n\
      if (typeof country == 'string' && country != '' && data.cities[country]) {\n\
        cities = data.cities[country];\n\
      }\n\
      $city.data('typeahead').source = cities;\n\
    } else {\n\
      $city.typeahead({\n\
          source: data.cities[country]\n\
      })\n\
    }\n\
  };\n\
  $country.typeahead({\n\
    onSelect: function(country) {\n\
      cityTypeahead(country);\n\
    },\n\
    source: data.countries\n\
  }).keyup(function(e) {\n\
    //if (e.keyCode != 13 && e.keyCode != 27) {\n\
    if (country_val != this.value) {\n\
      $city.val('');\n\
      country_val = this.value;\n\
    }\n\
  });\n\
  $city.focus(function(e) {\n\
    cityTypeahead(country_val);\n\
  });\n\
  if (country_val != '') {\n\
      cityTypeahead(country_val)\n\
  }\n\
});\n\
</script>" % (countries_str, ",".join(cities_arr))
    return inline_js