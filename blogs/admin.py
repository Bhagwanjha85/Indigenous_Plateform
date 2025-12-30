from django.contrib import admin
from .models import *
from .models import SiteView

# Register your models here.
admin.site.register(Blog)

admin.site.register(Category)

admin.site.register(Comment)

admin.site.register(Reply)

admin.site.register(Bookmark)
admin.site.register(SiteView)