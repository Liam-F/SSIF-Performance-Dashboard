from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.template import RequestContext, loader
from data.models import *
import datetime as dt
import json
import pandas as pd
import numpy as np
import pdb
#from scipy import optimize

#since epoch milliseconds
def unix_time(dte):
    epoch = dt.datetime.utcfromtimestamp(0)
    delta = dte - epoch
    return delta.total_seconds() * 1000.0

def index(request):
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


    # Template and output
    template = loader.get_template('dashboard/index.html')
    context = RequestContext(request, {
        'portfolioStartDate': dt.datetime.strftime(Portfolio.objects.all().order_by('date')[0].date, '%B %d, %Y'),
        'avgRet': round(er, 2),
        'vola': round(sigma, 2),
        'sharpe': round(sharpe,2),
        'alpha': round(alpha, 2),
        'beta': round(beta,2)
    })

    return HttpResponse(template.render(context))

def portfoliojson(request):
    # Template and output
    p = list(Portfolio.objects.all().order_by('date').values('date', 'value', 'cash'))

    e = []
    for i,dp in enumerate(p):
        e.append([ unix_time(dp['date']), round(dp['value']+dp['cash'])])

    return JsonResponse(e, safe=False)

def allocationjson(request):

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

    return JsonResponse(temp, safe=False)

def frontierjson(request):
    exclusion_list = ['USDCAD=X', '^GSPTSE', '^GSPC', 'XLS'] #Excelis is missing data

    # Markowitz Frontier
    r = pd.DataFrame(Asset.objects.all().first().getReturns()) # get the first asset to start it
    for a in Asset.objects.all()[1:]:
        if a.ticker not in exclusion_list:
            r = r.merge(pd.DataFrame(a.getReturns()), on='date')
    r = r[:, 1:] # Remove date column

    # First calculate Min variance
    n = r.columns
    covar = r.cov()
    er = r.mean(axis=1)
    cons = ({'type': 'eq', 'fun': lambda x: 1-sum(x)},)
   # w = optimize.minimize(lambda x, covar: np.dot(x,np.dot(covar,x)),
   #                       x0=np.array([1.0/n]*n), #Initial guess of 1/N
   #                       args=(covar), # Pass in arguments
   #                       method='SLSQP', jac=False, #Jacobian vector
    #                      constraints=cons, # constraints set as above
    #                      options=({'maxiter': 1e4}))   #Ensure convergence
   # r_r = [np.sqrt(w.fun), np.dot(w.x, er)]

    # Loop
    eps = 0.001 # margin of increase in risk
    n = 50 # number of iterations


    return JsonResponse(r, safe=False)
