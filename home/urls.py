from django.urls import path
from home.views import homepage,portal_redirect

urlpatterns = [
    path('', homepage, name='homepage'),
    path('portal/',portal_redirect, name='portal_redirect'),

]