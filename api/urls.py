from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path('information', views.information, name='information'),
    path('manifestSearch', views.manifestSearch, name='manifestSearch'),
    path(
        'packageManifests/<str:identifier>', views.packageManifests,
        name='packageManifests'
    )
]