import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'ssif.settings'
import importer.models as im
import data.models as d
import datetime
import csv

import django
django.setup()

p = d.Portfolio()
print(p.calculatePortfolioValue(datetime.datetime(2014,6,30)))
pv = p.calculatePortfolioTimeSeries()

#with open('a.csv', 'w') as csvf:
#    writer = csv.DictWriter(csvf, fieldnames=['date','value'])
#    writer.writeheader()
#    for v in pv:
#        writer.writerow(v)
#im.importPrices(datetime.date(2014,1,1), datetime.date(2015,7,1))