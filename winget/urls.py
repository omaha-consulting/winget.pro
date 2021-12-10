from django.urls import path

from . import views

app_name = 'winget'

urlpatterns = [
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