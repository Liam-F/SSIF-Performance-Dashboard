from django.contrib import admin

from .models import Asset, AssetPrice, Transaction, Portfolio

admin.site.register(Asset)
admin.site.register(AssetPrice)
admin.site.register(Transaction)
admin.site.register(Portfolio)