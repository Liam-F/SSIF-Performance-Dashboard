from django.db import models
from django.db.models import Sum

# Contain all Asset Descriptions and properties
class Asset(models.Model):
    assetid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    ticker = models.CharField(max_length=10, unique=True)
    industry = models.CharField(max_length=100)
    country = models.CharField(max_length=50)

    def __str__(self):
        return str(self.assetid)+': '+self.name+' ('+self.ticker+') | Country: '+self.country+' | Industry: '+self.industry

    def calculateHoldingValue(self, ddate):
        # Get a list of all transactional shares previous to this date
        s = list(Transaction.objects.filter(date__lte=ddate, assetid__exact=self.assetid).aggregate(Sum('shares')).values())[0]
        # get the current price as of this date
        p = AssetPrice.objects.filter(date__lte=ddate, assetid__exact=self.assetid).order_by('-date')[0].price

        if not p or not s: # If no price is available
            return 0
        else: # Total Shares * Price
            return s*p

class AssetPrice(models.Model):
    assetid = models.ForeignKey(Asset, unique_for_date='date')
    date = models.DateTimeField()
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return 'Name: '+str(self.assetid.name)+' | Date: '+self.date.strftime('%Y-%m-%d')+' | '+str(self.price)

class Transaction(models.Model):
    transid = models.AutoField(primary_key=True)
    date = models.DateTimeField(unique_for_date='date')
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
    value = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    cash = models.DecimalField(max_digits=10, decimal_places=3, default=100000) #Set default as initial Cash!!

    def calculatePortfolioValue(self, ddate):
        self.value = 0
        for a in Asset.objects.all():
           self.value += a.calculateHoldingValue(ddate)
           # Reconcile Cash
           # Asset Price as of the transaction date OR later if no price data is available
           p = AssetPrice.objects.filter(date__gte=ddate, assetid__exact=a.assetid).order_by('date')[0].price
           for tr in Transaction.objects.filter(date__exact = ddate, assetid__exact = a.assetid):
               self.cash -= tr.shares*p # Subtracted because negative shares = increase in cash and vice versa

           print(ddate.strftime('%Y/%m/%d')+' '+str(self.cash))
        return self.value+self.cash

    def calculatePortfolioTimeSeries(self):
        # Get all consistent Dates across all assets
        dates = []
        for a in Asset.objects.all():
            dates.append(set([d['date'] for d in AssetPrice.objects.filter(assetid__exact=a.assetid).values('date')]))

        dates = sorted(set.intersection(*dates)) # Find intersection and sort

        # Get all Portfolio Value at those dates
        pv = []
        for d in dates:
            pv.append({'date': d, 'value': self.calculatePortfolioValue(d)})

        return pv


