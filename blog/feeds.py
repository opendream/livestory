from django.contrib.syndication.views import Feed
from blog.models import Blog

class LatestEntriesFeed(Feed):
    title = "OxfamLivestories latest stories."
    link = "/"
    description = "Updates on new stories to oxfamlivestories.org."
    
    def items(self):
        return Blog.objects.order_by('-published')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_categories(self, item):
        return (item.category.name, )

    def item_author_name(self, item):
        return item.user.get_profile().get_full_name()