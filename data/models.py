from django.db import models
from django.db.models import Sum
import csv
import datetime as dt

# Contain all Asset Descriptions and properties

class EquityManager(models.Model):
    managerid = models.AutoField(primary_key = True)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length = 50)
    desc = models.CharField(max_length=2000)
    linkedin = models.CharField(max_length=100)
    twitter = models.CharField(max_length=100)
    profile = models.ImageField(upload_to = 'managers/')

    def __str__(self):
        return self.name


class Asset(models.Model):
    assetid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    ticker = models.CharField(max_length=10, unique=True)
    industry = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    managerid = models.ForeignKey(EquityManager)

    def __str__(self):
        return str(self.assetid)+': '+self.name+' ('+self.ticker+') | Country: '+self.country+' | Industry: '+self.industry

    def aggregateAssetTransactions(self, ddate):
        s = Transaction.objects.filter(date__lte=ddate, assetid__exact=self.assetid).aggregate(Sum('shares'))
        return s['shares__sum'] or 0

    # Function way too specific, consider deprecating or generalizing in the future
    def aggregateDividends(self):
        dps = 0
        divs = AssetDividend.objects.filter(assetid__exact = self.assetid)
        for d in divs:
            shares = self.aggregateAssetTransactions(ddate = d.date)
            if(shares > 0):
                dps += d.dps*shares*self.getExchangeRate(ddate = d.date)

        return dps

    def calculateHoldingValue(self, ddate):
        # Get a list of all transactional shares previous to this date
        s = self.aggregateAssetTransactions(ddate)

        # get the current price as of this date OR the next available day
        p = self.getAssetPrice(ddate)

        return s*p*self.getExchangeRate(ddate)

    def getAssetPrice(self, ddate):
        p = AssetPrice.objects.filter(date__lte=ddate, assetid__exact=self.assetid).order_by('-date')
        if not p:
            return 0
        else:
            return p[0].price

    def getReturns(self, sDate = None, eDate = None):
        if sDate is None:
            sDate = AssetPrice.objects.filter(assetid__exact = self.assetid).order_by('date')[0].date
        if eDate is None:
            eDate = AssetPrice.objects.filter(assetid__exact = self.assetid).order_by('-date')[0].date

        p = AssetPrice.objects.filter(assetid__exact = self.assetid, date__gte = sDate, date__lte = eDate).order_by('-date')
        exr = AssetPrice.objects.filter(assetid__exact = Asset.objects.filter(name__exact='USDCAD')[0], date__gte = sDate, date__lte = eDate).order_by('-date')
        r = []
        dates = []
        for i in range(0,len(p)-1):
            rate_t = exr.filter(date__lte = p[i].date)[0].price
            rate_t1 = exr.filter(date__lte = p[i+1].date)[0].price
            r.append((p[i].price*rate_t)/(p[i+1].price*rate_t1) -1)
            dates.append(p[i+1].date) # Return = % Change as of Yesterday close to Today's close

        return { 'date': dates, 'return': r}

    def getExchangeRate(self, ddate):
        # get the current exchange rate as of this date OR next available date
        # ASSUMPTION : USDCAD ONLY ATM, PORTFOLIO IS CAD DENOMINATED
        if self.country == 'US':
            exa = Asset.objects.filter(name__exact='USDCAD')[0]
            exc = AssetPrice.objects.filter(date__lte=ddate, assetid__exact=exa.assetid).order_by('-date')
            if not exc:
                return 1 # Fuck usd bulls, parity plz
            else: return exc[0].price;
        else: # add more cur
            return 1;

class AssetPrice(models.Model):
    assetid = models.ForeignKey(Asset, unique_for_date='date')
    date = models.DateTimeField()
    price = models.FloatField()

    def save(self, *args, **kwargs):
        if(not AssetPrice.objects.filter(assetid__exact=self.assetid,date__exact = self.date).exists()):
            super(AssetPrice, self).save(*args, **kwargs)

    def __str__(self):
        return 'Name: '+str(self.assetid.name)+' | Date: '+self.date.strftime('%Y-%m-%d')+' | '+str(self.price)

class AssetDividend(models.Model):
    assetid = models.ForeignKey(Asset, unique_for_date='date')
    date = models.DateTimeField()
    dps = models.FloatField()

    def save(self, *args, **kwargs):
        if(not AssetDividend.objects.filter(assetid__exact=self.assetid,date__exact = self.date).exists()):
            super(AssetDividend, self).save(*args, **kwargs)

    def __str__(self):
        return 'Name: '+str(self.assetid.name)+' | Date: '+self.date.strftime('%Y-%m-%d')+' | DPS: '+str(self.dps)

class Transaction(models.Model):
    transid = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    shares = models.FloatField()
    assetid = models.ForeignKey(Asset)

    def getCost(self):
        return (AssetPrice.objects.filter(date__lte = self.date, assetid__exact = self.assetid).order_by('-date')[0].price # Price that date or earlier
                * self.shares # Number of shares
                * self.assetid.getExchangeRate(ddate = self.date) # Account for Exchange rates (To CAD)
                )

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
    value = models.FloatField(unique_for_date='date')
    cash = models.FloatField(unique_for_date='date') #Set default as initial Cash!!

    def calculatePortfolioValue(self, ddate):
        self.value = 0

        # Find Last period Portfolio and see if there's been transactions before
        pminusone = Portfolio.objects.filter(date__lt=ddate).order_by('-date') # Get the most recent cash
        if pminusone:
            self.cash = pminusone[0].cash
        # If theres no transactions before this date, then its just cash!
        tminus = Transaction.objects.filter(date__lte=ddate)
        if not tminus:
            return self.cash

        for a in Asset.objects.all():
           self.value += a.calculateHoldingValue(ddate)
           exc = a.getExchangeRate(ddate) # get Exchange Rate to CAD

           # Calculate Dividends on this date
           aggTrans = a.aggregateAssetTransactions(ddate)
           # ASSUMPTION: Only One dividend may be distributed that dividend day for each asset
           d = AssetDividend.objects.filter(date__exact=ddate, assetid__exact=a.assetid)
           if d:
            self.cash += aggTrans*d[0].dps*exc

           # Reconcile Cash
           # Asset Price as of the transaction date OR later if no price data is available
           p = a.getAssetPrice(ddate)

           # ASSUMPTION: Transactions must be made on a valid trading date or cash will not be deducted
           for tr in Transaction.objects.filter(date__exact = ddate, assetid__exact = a.assetid):
               self.cash -= tr.shares*p*exc # Subtracted because negative shares = increase in cash and vice versa

        return self.value+self.cash

    def generatePortfolioTimeSeries(self, sDate=dt.datetime(2015,1,1), eDate=dt.datetime.now()):
        log = []
        # GETS THE FIRST ASSET'S PRICE LENGTH (BAD ASSUMPTION FIX IF NEEDED) CURRENT STOCK = AAPL
        dates = [d['date'] for d in AssetPrice.objects.filter(assetid__exact=1, date__gte=sDate, date__lte=eDate).order_by('date').values('date')]

        # Get all Portfolio Value at those dates
        for d in dates:
            p = Portfolio(date=d, cash=self.cash, value=self.value)
            # If portfolio exists on today, skip it
            # Assumption, recreating portfolio series, you need to delete it
            if (Portfolio.objects.filter(date__exact=d).exists()):
                log.append('Portfolio Exists on this date -- '+d.strftime('%Y-%m-%d')+'. Will not be saved')
                continue
            val = p.calculatePortfolioValue(d)
            log.append('Saving Portfolio on '+d.strftime('%Y-%m-%d')+' Equity Value: $'+str(p.value)+' Cash: $'+str(p.cash)+' Portfolio Value: $'+str(val))
            p.save()

        return log

    def __str__(self):
        return 'Portfolio on '+self.date.strftime('%Y-%m-%d')+' Equity Value: $'+str(self.value)+' Cash: $'+str(self.cash)

    def exportPortfolioTimeSeries(self):
        port = Portfolio.objects.all().order_by('date')
        with open('ts.csv', 'w', newline='') as csvf:
            w = csv.DictWriter(csvf, fieldnames = ['date','portfolio value','cash'])
            w.writeheader()
            for p in port:
                w.writerow({'date': p.date, 'portfolio value': p.value, 'cash': p.cash})

    def getPortfolioValue(self):
        return self.value+self.cash

    def getReturns(self, sDate = None, eDate = None):
        if sDate is None:
            sDate = Portfolio.objects.all().order_by('date')[0].date
        if eDate is None:
            eDate = Portfolio.objects.all().order_by('-date')[0].date

        p = Portfolio.objects.filter(date__gte = sDate, date__lte = eDate).order_by('-date')
        r = []
        dates = []
        for i in range(0,len(p)-1):
            r.append((p[i].getPortfolioValue())/(p[i+1].getPortfolioValue()) -1)
            dates.append(p[i+1].date)
        return {'date': dates, 'return': r}


