from django.urls import path

from . import views

app_name = 'api'

urlpatterns = [
    path(view, getattr(views, view), name=view)
    for view in views.__all__
]