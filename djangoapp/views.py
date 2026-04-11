import os
import sys
import json
import base64
from django.core.exceptions import BadRequest
from django.http import HttpResponse, Http404
from django.template import loader, RequestContext
from django.shortcuts import render
from src import api
import logging

APP_TITLE = 'OpendataMaps'
logger = logging.getLogger(__name__)

def error404(request):
        logger.debug('error404() start.')
        raise Http404
        return HttpResponseNotFound('<h3>Page not found</h3>')

def opendataIndex(request):
        logger.debug('opendataIndex() start.')
        return opendata(request, 'index.html')

def opendata(request, filePath):
        logger.debug('opendata() start, filePath='+filePath)
        if(filePath==""):
                filePath="index.html"
        contexts = {
                'APP_TITLE' : 'APP_TITLE',
                'GOOGLE_MAPS_API_KEY': base64.b64encode(bytes(os.getenv('GOOGLE_MAPS_API_KEY'), 'ascii')).decode(),
        }
        return render(request, filePath, contexts)

def opendataJson(request, filePath):
        logger.debug('opendataJson() start, filePath='+filePath)
        f = open('djangoapp/cache/'+filePath, 'r')
        response = HttpResponse(f)
        response['content-type'] = 'application/json; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename=' + filePath
        return response

def opendataCsv(request, filePath):
        logger.debug('opendataCsv() start, filePath='+filePath)
        f = open('djangoapp/cache/'+filePath, 'r')
        response = HttpResponse(f)
        response['content-type'] = 'text/csv; charset=utf-8'
        response['Content-Disposition'] = 'attachment; filename=' + filePath
        return response

def localitycodeQuery(request):
        # ?[code=code][&state_name=name][&locality_name=name][&limit=nnn]
        logger.debug('localitycodeQuery() start.')
        param = {'code': None, 'state_name': None, 'locality_name': None, 'limit': None}
        apiobj = None
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
                logger.exception(e)
                raise BadRequest('Invalid request. Invalid value in "limit" parameter.')
        try:
            apiobj = api.OpendataMapsApi(logname='djangoapp')
            res = apiobj.query_localitycode(param['code'],
                    param['state_name'], param['locality_name'],
                    limit=param['limit'])
            apiobj = None
        except Exception as e:
            logger.exception(e)
            apiobj = None
            raise BadRequest('Invalid request. Error in Execution.')
        response = HttpResponse(json.dumps(res, \
                ensure_ascii=False).replace('}, {', '},\n{'))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

def facilitySummary(request):
        logger.debug('facilitySummary() start.')
        apiobj = None
        try:
            apiobj = api.OpendataMapsApi(logname='djangoapp')
            recs = apiobj.get_summary()
            apiobj = None
        except Exception as e:
            logger.exception(e)
            apiobj = None
            raise BadRequest('Error in Execution.')
        response = HttpResponse(json.dumps(recs, \
                ensure_ascii=False).replace(']}, {', ']},\n{'))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

def facilityQueryByCenter(request):
        # ?lat=nn.nn&lng=nn.nn&distance=nnn[&kind=kind[,kind...]][&limit=nnn]
        logger.debug('facilityQueryByCenter() start.')
        param = {'kind': None, 'limit': None}
        apiobj = None
        if 'kind' in request.GET:
            param['kind'] = request.GET['kind'].split(',')
        if 'limit' in request.GET:
            try:
                param['limit'] = int(request.GET['limit'])
            except Exception as e:
                logger.exception(e)
                raise BadRequest('Invalid request. Invalid value in "limit" parameter.')
        if 'lat' not in request.GET \
        or 'lng' not in request.GET \
        or 'distance' not in request.GET:
            raise BadRequest('Invalid request."lat","lng","distance" parameter is not found.')
        try:
            param['lat'] = float(request.GET['lat'])
            param['lng'] = float(request.GET['lng'])
            param['distance'] = int(request.GET['distance'])
            apiobj = api.OpendataMapsApi(logname='djangoapp')
            recs = apiobj.get_by_distance_from_center(param['lat'], param['lng'],
                    param['distance'], param['kind'], limit=param['limit'])
            apiobj = None
        except Exception as e:
            logger.exception(e)
            apiobj = None
            raise BadRequest('Invalid request: Invalid value in '
						'"lat","lng","distance" parameter. Or error in execution.')
        response = HttpResponse(json.dumps(recs, ensure_ascii=False).replace( \
                    '}, {"locality_code":', '},\n{"locality_code":'))
        response['content-type'] = 'application/json; charset=utf-8'
        logger.debug('facilityQueryByCenter() ended.')
        return response

def facilityQueryByLocality(request):
        # ?code=code[,code...]][&kind=kind[,kind...]][&limit=nnn]
        logger.debug('facilityQueryByLocality() start.')
        param = {'kind': None, 'limit': None}
        apiobj = None
        if 'code' not in request.GET:
            raise BadRequest('Invalid request. "code" parameter is not found.')
        param['code'] = request.GET['code'].split(',')
        if 'kind' in request.GET:
            param['kind'] = request.GET['kind'].split(',')
        if 'limit' in request.GET:
            try:
                param['limit'] = int(request.GET['limit'])
            except Exception as e:
                logger.exception(e)
                raise BadRequest('Invalid request. Invalid value in "limit" parameter.')
        try:
            apiobj = api.OpendataMapsApi(logname='djangoapp')
            recs = apiobj.get_by_localitycode(param['code'], param['kind'],
                    limit=param['limit'])
            apiobj = None
        except Exception as e:
            logger.exception(e)
            apiobj = None
            raise BadRequest('Invalid request: Error in Execution.')
        response = HttpResponse(json.dumps(recs, ensure_ascii=False).replace( \
                    '}, {"locality_code":', '},\n{"locality_code":'))
        response['content-type'] = 'application/json; charset=utf-8'
        logger.debug('facilityQueryByLocality() ended.')
        return response

def facilityKinds(request):
        # ?[code=code[,code]]
        logger.debug('facilityKinds() start.')
        param = {'code': None}
        apiobj = None
        if 'code' in request.GET:
            param['code'] = request.GET['code'].split(',')
        try:
            apiobj = api.OpendataMapsApi(logname='djangoapp')
            res = apiobj.get_opendatamaps_kinds(param['code'])
            apiobj = None
        except Exception as e:
            logger.exception(e)
            apiobj = None
            raise BadRequest('Invalid request. Error in Execution.')
        response = HttpResponse(json.dumps(res, ensure_ascii=False))
        response['content-type'] = 'application/json; charset=utf-8'
        return response

