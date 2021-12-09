from django.http import JsonResponse

def information(request):
    return JsonResponse({
      'Data': {
        'SourceIdentifier': 'github.com/omaha-consulting/winget-private-repository',
        'ServerSupportedVersions': ['1.1.0']
      }
    })