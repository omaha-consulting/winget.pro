from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from api.models import Package
from api.util import json_response, json_request

__all__ = ['information', 'manifestSearch']


@require_GET
@json_response
def information(request):
    return {
        'SourceIdentifier':
            'github.com/omaha-consulting/winget-private-repository',
        'ServerSupportedVersions': ['1.1.0']
    }


@csrf_exempt
@require_POST
@json_request
@json_response
def manifestSearch(request):
    if request.get('FetchAllManifests'):
        return []
    keyword = request['Query']['KeyWord']
    return [
        {
            'PackageIdentifier': package.identifier,
            'PackageName': package.name,
            'Publisher': package.publisher,
            'Versions': [
                {'PackageVersion': version.version}
                for version in package.version_set.all()
            ]
        }
        for package in Package.objects.filter(name__icontains=keyword)
    ]
