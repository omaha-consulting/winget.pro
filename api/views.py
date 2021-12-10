from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

import json

__all__ = ['information', 'manifestSearch']

@require_GET
def information(request):
    return JsonResponse({
        'Data': {
            'SourceIdentifier':
                'github.com/omaha-consulting/winget-private-repository',
            'ServerSupportedVersions': ['1.1.0']
        }
    })

@csrf_exempt
@require_POST
def manifestSearch(request):
    data = json.loads(request.body)
    if data.get('FetchAllManifests'):
        return JsonResponse({'Data': []})
    return JsonResponse({})