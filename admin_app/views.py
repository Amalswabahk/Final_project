from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .models import Facility, Department, Resource
from patient_app.models import Appointment,Patient,HealthcareProvider
from .forms import (
    CustomUserChangeForm, FacilityForm,
    DepartmentForm, ResourceForm, GroupPermissionForm
)

# views.py
from django.shortcuts import render
from django.utils import timezone
from patient_app.models import HealthcareProvider, User, Department, Appointment
from django.db.models import Count

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Get basic stats
    stats = {
        'total_users': User.objects.count(),
        'new_users_today': User.objects.filter(date_joined__date=timezone.now().date()).count(),
        'active_patients': User.objects.filter(is_active=True, groups__name='Patients').count(),
        'patients_with_appointments': Patient.objects.filter(appointment__isnull=False).distinct().count(),
        'doctors': HealthcareProvider.objects.count(),
        'available_providers': HealthcareProvider.objects.count(),
        'today_appointments': Appointment.objects.filter(
            date_time__date=timezone.now().date()
        ).count(),
        'upcoming_appointments': Appointment.objects.filter(
            date_time__gte=timezone.now()
        ).count(),
    }

    # Get recent data
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_providers = HealthcareProvider.objects.select_related('user', 'department')[:5]
    recent_appointments = Appointment.objects.select_related(
        'patient__user', 'Healthcareprovider__user'
    ).order_by('-date_time')[:10]

    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_appointments': recent_appointments,
        'recent_providers': recent_providers,
        'now': timezone.now()
    }

    return render(request, 'admin_module/dashboard.html', context)
def user_management(request):
    """
    Manage all system users
    """
    users = User.objects.all().order_by('-date_joined')

    # Search functionality
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'users': users,
        'query': query,
    }
    return render(request, 'admin_module/user_management.html', context)

def edit_user(request, user_id):
    """
    Edit user details and permissions
    """
    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = CustomUserChangeForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'admin_module/edit_user.html', context)



def group_management(request):
    """
    Manage user groups and permissions
    """
    groups = Group.objects.all()

    if request.method == 'POST':
        form = GroupPermissionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('group_management')
    else:
        form = GroupPermissionForm()

    context = {
        'groups': groups,
        'form': form,
    }
    return render(request, 'admin_module/group_management.html', context)



def edit_group(request, group_id):
    """
    Edit group permissions
    """
    group = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        form = GroupPermissionForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_management')
    else:
        form = GroupPermissionForm(instance=group)

    context = {
        'form': form,
        'group': group,
    }
    return render(request, 'admin_module/edit_group.html', context)



def facility_management(request):
    """
    Manage healthcare facilities
    """
    facilities = Facility.objects.all()

    if request.method == 'POST':
        form = FacilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('facility_management')
    else:
        form = FacilityForm()

    context = {
        'facilities': facilities,
        'form': form,
    }
    return render(request, 'admin_module/facility_management.html', context)



def edit_facility(request, facility_id):
    """
    Edit facility details
    """
    facility = get_object_or_404(Facility, pk=facility_id)

    if request.method == 'POST':
        form = FacilityForm(request.POST, instance=facility)
        if form.is_valid():
            form.save()
            return redirect('facility_management')
    else:
        form = FacilityForm(instance=facility)

    context = {
        'form': form,
        'facility': facility,
    }
    return render(request, 'admin_module/edit_facility.html', context)



def department_management(request, facility_id=None):
    """
    Manage departments within facilities
    """
    departments = Department.objects.select_related('facility', 'head__user')
    facility = None

    if facility_id:
        facility = get_object_or_404(Facility, pk=facility_id)
        departments = departments.filter(facility=facility)

    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('department_management') + f'?facility={facility_id}' if facility_id else '')
    else:
        form = DepartmentForm(initial={'facility': facility} if facility else None)

    context = {
        'departments': departments,
        'facility': facility,
        'form': form,
    }
    return render(request, 'admin_module/department_management.html', context)



def edit_department(request, department_id):
    """
    Edit department details
    """
    department = get_object_or_404(Department, pk=department_id)

    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            return redirect('department_management')
    else:
        form = DepartmentForm(instance=department)

    context = {
        'form': form,
        'department': department,
    }
    return render(request, 'admin_module/edit_department.html', context)



def resource_management(request, department_id=None):
    """
    Manage resources within departments
    """
    resources = Resource.objects.select_related('department__facility')
    department = None

    if department_id:
        department = get_object_or_404(Department, pk=department_id)
        resources = resources.filter(department=department)

    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('resource_management') + f'?department={department_id}' if department_id else '')
    else:
        form = ResourceForm(initial={'department': department} if department else None)

    context = {
        'resources': resources,
        'department': department,
        'form': form,
    }
    return render(request, 'admin_module/resource_management.html', context)



def edit_resource(request, resource_id):
    """
    Edit resource details
    """
    resource = get_object_or_404(Resource, pk=resource_id)

    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            return redirect('resource_management')
    else:
        form = ResourceForm(instance=resource)

    context = {
        'form': form,
        'resource': resource,
    }
    return render(request, 'admin_module/edit_resource.html', context)



def admin_appointment_management(request):
    """
    Comprehensive appointment management for admins
    """
    appointments = Appointment.objects.select_related(
        'patient__user', 'Heaithcareprovider__user', 'Healthcareprovider__department__facility'
    ).order_by('-date_time')

    # Filtering options
    facility_filter = request.GET.get('facility')
    department_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')

    if facility_filter:
        appointments = appointments.filter(
            HealthcareProvider__department__facility_id=facility_filter
        )

    if department_filter:
        appointments = appointments.filter(
            Heaithcareprovider__department_id=department_filter
        )

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if date_filter:
        appointments = appointments.filter(date_time__date=date_filter)

    facilities = Facility.objects.all()
    departments = Department.objects.all()

    context = {
        'appointments': appointments,
        'facilities': facilities,
        'departments': departments,
        'status_choices': Appointment.status,
        'current_filters': {
            'facility': facility_filter,
            'department': department_filter,
            'status': status_filter,
            'date': date_filter,
        }
    }
    return render(request, 'admin_module/appointment_management.html', context)




def edit_appointment(request, appointment_id):


    appointment = get_object_or_404(
        Appointment.objects.select_related('patient__user', 'Healthcareprovider__user'),
        pk=appointment_id
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Validate status - use get_status_choices() or STATUS_CHOICES directly
        if new_status in [choice[0] for choice in Appointment.status]:
            appointment.status = new_status
            appointment.save()
            messages.success(request, 'Appointment status updated successfully.')
            return redirect('admin_appointment_management')
        else:
            messages.error(request, 'Invalid status selected.')

    # Get status choices for the template
    context = {
        'appointment': appointment,
        'status_choices': Appointment.status,
        'current_status': appointment.status,
    }
    return render(request, 'admin_module/edit_appointment.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import HealthcareProviderUserForm, HealthcareProviderForm
from patient_app.models import HealthcareProvider


def is_admin(user):
    return user.is_staff


@login_required
@user_passes_test(is_admin)
def register_healthcare_provider(request):
    if request.method == 'POST':
        user_form = HealthcareProviderUserForm(request.POST)
        provider_form = HealthcareProviderForm(request.POST)

        if user_form.is_valid() and provider_form.is_valid():
            user = user_form.save()

            provider = provider_form.save(commit=False)
            provider.user = user
            provider.save()

            messages.success(request, 'Healthcare provider registered successfully!')
            return redirect('provider-list')
    else:
        user_form = HealthcareProviderUserForm()
        provider_form = HealthcareProviderForm()

    return render(request, 'admin_module/register_healthcare_provider.html', {
        'user_form': user_form,
        'provider_form': provider_form
    })


# healthcare/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import ListView
from patient_app.models import HealthcareProvider, Department
from .forms import HealthcareProviderForm


def is_admin(user):
    return user.is_authenticated and user.is_staff





def healthcare_provider_list(request):
    providers = HealthcareProvider.objects.select_related('user', 'department').all()
    return render(request, 'admin_module/healthcareprovider/provider_list.html', {'providers': providers})




def healthcare_provider_detail(request, pk):
    provider = get_object_or_404(HealthcareProvider, pk=pk)
    return render(request, 'admin_module/healthcareprovider/provider_detail.html', {'provider': provider})


@login_required
@user_passes_test(is_admin)
def healthcare_provider_create(request):
    if request.method == 'POST':
        form = HealthcareProviderForm(request.POST, request.FILES)
        if form.is_valid():
            provider = form.save()
            messages.success(request, f'Healthcare provider {provider.user.get_full_name()} created successfully!')
            return redirect('healthcare:provider-list')
    else:
        form = HealthcareProviderForm()

    return render(request, 'admin_module/healthcareprovider/provider_create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def healthcare_provider_update(request, pk):
    provider = get_object_or_404(HealthcareProvider, pk=pk)
    if request.method == 'POST':
        form = HealthcareProviderForm(request.POST, request.FILES, instance=provider)
        if form.is_valid():
            provider = form.save()
            messages.success(request, f'Healthcare provider {provider.user.get_full_name()} updated successfully!')
            return redirect('healthcare:provider-list')
    else:
        form = HealthcareProviderForm(instance=provider)

    return render(request, 'admin_module/healthcareprovider/provider_create.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def healthcare_provider_delete(request, pk):
    provider = get_object_or_404(HealthcareProvider, pk=pk)
    if request.method == 'POST':
        provider.delete()
        messages.success(request, 'Healthcare provider deleted successfully!')
        return redirect('healthcare:provider-list')

    return render(request, 'admin_module/healthcareprovider/provider_delete.html', {'provider': provider})





from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt  # Only use this if you're having CSRF issues - better to properly handle CSRF
def toggle_sidebar(request):
    if 'sidebar_collapsed' in request.session:
        request.session['sidebar_collapsed'] = not request.session['sidebar_collapsed']
    else:
        request.session['sidebar_collapsed'] = True
    return JsonResponse({'status': 'ok', 'collapsed': request.session['sidebar_collapsed']})


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def admin_login(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')  # Replace with your admin dashboard URL

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('admin_dashboard')  # Replace with your admin dashboard URL
        else:
            messages.error(request, 'Invalid credentials or not an admin user.')

    return render(request, 'admin_module/login.html')


@login_required
def admin_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('admin_login')

from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    DeleteView
)
from .models import Department

class DepartmentListView(ListView):
    model = Department
    template_name = 'departments/department_list.html'
    context_object_name = 'departments'
    paginate_by = 10

class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'departments/department_detail.html'
    context_object_name = 'department'

class DepartmentCreateView(CreateView):
    model = Department
    template_name = 'departments/department_form.html'
    fields = ['name', 'description', 'icon']
    success_url = reverse_lazy('department-list')

    def form_valid(self, form):
        # You can add any additional logic here before saving
        return super().form_valid(form)

class DepartmentDeleteView(DeleteView):
    model = Department
    template_name = 'departments/department_confirm_delete.html'
    success_url = reverse_lazy('department-list')
    context_object_name = 'department'

