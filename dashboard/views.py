from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from data.models import *

def index(request):
    # Template and output
    template = loader.get_template('dashboard/index.html')
    context = RequestContext(request)

    return HttpResponse(template.render(context))