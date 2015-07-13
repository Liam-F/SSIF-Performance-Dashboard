from django.db import models
from django.db.models import Sum
import csv
import datetime as dt

# Contain all Asset Descriptions and properties
class Asset(models.Model):
    assetid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    ticker = models.CharField(max_length=10, unique=True)
    industry = models.CharField(max_length=100)
    country = models.CharField(max_length=50)

    def __str__(self):
        return str(self.assetid)+': '+self.name+' ('+self.ticker+') | Country: '+self.country+' | Industry: '+self.industry

    def aggregateAssetTransactions(self, ddate):
        s = Transaction.objects.filter(date__lte=ddate, assetid__exact=self.assetid).aggregate(Sum('shares'))
        return s['shares__sum'] or 0

    def calculateHoldingValue(self, ddate):
        # Get a list of all transactional shares previous to this date
        s = self.aggregateAssetTransactions(ddate)

        # get the current price as of this date OR the next available day
        p = AssetPrice.objects.filter(date__lte=ddate, assetid__exact=self.assetid).order_by('-date')

        if not p or not s: # If no price is available
            return 0
        else: # Total Shares * Price
            return s*p[0].price

class AssetPrice(models.Model):
    assetid = models.ForeignKey(Asset, unique_for_date='date')
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return 'Name: '+str(self.assetid.name)+' | Date: '+self.date.strftime('%Y-%m-%d')+' | '+str(self.price)

class AssetDividend(models.Model):
    assetid = models.ForeignKey(Asset, unique_for_date='date')
    date = models.DateTimeField()
    dps = models.DecimalField(max_digits=5,decimal_places=2)

    def __str__(self):
        return 'Name: '+str(self.assetid.name)+' | Date: '+self.date.strftime('%Y-%m-%d')+' | DPS: '+str(self.dps)

class Transaction(models.Model):
    transid = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    shares = models.DecimalField(max_digits=10, decimal_places=3)
    assetid = models.ForeignKey(Asset)

    def __str__(self):
        if(self.shares > 0):
            otype = 'BUY'
        elif(self.shares < 0):
            otype = 'SELL'
        else:
            return 'NO ACTION'
        return otype+' '+str(self.shares)+' of '+self.assetid.name+' ('+self.assetid.ticker+') on close of '+self.date.strftime('%Y-%m-%d')

class Portfolio(models.Model):
    portfolioid = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    value = models.DecimalField(max_digits=10, decimal_places=3, default=0, unique_for_date='date')
    cash = models.DecimalField(max_digits=10, decimal_places=3, default=1000000, unique_for_date='date') #Set default as initial Cash!!

    def calculatePortfolioValue(self, ddate):
        # If portfolio exists on today, delete it
        Portfolio.objects.filter(date__exact=ddate).delete()

        self.value = 0

        # Find Last period Portfolio and see if there's been transactions before
        pminusone = Portfolio.objects.filter(date__lte=ddate).order_by('-date') # Get the most recent cash
        if pminusone:
            self.cash = pminusone[0].cash
        # If theres no transactions before this date, then its just cash!
        tminus = Transaction.objects.filter(date__lte=ddate)
        if not tminus:
            return self.cash

        for a in Asset.objects.all():
           self.value += a.calculateHoldingValue(ddate)

           # Calculate Dividends on this date
           aggTrans = a.aggregateAssetTransactions(ddate)
           # ASSUMPTION: Only One dividend may be distributed that dividend day for each asset
           d = AssetDividend.objects.filter(date__exact=ddate, assetid__exact=a.assetid)
           if d:
            self.cash += aggTrans*d[0].dps

           # Reconcile Cash
           # Asset Price as of the transaction date OR later if no price data is available
           p = AssetPrice.objects.filter(date__lte=ddate, assetid__exact=a.assetid).order_by('-date')
           if not p:
               p = 0

           # ASSUMPTION: Transactions must be made on a valid trading date or cash will not be deducted
           for tr in Transaction.objects.filter(date__exact = ddate, assetid__exact = a.assetid):
               self.cash -= tr.shares*p[0].price # Subtracted because negative shares = increase in cash and vice versa

        return self.value+self.cash

    def generatePortfolioTimeSeries(self, sDate=dt.datetime(2015,1,1), eDate=dt.datetime.now()):
        # GETS THE FIRST ASSET'S PRICE LENGTH (BAD ASSUMPTION FIX IF NEEDED) CURRENT STOCK = AAPL
        dates = [d['date'] for d in AssetPrice.objects.filter(assetid__exact=1, date__gte=sDate, date__lte=eDate).order_by('date').values('date')]

        # Get all Portfolio Value at those dates
        for d in dates:
            p = Portfolio(date=d, cash=self.cash, value=self.value)
            val = p.calculatePortfolioValue(d)
            print('Saving Portfolio on '+d.strftime('%Y-%m-%d')+' Portfolio Value: $'+str(val)+' Cash: $'+str(p.cash))
            p.save()

        return 1

    def __str__(self):
        return 'Portfolio on '+self.date.strftime('%Y-%m-%d')+' Portfolio Value: $'+str(self.value)+' Cash: $'+str(self.cash)

    def exportPortfolioTimeSeries(self):
        port = Portfolio.objects.all().order_by('date')
        with open('ts.csv', 'w', newline='') as csvf:
            w = csv.DictWriter(csvf, fieldnames = ['date','portfolio value','cash'])
            w.writeheader()
            for p in port:
                w.writerow({'date': p.date, 'portfolio value': p.value, 'cash': p.cash})


