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
from os import remove
from scipy import optimize
#from pyfolio.bayesian import run_model, compute_bayes_cone

import time

#since epoch milliseconds
def unix_time(dte):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = dte - epoch
    return delta.total_seconds() * 1000.0

def portfolioindex():
    # Calculate Portfolio Statistics
    rf = 0.0 #LOL RATES
    per = 252
    sDate = Portfolio.objects.all().order_by('date')[0].date # get the starting date of the portfolio
    r_p = Portfolio().getReturns(sDate =sDate, over=1)
    er = np.mean(r_p)*per*100 # Mean Annualized Return from per
    sigma = (np.std(r_p)*np.sqrt(per))*100 # Annualized Standard Deviation
    sharpe = (er-rf)/sigma

    # Benchmark Calculations
    # ASSUMPTION: Benchmark is hardcoded as 65% US SPX, 35% CN TSX
    w = [0.65, 0.35]
    us_b = Asset.objects.filter(country__exact = 'US', industry__exact = 'Index').first().getReturns(sDate = sDate, over =1)
    cn_b = Asset.objects.filter(country__exact = 'CN', industry__exact = 'Index').first().getReturns(sDate = sDate, over =1)

    rmat = np.matrix(pd.concat([r_p, us_b, cn_b], axis=1).dropna(axis=0)) # Ignore dates, Canadian bench is fucked
    r_b = np.dot(rmat[:, 1:], w) # Calculate Benchmark
    r_p = np.squeeze(np.asarray(rmat[:,0]))

    beta = np.cov(r_p,r_b)[0,1]/np.var(r_b) # Beta
    alpha = (np.mean(r_p) - np.mean(r_b)*beta)*100*per
    te = np.std(r_p-r_b)*100*np.sqrt(per)
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
                             'manager': a.managerid.name,
                             'managerid': a.managerid.managerid,
                             'yield': round(dyield*100,1)})

    # Template and output
    output = {
        'portfolioStartDate': dt.datetime.strftime(Portfolio.objects.all().order_by('date')[0].date, '%B %d, %Y'),
        'frontierStartDate': dt.datetime.strftime(dt.datetime.now()-dt.timedelta(days=365), '%B %d, %Y'),
        'today': dt.datetime.strftime(dt.datetime.now(), '%B %d, %Y'),
        'avgRet': round(er, 2),
        'vola': round(sigma, 2),
        'sharpe': round(sharpe,2),
        'alpha': round(alpha, 2),
        'beta': round(beta,2),
        'ir': round(ir,2),
        'holdings': holdings,
        'assetids': assetids
    }
    return output

def index(request):
    if request.GET.get('a') == 'eod':
      if(isfile('portfoliostats.json')):
          remove('portfoliostats.json')

    if(isfile('portfoliostats.json')):
        with open('portfoliostats.json') as j:
            output = json.load(j)
    else:
        output = portfolioindex() # Exterrnal for eodupdate

        # Save as JSON
        with open('portfoliostats.json', 'w') as j:
            json.dump(output, j)

    template = loader.get_template('dashboard/index.html')
    context = RequestContext(request, output)

    return HttpResponse(template.render(context))

def forecastjson(request):
    if request.GET.get('a') == 'eod':
      if(isfile('forecast.json')):
          remove('forecast.json')

    if(isfile('forecast.json')):
        with open('forecast.json') as j:
            e = json.load(j)
    else:

        lookback = dt.timedelta(days = 365)
        now = dt.date.today()
        ret = Portfolio.objects.first().getReturns(sDate=now-lookback)
        t_forecast = pd.date_range(now, periods=22, freq='B')
        trace = run_model('t', ret, pd.Series([0]*len(t_forecast), index=t_forecast), samples=500)

        # Compute bayes cone
        forecast = compute_bayes_cone(trace['returns_missing'])
        pv = Portfolio.objects.order_by('date').last().getPortfolioValue()

        # Format cones
        e = []
        # inner level
        #Prepend initial value of 1 to match date
        forecast.get(5).insert(0,1); forecast.get(25).insert(0,1); forecast.get(75).insert(0,1); forecast.get(95).insert(0,1);
        forecast_mat = pv*pd.DataFrame([forecast.get(25), forecast.get(75)], columns = [unix_time(t) for t in t_forecast]).T

        forecast_mat.reset_index(inplace=True)
        e.append(forecast_mat.values.tolist())

        # outer level
        forecast_mat[0] = np.array(forecast.get(5))*pv
        forecast_mat[1] = np.array(forecast.get(95))*pv
        e.append(forecast_mat.values.tolist())

        # Save as JSON
        with open('forecast.json', 'w') as j:
            json.dump(e, j)

    return JsonResponse(e, safe=False)

def portfoliojson(request):
    if request.GET.get('a') == 'eod':
      if(isfile('portfolio.json')):
          remove('portfolio.json')

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

def benchmarkjson(request):
    if request.GET.get('a') == 'eod':
      if(isfile('benchmark.json')):
          remove('benchmark.json')

    if(isfile('benchmark.json')):
        with open('benchmark.json') as j:
            e = json.load(j)
    else:
        first = Portfolio.objects.all().order_by('date').first()
        sDate = first.date
        s_o = first.value + first.cash
        # Benchmark Calculations
        # ASSUMPTION: Benchmark is hardcoded as 65% US SPX, 35% CN TSX
        w = [0.65, 0.35]
        us_b = Asset.objects.filter(country__exact = 'US', industry__exact = 'Index').first().getReturns(sDate = sDate)
        cn_b = Asset.objects.filter(country__exact = 'CN', industry__exact = 'Index').first().getReturns(sDate = sDate)
        rmat = pd.concat([us_b, cn_b], axis=1).dropna(axis=0)# Concat us and CN first
        r_b =  pd.DataFrame(np.dot(rmat, w), index=rmat.index) # Get Benchmark return first the

        port = pd.DataFrame(Portfolio().getReturns(sDate = sDate)) # Then get portfolio dates/returns
        r_b = port.join(r_b, how='left', lsuffix='p', rsuffix='b') # Do a LEFT join on portfolio date
        r_b = r_b['0b'].fillna(0) # Then fill NaNs with zeros, this ensures equal length
        ts = np.cumprod(r_b+1)*s_o

        e = [[unix_time(i),round(p)] for (i,p) in ts.iteritems()]

        # Save as JSON
        with open('benchmark.json', 'w') as j:
            json.dump(e, j)


    return JsonResponse(e, safe=False)


def allocationjson(request):
    if request.GET.get('a') == 'eod':
      if(isfile('allocation.json')):
          remove('allocation.json')

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
    if request.GET.get('a') == 'eod':
      if(isfile('frontier.json')):
          remove('frontier.json')

    if(isfile('frontier.json')):
        with open('frontier.json') as j:
            r_r = json.load(j)
    else:
        exclusion_list = ['USDCAD=X', '^GSPTSE', '^GSPC', 'XLS'] #Excelis is missing data

        lookback = dt.timedelta(days = 365)
        now = dt.datetime.now()
        sDate = now - lookback
        # Markowitz Frontier
        r = []
        for a in Asset.objects.all()[1:]:
            if a.ticker not in exclusion_list or a.calculateHoldingValue(ddate = now) > 0:
                r.append(pd.DataFrame(a.getReturns(sDate = sDate, eDate = now)))

        r = pd.concat(r, axis=1, join='inner').dropna(axis=0)
        # First calculate Min variance
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

    if request.GET.get('a') == 'eod' and (isfile('relativefrontier.json')):
        remove('relativefrontier.json')

    if(isfile('relativefrontier.json')):
        with open('relativefrontier.json') as j:
            r_r = json.load(j)
    else:
        # Calculate Portfolio Statistics
        rf = 0.0 #LOL RATES
        lookback = dt.timedelta(days = 365)
        now = dt.datetime.now()
        sDate = now - lookback
        r_p = Portfolio().getReturns(sDate = sDate, eDate = dt.datetime.now())
        er = np.mean(r_p)*252*100 # Mean Annualized Return from daily
        sigma = (np.std(r_p)*np.sqrt(252))*100 # Annualized Standard Deviation

        # Calculate Benchmark Statistics
        b = Asset.objects.filter(industry__exact = 'Index')
        r_r = [{'x': sigma, 'y': er, 'name': 'SSIF'}]
        r_ba = []
        for bmark in b:
            bp = bmark.getReturns(sDate = sDate, eDate = dt.datetime.now())
            r_ba.append(pd.DataFrame(bp)) # Used later in combined benchmark
            er = np.mean(bp)*252*100 # Mean Annualized Return from daily
            sigma = (np.std(bp)*np.sqrt(252))*100 # Annualized Standard Deviation
            r_r.append({'x': sigma, 'y': er, 'name': bmark.name})

        # Calculate Combined Benchmark Statistics
        # Assumption: 65% US and 35% CN like in main page, S&P 500 FIRST!
        w = [0.65, 0.35]
        r_ba = pd.DataFrame.merge(r_ba[0], r_ba[1], left_index = True, right_index = True) # Strip the date
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
        pr = pr[0:22:5]
        resp = []
        for p in pr:
            resp.append({'x': unix_time(p.date), 'y': p.price})

        return JsonResponse(resp, safe=False)
    else:
        return HttpResponse('nah')

def managerinfo(request):
    id = request.GET.get('a')
    if id:
        mgr = EquityManager.objects.filter(managerid__exact = id)
        if not mgr:
            return HttpResponse('<h2>Not Found</h2>')
        else:
            template = loader.get_template('dashboard/mgrinfo.html')
            context = RequestContext(request, {'mgr': mgr[0]})

            return HttpResponse(template.render(context))
    else:
        return HttpResponse('<h2>Not Found</h2>')