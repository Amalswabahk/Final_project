from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import HospitalProfile



def homepage(request):
    try:
        hospital = HospitalProfile.objects.get()
    except HospitalProfile.DoesNotExist:
        hospital = None

    context = {
        'hospital': hospital,
        'user': request.user
    }
    return render(request, 'home/homepage.html', context)


@login_required
def portal_redirect(request):
    if hasattr(request.user, 'healthcareprovider'):
        return redirect('doctor_dashboard')
    elif hasattr(request.user, 'patient'):
        return redirect('patient_dashboard')
    elif request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('homepage')





