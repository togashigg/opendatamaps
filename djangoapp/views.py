import sys
import json
from django.core.exceptions import BadRequest
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.shortcuts import render
from djangoapp.crawler import opendatadb

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

def localitycodeQuery(request):
        # ?[code=code][&state_name=name][&locality_name=name][&limit=nnn]
        # print("\nstart localitycodeQuery().", file=sys.stderr)
        param = {'code': None, 'state_name': None, 'locality_name': None, 'limit': None}
        db = None
        if 'code' in request.GET:
            param['code'] = request.GET['code']
        if 'state_name' in request.GET:
            param['state_name'] = request.GET['state_name']
        if 'locality_name' in request.GET:
            param['locality_name'] = request.GET['locality_name']
        if 'limit' in request.GET:
            try:
                param['limit'] = int(request.GET['limit'])
            except Exception as e:
                raise BadRequest('Invalid request. Invalid value in "limit" parameter.')
        try:
            db = opendatadb.opendatadb()
            db.connect()
            res = db.query_localitycode(param['code'],
                    param['state_name'], param['locality_name'],
                    limit=param['limit'])
        except Exception as e:
            logger.exception(e)
            db.disconnect()
            db = None
            raise BadRequest('Invalid request. Error in Execution.')
        if db is not None:
            db.disconnect()
            db = None
        response = HttpResponse(json.dumps(res, ensure_ascii=False))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

def facilitySummary(request):
        # print("\nstart facilitySummary().", file=sys.stderr)
        db = None
        try:
            db = opendatadb.opendatadb()
            db.connect()
            recs = db.get_summary()
        except Exception as e:
            if db is not None:
                db.disconnect()
                db = None
            raise BadRequest('Error in Execution.')
        if db is not None:
            db.disconnect()
            db = None
        response = HttpResponse(json.dumps(recs, ensure_ascii=False).replace('], [', '],\n['))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

def facilityQuery(request):
        # ?by=center&lat=nn.nn&lng=nn.nn&distance=nnn[&kind=kind[,kind...]][&limit=nnn]
        # ?by=code&code=code[,code...]][&kind=kind[,kind...]][&limit=nnn]
        # print("\nstart facilityQuery().", file=sys.stderr)
        param = {'kind': None, 'limit': None}
        db = None
        if 'by' not in request.GET:
            raise BadRequest('Invalid request. "by" parameter not specified.')
        param['by'] = request.GET['by']
        if param['by'] not in ['center', 'code']:
            raise BadRequest('Invalid request. Invalid value in "by" parameter.')
        if 'kind' in request.GET:
            param['kind'] = request.GET['kind'].split(',')
        if 'limit' in request.GET:
            try:
                param['limit'] = int(request.GET['limit'])
            except Exception as e:
                raise BadRequest('Invalid request. Invalid value in "limit" parameter.')
        if param['by'] == 'code':
            if 'code' not in request.GET:
                raise BadRequest('Invalid request. "code" parameter is not found.')
            param['code'] = request.GET['code'].split(',')
            try:
                db = opendatadb.opendatadb()
                db.connect()
                recs = db.get_by_localitycode(param['code'], param['kind'],
                        limit=param['limit'])
            except Exception as e:
                db.disconnect()
                db = None
                raise BadRequest('Invalid request. Error in Execution.')
        elif param['by'] == 'center':
            if 'lat' not in request.GET \
            or 'lng' not in request.GET \
            or 'distance' not in request.GET:
                raise BadRequest('Invalid request."lat","lng","distance" parameter is not found.')
            db = None
            try:
                param['lat'] = float(request.GET['lat'])
                param['lng'] = float(request.GET['lng'])
                param['distance'] = int(request.GET['distance'])
                db = opendatadb.opendatadb()
                db.connect()
                recs = db.get_by_distance_from_center(param['lat'], param['lng'],
                        param['distance'], param['kind'], limit=param['limit'])
            except Exception as e:
                db.disconnect()
                db = None
                raise BadRequest('Invalid request.Invalid value in "lat","lng","distance" parameter. Or error in execution.')
        if db is not None:
            db.disconnect()
            db = None
        response = HttpResponse(json.dumps(recs, ensure_ascii=False).replace('], [', '],\n['))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

def facilityKinds(request):
        # ?[code=code[,code]]
        # print("\nstart facilityKinds().", file=sys.stderr)
        param = {'code': None}
        db = None
        if 'code' in request.GET:
            param['code'] = request.GET['code'].split(',')
        try:
            db = opendatadb.opendatadb()
            db.connect()
            res = db.get_opendatamaps_kinds(param['code'])
        except Exception as e:
            db.disconnect()
            db = None
            raise BadRequest('Invalid request. Error in Execution.')
        if db is not None:
            db.disconnect()
            db = None
        response = HttpResponse(json.dumps(res, ensure_ascii=False))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

