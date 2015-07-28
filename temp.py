import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'ssif.settings'
from importer.models import *
from data.models import *
import datetime as dt
import csv
import numpy as np

import django
django.setup()

#l = im.importDividends(dt.datetime(2014,1,1), dt.datetime(2015,7,1))
#for ll in l: print(ll)
#im.importTransactions('transactions-2015.csv')
#e = d.Portfolio(cash=776980)
#e.generatePortfolioTimeSeries(sDate = dt.datetime(2015,7,12))
#e.exportPortfolioTimeSeries()

from dashboard.views import *
portfolioindex()
# Portfolio.objects.all().delete()
# Portfolio(cash=528728.96).generatePortfolioTimeSeries(sDate=dt.datetime(2013,1,1), eDate=dt.datetime.now())

# with open('csv/USDCAD.csv', 'rt') as csvf:
#     read = csv.DictReader(csvf, fieldnames=['Date', 'USDCAD'])
#     next(read)
#     for r in read:
#        aa = Asset.objects.filter(ticker__exact='USDCAD=X')[0]
#        a = AssetPrice(assetid=aa, date = dt.datetime.strptime(r['Date'], '%m/%d/%Y'), price=r['USDCAD'])
#        print('Saving '+a.__str__())
#        a.save()

#with open('a.csv', 'w') as csvf:
#    writer = csv.DictWriter(csvf, fieldnames=['date','value'])
#    writer.writeheader()
#    writer.writerow({'date': 'a', 'value': 'b'})
#    writer.writerow({'date': 'a', 'value': 'b'})

#a = Asset.objects.filter(industry__exact = 'Basic Materials')
#for asset in a:
#     asset.managerid = EquityManager.objects.filter(name__exact = 'Chris Koutsikaloudis')[0]
#     asset.save()


