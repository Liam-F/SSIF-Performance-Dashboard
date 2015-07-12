import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'ssif.settings'
import importer.models as im
import data.models as d
import datetime
import csv

import django
django.setup()

#im.importTransactions('transactions-jan1.csv')
#d.Portfolio().generatePortfolioTimeSeries()
d.Portfolio().exportPortfolioTimeSeries()
#with open('a.csv', 'w') as csvf:
#    writer = csv.DictWriter(csvf, fieldnames=['date','value'])
#    writer.writeheader()
#    writer.writerow({'date': 'a', 'value': 'b'})
#    writer.writerow({'date': 'a', 'value': 'b'})