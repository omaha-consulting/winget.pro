from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST

from .models import Package
from .util import load_tenant, return_jsonresponse, parse_jsonrequest


@require_GET
@load_tenant
@return_jsonresponse
def information(*_):
    return {
        'SourceIdentifier':
            'github.com/omaha-consulting/winget-private-repository',
        'ServerSupportedVersions': ['1.1.0']
    }


@require_POST
@load_tenant
@parse_jsonrequest
@return_jsonresponse
def manifestSearch(data, tenant):
    db_query = Q(tenant=tenant)
    if 'Query' in data:
        keyword = data['Query']['KeyWord']
        db_query &= Q(name__icontains=keyword)
    if 'Inclusions' in data:
        for inclusion in data['Inclusions']:
            field = inclusion['PackageMatchField']
            if field == 'PackageName':
                keyword = inclusion['RequestMatch']['KeyWord']
                db_query &= Q(name__icontains=keyword)
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
        for package in Package.objects.filter(db_query)
    ]

@require_GET
@load_tenant
@return_jsonresponse
def packageManifests(_, tenant, identifier):
    package = get_object_or_404(Package, tenant=tenant, identifier=identifier)
    return {
        'PackageIdentifier': package.identifier,
        'Versions': [
            {
                'PackageVersion': version.version,
                'DefaultLocale': {
                    'PackageLocale': 'en-us',
                    'Publisher': package.publisher,
                    'PackageName': package.name,
                    'ShortDescription': package.description
                },
                'Installers': [
                    {
                        'Architecture': installer.architecture,
                        'InstallerType': installer.type,
                        'InstallerUrl': installer.url,
                        'InstallerSha256': installer.sha256
                    }
                    for installer in version.installer_set.all()
                ]
            }
            for version in package.version_set.all()
        ]
    }
