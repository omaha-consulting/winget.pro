from django.urls import path

from tenants.views import signup

app_name = 'tenants'

urlpatterns = [
    path('signup/', signup, name='signup')
]
