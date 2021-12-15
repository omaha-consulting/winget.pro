from django.urls import path

from . import views

app_name = 'winget'

urlpatterns = [
    # The sole motivation for having this view is that we want to be able to
    # reverse('winget:index') in instructions for setting up the winget source.
    path('<str:tenant_uuid>', views.index, name='index'),
    path(
        '<str:tenant_uuid>/information', views.information, name='information'
    ),
    path(
        '<str:tenant_uuid>/manifestSearch', views.manifestSearch,
        name='manifestSearch'
    ),
    path(
        '<str:tenant_uuid>/packageManifests/<str:identifier>',
        views.packageManifests, name='packageManifests'
    )
]