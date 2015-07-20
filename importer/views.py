import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from data.models import Asset, AssetPrice
from .models import importPrices

def index(request):
    assetnames = ', '.join([a['name'] for a in Asset.objects.values('name')])

    # Template and output
    template = loader.get_template('importer/index.html')
    context = RequestContext(request, {'assetnames': assetnames})

    return HttpResponse(template.render(context))

def confirm(request):
    startDate = datetime.date(2015,1,1)
    endDate = datetime.datetime.now()
    outputlog = importPrices(startDate, endDate)

    # Template and output
    template = loader.get_template('importer/index.html')
    context = RequestContext(request, {'log': outputlog})

    return HttpResponse(template.render(context))
