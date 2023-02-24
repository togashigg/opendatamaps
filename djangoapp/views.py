import sys
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.shortcuts import render

def error404(request):
        # print("\nstart error404()", file=sys.stderr)
        raise Http404
        return HttpResponseNotFound('<h3>Page not found</h3>')

def opendataIndex(request):
        # print("\nstart opendataIndex()", file=sys.stderr)
        return opendata(request, 'index.html')

def opendata(request, filePath):
        # print("\nstart opendata(), filePath=" + filePath, file=sys.stderr)
        if(filePath==""):
                filePath="index.html"
        contexts = {
                'title' : 'title',
                'ID' : '0',
        }
        return render(request, filePath, contexts)

def opendataID(request, Locality, ID):
        # print("\nstart opendataID(), Locality=" + str(Locality) + ', ID=" + str(ID), file=sys.stderr)
        filePath="index.html"
        contexts = {
                'title' : 'title',
                'Locality' : Locality,
                'ID' : ID,
        }
        return render(request, filePath, contexts)

def opendataJson(request, filePath):
        # print("\nstart opendataJson(), filePath=" + filePath, file=sys.stderr)
        contexts = {
                'title' : 'title',
        }
        f = open('djangoapp/cache/'+filePath, 'r')
        response = HttpResponse(f)
        response['content-type'] = 'application/json; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename=' + filePath
        return response

def opendataCsv(request, filePath):
        # print("\nstart opendataCsv(), filePath=" + filePath, file=sys.stderr)
        contexts = {
                'title' : 'title',
        }
        f = open('djangoapp/cache/'+filePath, 'r')
        response = HttpResponse(f)
        response['content-type'] = 'text/csv; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename=' + filePath
        return response

