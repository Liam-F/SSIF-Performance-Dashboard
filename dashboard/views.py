from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import RequestContext, loader
from data.models import *
import datetime as dt
import json
import pandas as pd
import numpy as np
import pdb
from os.path import isfile
from scipy import optimize

#since epoch milliseconds
def unix_time(dte):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = dte - epoch
    return delta.total_seconds() * 1000.0

def index(request):
    if(isfile('portfoliostats.json')):
        with open('portfoliostats.json') as j:
            output = json.load(j)
    else:
        # Calculate Portfolio Statistics
        rf = 0.0 #LOL RATES
        r_p = Portfolio().getReturns()
        r = r_p['return']
        er = np.mean(r)*252*100 # Mean Annualized Return from daily
        sigma = (np.std(r)*np.sqrt(252))*100 # Annualized Standard Deviation
        sharpe = (er-rf)/sigma

        # Benchmark Calculations
        # ASSUMPTION: Benchmark is hardcoded as 65% US SPX, 35% CN TSX
        w = [0.65, 0.35]
        benchmark = Asset.objects.filter(industry__exact = 'Index')
        exr = Asset.objects.filter(name__exact = 'USDCAD')
        # get returns according to available portfolio dates, merge is required to ensure dates are matched
        # COLUMNS ARE: [DATE PORTFOLIO BENCHMARK US BENCHMARK CN USDCAD]
        rmat = pd.merge(pd.DataFrame(benchmark[0].getReturns()), pd.DataFrame(benchmark[1].getReturns()), on='date') # Merge Benchmarks
        rmat = pd.merge(pd.DataFrame(r_p), rmat, on='date') # Merge Portfolio Returns
        rmat = pd.merge(rmat, pd.DataFrame(exr[0].getReturns()), on='date') # Merge Exchange Rates
        rmat = rmat.iloc[:,1:] # Remove Date column
        rmat.iloc[:,1] *= (1+rmat.iloc[:,-1]) # USDCAD
        r_b = np.dot(rmat.iloc[:, [1,2]], w) # Calculate Benchmark
        r = rmat.iloc[:, 0]
        beta = np.cov(r,r_b)[0,1]/np.var(r_b) # Beta
        alpha = (np.mean(r) - np.mean(r_b)*beta)*100*252
        te = np.std(r-r_b)*100*np.sqrt(252)
        ir = (er-rf)/te

        # Holdings List:
        holdings = []
        assetids =[]
        for a in Asset.objects.all():
            assetValNow = a.calculateHoldingValue(ddate = dt.datetime.now())
            if(assetValNow > 0):
                # Get Total Return
                # ASSUMPTION: Completely sold off assets are excluded
                assetValCost = 0.0
                for s in Transaction.objects.filter(assetid__exact = a):
                    cost = s.getCost()
                    if(cost < 0):
                        assetValNow -= cost # it's negative cost so add it to the value now
                    else:
                        assetValCost += cost

                # Get Managers
                m = SectorManager.objects.filter(assetid__exact = a)
                if not m: m = 'None'
                else: m = m[0].name

                # Get Dividend Yield
                divValue = a.aggregateDividends()
                dyield = divValue / assetValNow

                assetids.append(a.assetid) # For Sparklines
                holdings.append({'assetid': a.assetid,
                                 'ticker': a.ticker,
                                 'company': a.name,
                                 'sector': a.industry,
                                 'country': a.country,
                                 'totalreturn': round((assetValNow/assetValCost - 1)*100, 1),
                                 'manager': m,
                                 'yield': round(dyield*100,1)})

        # Template and output
        output = {
            'portfolioStartDate': dt.datetime.strftime(Portfolio.objects.all().order_by('date')[0].date, '%B %d, %Y'),
            'avgRet': round(er, 2),
            'vola': round(sigma, 2),
            'sharpe': round(sharpe,2),
            'alpha': round(alpha, 2),
            'beta': round(beta,2),
            'ir': round(ir,2),
            'holdings': holdings,
            'assetids': assetids
        }

        # Save as JSON
        with open('portfoliostats.json', 'w') as j:
            json.dump(output, j)

    # If its a 'None' type request, we just return our output
    # AKA, its the importer eod view calling...
    if request is None:
        return output
    else:
        template = loader.get_template('dashboard/index.html')
        context = RequestContext(request, output)

        return HttpResponse(template.render(context))

def portfoliojson(request):
    if(isfile('portfolio.json')):
        with open('portfolio.json') as j:
            e = json.load(j)
    else:
        # Template and output
        p = list(Portfolio.objects.all().order_by('date').values('date', 'value', 'cash'))

        e = []
        for i,dp in enumerate(p):
            e.append([ unix_time(dp['date']), round(dp['value']+dp['cash'])])

        # Save as JSON
        with open('portfolio.json', 'w') as j:
            json.dump(e, j)


    return JsonResponse(e, safe=False)

def allocationjson(request):
    if(isfile('allocation.json')):
        with open('allocation.json') as j:
            temp = json.load(j)
    else:
        sectors = {'Information Technology': 0,
                   'Financial': 0,
                   'Energy':0,
                   'Consumer Staples': 0,
                   'Consumer Discretionary': 0,
                   'Healthcare': 0,
                   'Industrials': 0,
                   'Utilities': 0,
                   'Basic Materials': 0,
                   'Telecom': 0}

        p = Portfolio.objects.filter(date__lte = dt.datetime.now()).order_by('-date')[0].value
        for a in Asset.objects.all():
            if a.industry in sectors.keys():
                sectors[a.industry] += a.calculateHoldingValue(ddate = dt.datetime.now())/p

        temp = []
        for s,per in sectors.items():
            temp.append({'name': s, 'y': per})

        # Save as JSON
        with open('allocation.json', 'w') as j:
            json.dump(temp, j)

    return JsonResponse(temp, safe=False)

def frontierjson(request):
    if(isfile('frontier.json')):
        with open('frontier.json') as j:
            r_r = json.load(j)
    else:
        exclusion_list = ['USDCAD=X', '^GSPTSE', '^GSPC', 'XLS'] #Excelis is missing data

        # Markowitz Frontier
        sDate = Portfolio.objects.all().order_by('date')[0].date # Get first date of Portfolio
        r = pd.DataFrame(Asset.objects.all().first().getReturns(sDate = sDate, eDate = dt.datetime.now())) # get the first asset to start it
        for a in Asset.objects.all()[1:]:
            if a.ticker not in exclusion_list:
                r = r.merge(pd.DataFrame(a.getReturns(sDate = sDate, eDate = dt.datetime.now())), on='date')
        r = r.iloc[:, 1:] # Remove date column

        # First calculate Min variance
        #pdb.set_trace()
        n = len(r.columns)
        covar = np.cov(r, rowvar=0)
        er = r.mean(axis=0)
        cons = ({'type': 'eq', 'fun': lambda x: 1-sum(x)},{'type': 'ineq', 'fun': lambda x: x},)
        wstar = optimize.minimize(lambda x, covar: np.sqrt(252)*np.sqrt(np.dot(x,np.dot(covar,x)))*100,
                              x0=np.array([1.0/n]*n),#Initial guess of 1/N
                              args=(covar,), # Pass in arguments
                              method='SLSQP', jac=False, #Jacobian vector
                              constraints=cons, # constraints set as above
                              options=({'maxiter': 1e5}))   #Ensure convergence
        r_r = [{'x': wstar.fun, 'y': np.dot(wstar.x, er)*252*100}]

        # Loop
        eps = 0.35 # margin of increase in risk
        iter = 25 # number of iterations
        vol = wstar.fun
        for i in range(1,iter):
            vol += eps
            cons = ({'type': 'eq', 'fun': lambda x: 1-sum(x)},
                    {'type': 'ineq', 'fun': lambda x: x},
                    {'type': 'eq', 'fun': lambda x,covar: vol - np.sqrt(252)*np.sqrt(np.dot(x,np.dot(covar,x)))*100, 'args': (covar,)})
            wstar = optimize.minimize(lambda x, er: -np.dot(x,er),
                                      x0=np.array([1.0/n]*n),#Initial guess of 1/N
                                      args=(er,), # Pass in arguments
                                      method='SLSQP', jac=False, #Jacobian vector
                                      constraints=cons, # constraints set as above
                                      options=({'maxiter': 1e5}))   #Ensure convergence
            r_r.append({'x': np.sqrt(252*np.dot(wstar.x,np.dot(covar,wstar.x)))*100,
                         'y': -wstar.fun*252*100})

        # Save as JSON
        with open('frontier.json', 'w') as j:
            json.dump(r_r, j)

    return JsonResponse(r_r, safe=False)

def relativefrontjson(request):
    if(isfile('relativefrontier.json')):
        with open('relativefrontier.json') as j:
            r_r = json.load(j)
    else:
        # Calculate Portfolio Statistics
        rf = 0.0 #LOL RATES
        r_p = Portfolio().getReturns()
        sDate = r_p['date'][-1]
        r = r_p['return']
        er = np.mean(r)*252*100 # Mean Annualized Return from daily
        sigma = (np.std(r)*np.sqrt(252))*100 # Annualized Standard Deviation

        # Calculate Benchmark Statistics
        b = Asset.objects.filter(industry__exact = 'Index')
        r_r = [{'x': sigma, 'y': er, 'name': 'SSIF'}]
        r_ba = []
        for bmark in b:
            bp = bmark.getReturns(sDate = sDate, eDate = dt.datetime.now())
            r_b = bp['return']
            r_ba.append(pd.DataFrame(bp))
            er = np.mean(r_b)*252*100 # Mean Annualized Return from daily
            sigma = (np.std(r_b)*np.sqrt(252))*100 # Annualized Standard Deviation
            r_r.append({'x': sigma, 'y': er, 'name': bmark.name})

        # Calculate Combined Benchmark Statistics
        # Assumption: 65% US and 35% CN like in main page, S&P 500 FIRST!
        w = [0.65, 0.35]
        r_ba = pd.DataFrame.merge(r_ba[0], r_ba[1], on='date').iloc[:,1:] # Strip the date
        r_cb = np.dot(r_ba, w)
        er = np.mean(r_cb)*252*100 # Mean Annualized Return from daily
        sigma = (np.std(r_cb)*np.sqrt(252))*100 # Annualized Standard Deviation
        r_r.append({'x': sigma, 'y': er, 'name': 'Combined Benchmark'})

        # Save as JSON
        with open('relativefrontier.json', 'w') as j:
            json.dump(r_r, j)

    return JsonResponse(r_r, safe=False)

def spkperformancejson(request):
    a = request.GET.get('a')
    if a:
        pr = AssetPrice.objects.filter(assetid__exact = a).order_by('-date')
        if not pr:
            return HttpResponse('nah')
        pr = pr[0:5]
        resp = []
        for p in pr:
            resp.append({'x': unix_time(p.date), 'y': p.price})

        return JsonResponse(resp, safe=False)
    else:
        return HttpResponse('nah')
