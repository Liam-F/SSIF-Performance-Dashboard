from django.contrib import admin

from .models import *

admin.site.register(Asset)
admin.site.register(AssetPrice)
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(AssetDividend)