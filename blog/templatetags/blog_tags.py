from django import template
from django.utils import simplejson as json

from location.models import Location
from taggit.models import Tag

register = template.Library()

@register.simple_tag()
def tags_js():
  tags_raw = Tag.objects.all()
  tags = []
  for tag in tags_raw:
    tags.append(tag.name)

  return '''
<script type="text/javascript">

$(document).ready(function() {
  $('#id_tags').tagit({
    availableTags: ['%s'],
    allowSpaces: true,
    caseSensitive: false,
    removeConfirmation: true,
  });
});

</script>
''' % "', '".join(tags)

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
    source: data.countries\n\
  }).keyup(function(e) {\n\
    if (country_val != this.value) {\n\
      $city.val('');\n\
      country_val = this.value;\n\
    }\n\
  });\n\
  $city.focus(function(e) {\n\
    cityTypeahead($country.val());\n\
  });\n\
  if ($country.val() != '') {\n\
    cityTypeahead(country_val)\n\
  }\n\
});\n\
</script>" % (countries_str, ",".join(cities_arr))
    return inline_js

@register.simple_tag
def textcounter_js():
    maxlength = 300;
    inline_js = "<script>\n\
$(document).ready(function() {\n\
  var maxlength = %s;\n\
  $('.textcounter').each(function(delta, el) {\n\
    var $form = $(el).closest('form');\n\
    var $buttons = $('button[type=submit]', $form);\n\
    var $counter = $('span#'+ $(el).attr('id') +'_counter');\n\
    var updateLength = function() {\n\
      var len = parseInt($(el).val().length);\n\
      var remaining = maxlength - len;\n\
      if (remaining < 0) {\n\
        $counter.closest('.control-group').addClass('error');\n\
        //$buttons.removeAttr('disabled', 'disabled');\n\
      } else {\n\
        $counter.closest('.control-group').removeClass('error');\n\
        $buttons.removeAttr('disabled');\n\
      }\n\
      $counter.html(remaining + '');\n\
    }\n\
    $(el).keyup(function(e) { updateLength() });\n\
    updateLength();\n\
  });\n\
});\n\
</script>"
    return inline_js % maxlength