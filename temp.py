import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'ssif.settings'
import importer.models as im
import data.models as d
import datetime as dt
import csv

import django
django.setup()

#l = im.importDividends(dt.datetime(2014,1,1), dt.datetime(2015,7,1))
#for ll in l: print(ll)
#im.importTransactions('transactions-2015.csv')
e = d.Portfolio(cash=777000)
e.generatePortfolioTimeSeries()
e.exportPortfolioTimeSeries()
#with open('a.csv', 'w') as csvf:
#    writer = csv.DictWriter(csvf, fieldnames=['date','value'])
#    writer.writeheader()
#    writer.writerow({'date': 'a', 'value': 'b'})
#    writer.writerow({'date': 'a', 'value': 'b'})