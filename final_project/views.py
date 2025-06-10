from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

@require_http_methods(['GET', 'POST'])
def custom_logout(request):
    logout(request)
    return redirect('homepage')