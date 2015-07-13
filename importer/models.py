from data.models import *
import pandas as pd
import urllib.parse as parser
import datetime as dt

#https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
def importPrices(startDate, endDate):
    log = []
    alist = Asset.objects.all()
    log.append('Getting prices '+startDate.strftime('%d-%m-%Y')+' - '
               +endDate.strftime('%d-%m-%Y')+' for Asset List: ')
    log.append(', '.join([s.ticker for s in alist]))
    log.append('')

    for i,a in enumerate(alist):
        payload = {
            's': a.ticker, # Ticker Name
            'a': startDate.month-1,'b': startDate.day, 'c': startDate.year,#Start Date MM DD YYYY , MINUS MONTH BY 1
            'd': endDate.month-1,'e': endDate.day, 'f': endDate.year,#End  Date MM DD YYYY , MINUS MONTH BY 1
            'g': 'd' # Daily Data
        }

        price = pd.read_csv('http://ichart.yahoo.com/table.csv?'+parser.urlencode(payload))
        price = price[['Date','Adj Close']]
        log.append('Importing '+str(len(price))+' Rows of Price Data for '+str(a.name))
        for i,p in price.iterrows():
            # Check to see if it already exists
            if(AssetPrice.objects.filter(assetid__exact=a,date__exact = dt.datetime.strptime(p['Date'], '%Y-%m-%d')).exists()):
                log.append('Already Exists, Row will not be saved')
            else:
                b = AssetPrice(assetid = a, date = dt.datetime.strptime(p['Date'], '%Y-%m-%d'), price = p['Adj Close'])
                log.append('Saving - '+str(a.assetid)+' '+p['Date']+' : '+str(p['Adj Close']))
                b.save()
        log.append('')

    return log

def importDividends(startDate, endDate):
    log = []
    alist = Asset.objects.all()
    log.append('Getting Dividends '+startDate.strftime('%d-%m-%Y')+' - '
               +endDate.strftime('%d-%m-%Y')+' for Asset List: ')
    log.append(', '.join([s.ticker for s in alist]))
    log.append('')

    for i,a in enumerate(alist):
        payload = {
            's': a.ticker, # Ticker Name
            'a': startDate.month-1,'b': startDate.day, 'c': startDate.year,#Start Date MM DD YYYY , MINUS MONTH BY 1
            'd': endDate.month-1,'e': endDate.day, 'f': endDate.year,#End  Date MM DD YYYY , MINUS MONTH BY 1
            'g': 'v' # Daily Data
        }

        dividends = pd.read_csv('http://ichart.yahoo.com/table.csv?'+parser.urlencode(payload))
        dividends = dividends[['Date','Dividends']]
        log.append('Importing '+str(len(dividends))+' Rows of Dividend Data for '+str(a.name))
        for i,d in dividends.iterrows():
            # Check to see if it already exists
            if(AssetDividend.objects.filter(assetid__exact=a,date__exact = dt.datetime.strptime(d['Date'], '%Y-%m-%d')).exists()):
                log.append('Already Exists, Row will not be saved')
            else:
                b = AssetDividend(assetid = a, date = dt.datetime.strptime(d['Date'], '%Y-%m-%d'), dps = d['Dividends'])
                log.append('Saving - '+str(a.assetid)+' '+d['Date']+' : '+str(d['Dividends']))
                b.save()
        log.append('')

    return log

def importTransactions(csv):
    t = pd.read_csv(csv)
    dateformat = '%m/%d/%Y'
    if(set(['ticker', 'date', 'shares']).issubset(t.columns)):
         for i,row in t.iterrows():
             a = Asset.objects.filter(ticker__exact= row['ticker'])[0]
             trans = Transaction(assetid = a, date = dt.datetime.strptime(row['date'], dateformat), shares = row['shares'])
             print('Saving: '+str(trans))
             trans.save()
    else:
        return {'error': 'Poorly formatted import, should be three columns: ticker, date and shares'}
