from django.urls import re_path, include, path

from . import views
from .api.urls import router as api_router

app_name = 'winget'

_tenant_uuid = '(?P<tenant_uuid>[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-' \
               '[a-f0-9]{4}-[a-f0-9]{12})'

urlpatterns = [
    # The sole motivation for having this view is that we want to be able to
    # reverse('winget:index') in instructions for setting up the winget source.
    re_path(f'^{_tenant_uuid}$', views.index, name='index'),
    re_path(
        f'^{_tenant_uuid}/information$', views.information, name='information'
    ),
    re_path(
        f'^{_tenant_uuid}/manifestSearch$', views.manifestSearch,
        name='manifestSearch'
    ),
    re_path(
        f'^{_tenant_uuid}/packageManifests/(?P<identifier>.*)$',
        views.packageManifests, name='packageManifests'
    ),
    path('api/v1/', include(api_router.urls))
]