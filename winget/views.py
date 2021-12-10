from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Package
from .util import json_get, json_post


@json_get
def information():
    return {
        'SourceIdentifier':
            'github.com/omaha-consulting/winget-private-repository',
        'ServerSupportedVersions': ['1.1.0']
    }


@json_post
def manifestSearch(data):
    db_query = Q()
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


@json_get
def packageManifests(identifier):
    package = get_object_or_404(Package, identifier=identifier)
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
