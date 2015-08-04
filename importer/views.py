import datetime as dt
from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.template import RequestContext, loader
from data.models import *
from .models import *
from os import remove
from os.path import isfile
from dashboard.views import *
import pdb

# Current deprecated to be imporved in the future when im not lazy
# #def index(request):
#     assetnames = ', '.join([a['name'] for a in Asset.objects.values('name')])
#
#     # Template and output
#     template = loader.get_template('importer/index.html')
#     context = RequestContext(request, {'assetnames': assetnames})
#
#     return HttpResponse(template.render(context))
#
# def confirm(request):
#     startDate = dt.datetime(2015,1,1)
#     endDate = dt.datetime.now()
#     outputlog = importPrices(startDate, endDate)
#
#     # Template and output
#     template = loader.get_template('importer/index.html')
#     context = RequestContext(request, {'log': outputlog})
#
#     return HttpResponse(template.render(context))

def eodupdate(request):
    # Update price for the past two days
    log = ['Updating Asset Prices']
    days = dt.timedelta(days = 2)
    now = dt.datetime.now()
    now = dt.datetime(now.year, now.month, now.day)
    ilog = importPrices(startDate= now - days, endDate = now)
    log.append('importPrice() log: ')
    log.append('<br/>'.join(ilog))

    # Update Dividends for past two days
    log.append('')
    log.append('Updating Dividends')
    dlog = importDividends(startDate= now - days, endDate = now)
    log.append('importDividends() log: ')
    log.append('<br/>'.join(dlog))

    # Update Exchange Rate
    log.append('')
    log.append('Getting USDCAD Quote')
    crncy = Asset.objects.filter(name__exact = 'USDCAD')[0]
    q = getQuote(crncy.ticker)
    AssetPrice(assetid= crncy, date = now, price = q).save()
    log.append('Price: $C'+str(q)+' --- Saved')

    # Update Portfolio
    log.append('')
    log.append('Generating Portfolio')
    plog = Portfolio().generatePortfolioTimeSeries(sDate = now - days)
    log.append('generatePortfolioTimeSeries() log: ')
    log.append('<br/>'.join(plog))

    return HttpResponse('<br/>'.join(log))