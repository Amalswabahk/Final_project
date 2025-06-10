from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.views import View
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import (
    Patient, HealthcareProvider, Prescription,
    DrugInteraction, TreatmentPlan
)
from patient_app.models import Appointment, MedicalRecord, Allergy
from .forms import PrescriptionForm, TreatmentPlanForm
from django.core.exceptions import PermissionDenied

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, UpdateView
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, date
from django.contrib import messages
from django.urls import reverse_lazy

from .models import (
    HealthcareProvider, Prescription,
    DrugInteraction, TreatmentPlan,
)
from admin_app.models import  Department
from patient_app.models import Patient, MedicalRecord, Allergy, Appointment
from .forms import (
    HealthcareProviderProfileForm, AppointmentStatusForm,
    PrescriptionForm, TreatmentPlanForm
)


class DoctorAuthMixin(LoginRequiredMixin):
    """Mixin to verify doctor authentication and permissions"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        # Use lowercase 'healthcareprovider' consistently everywhere
        if not hasattr(request.user, 'healthcareprovider'):
            messages.error(request, "Only healthcare providers can access this portal")
            return redirect('home')

        return super().dispatch(request, *args, **kwargs)


class DoctorLoginView(View):
    """Custom login view for doctors"""
    template_name = 'doctor_module/login.html'

    def get(self, request):
        # Use lowercase consistently
        if request.user.is_authenticated and hasattr(request.user, 'healthcareprovider'):
            return redirect('doctor_dashboard')
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            # Use lowercase consistently
            if user and hasattr(user, 'healthcareprovider'):
                login(request, user)
                next_url = request.GET.get('next', 'doctor_dashboard')
                return redirect(next_url)

        return render(request, self.template_name, {
            'form': form,
            'error': 'Invalid credentials or not a doctor account'
        })


from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from patient_app.models import Appointment
from .forms import HealthcareProviderProfileForm

@login_required
def doctor_dashboard(request):
    """Function-based view for doctor dashboard"""
    try:
        if not hasattr(request.user, 'healthcareprovider'):
            messages.error(request, "Doctor profile not found")
            return redirect('home')

        doctor = request.user.healthcareprovider
        today = timezone.now().date()

        # Helper functions could be defined here if needed
        def get_todays_appointments():
            return Appointment.objects.filter(
                Healthcareprovider=doctor,
                date_time__date=today
            ).order_by('date_time')

        def get_upcoming_appointments():
            return Appointment.objects.filter(
                Healthcareprovider=doctor,
                date_time__date__gt=today
            ).order_by('date_time')[:5]

        def get_patient_count():
            return Appointment.objects.filter(
                Healthcareprovider=doctor
            ).values('patient').distinct().count()

        context = {
            'doctor': doctor,
            'todays_appointments': get_todays_appointments(),
            'upcoming_appointments': get_upcoming_appointments(),
            'patient_count': get_patient_count(),
        }
        return render(request, 'doctor_module/dashboard.html', context)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home')

@login_required
def doctor_profile(request):
    """Function-based view for doctor profile"""
    if not hasattr(request.user, 'healthcareprovider'):
        messages.error(request, "Doctor profile not found")
        return redirect('home')

    doctor = request.user.healthcareprovider

    if request.method == 'POST':
        form = HealthcareProviderProfileForm(
            request.POST,
            request.FILES,
            instance=doctor
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('doctor_profile')
    else:
        form = HealthcareProviderProfileForm(instance=doctor)

    return render(request, 'doctor_module/profile.html', {
        'form': form,
        'doctor': doctor
    })




class DoctorAppointmentsView(DoctorAuthMixin, View):
    """View and filter doctor's appointments"""
    template_name = 'doctor_module/appointments.html'

    def get(self, request):
        doctor = request.user.healthcareprovider
        appointments = self.get_filtered_appointments(request, doctor)

        context = {
            'appointments': appointments,
            'status_choices': Appointment.status,
            'current_filters': {
                'status': request.GET.get('status'),
                'date': request.GET.get('date'),
            }
        }
        return render(request, self.template_name, context)

    def get_filtered_appointments(self, request, doctor):
        appointments = Appointment.objects.filter(
            Healthcareprovider=doctor
        ).select_related('patient__user').order_by('-date_time')

        if status_filter := request.GET.get('status'):
            appointments = appointments.filter(status=status_filter)

        if date_filter := request.GET.get('date'):
            appointments = appointments.filter(date_time__date=date_filter)

        return appointments


class AppointmentUpdateView(DoctorAuthMixin, UpdateView):
    """Update appointment status"""
    model = Appointment
    form_class = AppointmentStatusForm
    template_name = 'doctor_module/appointment_update.html'
    success_url = reverse_lazy('doctor_appointments')

    def get_queryset(self):
        return Appointment.objects.filter(
            Healthcareprovider=self.request.user.Healthcareprovider
        )

    def form_valid(self, form):
        messages.success(self.request, 'Appointment updated successfully!')
        return super().form_valid(form)


class DoctorPatientListView(DoctorAuthMixin, View):
    """List of patients who have appointments with the doctor"""
    template_name = 'doctor_module/patient_list.html'

    def get(self, request):
        doctor = request.user.healthcareprovider
        patients = self.get_patient_list(doctor)

        return render(request, self.template_name, {
            'patients': patients,
            'search_query': request.GET.get('search', '')
        })

    def get_patient_list(self, doctor):
        # Get distinct patients who have appointments with this doctor
        patient_ids = Appointment.objects.filter(
            Healthcareprovider=doctor
        ).values_list('patient', flat=True).distinct()

        patients = Patient.objects.filter(
            id__in=patient_ids
        ).select_related('user')

        if search_query := self.request.GET.get('search'):
            patients = patients.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__email__icontains=search_query))

        return patients


class PatientDetailView(DoctorAuthMixin, View):
    """Detailed view of a patient's medical information"""
    template_name = 'doctor_module/patient_detail.html'

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        doctor = request.user.healthcareprovider



        context = {
            'patient': patient,
            'medical_records': MedicalRecord.objects.filter(patient=patient),
            'allergies': Allergy.objects.filter(patient=patient),
            'prescriptions': Prescription.objects.filter(
                patient=patient,
                is_active=True
            ),
            'upcoming_appointments': Appointment.objects.filter(
                patient=patient,
                Healthcareprovider=doctor,
                date_time__gte=timezone.now()
            ).order_by('date_time'),
        }
        return render(request, self.template_name, context)


# (Include the PrescriptionCreateView, TreatmentPlanCreateView,
# TreatmentPlanDetailView, and API views from your original code)

@login_required
def check_interactions(request):
    """API endpoint for checking drug interactions"""
    if not hasattr(request.user, 'healthcareprovider'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    medications = request.GET.get('medications', '').split(',')
    interactions = check_drug_interactions(medications)

    return JsonResponse({
        'interactions': [
            {
                'drug1': i.drug1,
                'drug2': i.drug2,
                'severity': i.severity,
                'description': i.description
            } for i in interactions
        ]
    })


def check_drug_interactions(medications):
    """Helper function to check for drug interactions"""
    interactions = []
    if len(medications) >= 2:
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                drug1 = medications[i]
                drug2 = medications[j]

                interaction = DrugInteraction.objects.filter(
                    (Q(drug1__iexact=drug1) & Q(drug2__iexact=drug2)) |
                    (Q(drug1__iexact=drug2) & Q(drug2__iexact=drug1))
                ).first()

                if interaction:
                    interactions.append(interaction)
    return interactions


class PrescriptionCreateView(DoctorAuthMixin, View):
    """Create new prescription with drug interaction checking"""
    template_name = 'doctor_module/create_prescription.html'

    def get(self, request):
        form = PrescriptionForm(
            doctor=request.user.healthcareprovider,
            initial=self.get_initial_data(request)
        )
        return render(request, self.template_name, self.get_context(form))

    def post(self, request):
        form = PrescriptionForm(
            request.POST,
            doctor=request.user.healthcareprovider
        )

        if form.is_valid():
            return self.process_valid_form(request, form)

        return render(request, self.template_name, self.get_context(form))

    def get_initial_data(self, request):
        initial = {}
        if patient_id := request.GET.get('patient'):
            try:
                initial['patient'] = Patient.objects.get(id=patient_id, is_active=True)
            except Patient.DoesNotExist:
                messages.error(request, "Patient not found or inactive")
        return initial

    def get_context(self, form):
        return {
            'form': form,
            'doctor': self.request.user.healthcareprovider,
            'interactions': self.request.session.get('prescription_interactions', [])
        }

    def process_valid_form(self, request, form):
        prescription = form.save(commit=False)
        prescription.doctor = request.user.healthcareprovider

        # Rest of your method remains the same...
        medications = [prescription.medication]
        existing_meds = Prescription.objects.filter(
            patient=prescription.patient,
            is_active=True
        ).values_list('medication', flat=True)

        medications.extend(existing_meds)
        interactions = check_drug_interactions(medications)

        if interactions:
            request.session['prescription_data'] = {
                'patient': prescription.patient.id,
                'medication': prescription.medication.id,
                'dosage': prescription.dosage,
                'frequency': prescription.frequency,
                'instructions': prescription.instructions,
                'duration': prescription.duration,
                'interactions': [
                    {
                        'drug1': i.drug1,
                        'drug2': i.drug2,
                        'severity': i.severity,
                        'description': i.description
                    } for i in interactions
                ]
            }
            return redirect('confirm_prescription')

        prescription.save()
        messages.success(request, 'Prescription created successfully!')
        return redirect('patient_detail', patient_id=prescription.patient.id)



class PrescriptionConfirmationView(DoctorAuthMixin, View):
    """Confirm prescription with potential interactions"""
    template_name = 'doctor_module/prescription_confirmation.html'

    def get(self, request):
        if 'prescription_data' not in request.session:
            return redirect('create_prescription')

        data = request.session['prescription_data']
        patient = get_object_or_404(Patient, pk=data['patient'])

        return render(request, self.template_name, {
            'patient': patient,
            'prescription_data': data,
            'interactions': data.get('interactions', [])
        })

    def post(self, request):
        if 'prescription_data' not in request.session:
            return redirect('create_prescription')

        data = request.session['prescription_data']
        patient = get_object_or_404(Patient, pk=data['patient'])

        # Create the prescription
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=request.user.healthcareprovider,
            medication=data['medication'],
            dosage=data['dosage'],
            frequency=data['frequency'],
            instructions=data['instructions'],
            duration=data['duration']
        )

        # Clear session data
        del request.session['prescription_data']

        messages.success(request,
                         f"Prescription created despite {len(data.get('interactions', []))} potential interactions")
        return redirect('patient_detail', patient_id=patient.id)




    def get_initial_data(self, request):
        if patient_id := request.GET.get('patient'):
            return {'patient': patient_id}
        return {}

    def get_context(self, form):
        patient_id = self.request.GET.get('patient') or form.initial.get('patient')
        active_meds = []

        if patient_id:
            active_meds = Prescription.objects.filter(
                patient_id=patient_id,
                is_active=True
            )

        return {
            'form': form,
            'doctor': self.request.user.healthcareprovider,
            'active_medications': active_meds
        }


class TreatmentPlanDetailView(DoctorAuthMixin, View):
    """View details of a specific treatment plan"""
    template_name = 'doctor_module/treatment_plan_detail.html'

    def get(self, request, plan_id):
        treatment_plan = self.get_treatment_plan(plan_id)
        self.verify_access(request.user.healthcareprovider, treatment_plan)

        return render(request, self.template_name, {
            'plan': treatment_plan,
            'patient': treatment_plan.patient,
            'medications': treatment_plan.medications.all(),
            'can_edit': treatment_plan.doctor == request.user.healthcareprovider
        })

    def get_treatment_plan(self, plan_id):
        return get_object_or_404(
            TreatmentPlan.objects.select_related('patient__user', 'doctor__user'),
            pk=plan_id
        )

    def verify_access(self, doctor, treatment_plan):
        if (treatment_plan.doctor != doctor and
                not Appointment.objects.filter(
                    Healthcareprovider=doctor,
                    patient=treatment_plan.patient
                ).exists()):
            raise PermissionDenied("You don't have access to this treatment plan")



@login_required
def check_interactions(request):
    """API endpoint for checking drug interactions"""
    if not hasattr(request.user, 'healthcareprovider'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    medications = request.GET.get('medications', '')
    medication_list = [m.strip() for m in medications.split(',') if m.strip()]

    interactions = check_drug_interactions(medication_list)

    return JsonResponse({
        'interactions': [
            {
                'drug1': i.drug1,
                'drug2': i.drug2,
                'severity': i.severity,
                'description': i.description
            } for i in interactions
        ]
    })

@login_required
def patient_medications_api(request, patient_id):
    """API endpoint to get a patient's current medications"""
    if not hasattr(request.user, 'healthcareprovider'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    patient = get_object_or_404(Patient, pk=patient_id)

    # Verify the doctor has access to this patient
    if not Appointment.objects.filter(
        Healthcareprovider=request.user.Healthcareprovider,
        patient=patient
    ).exists():
        return JsonResponse({'error': 'Not authorized to access this patient'}, status=403)

    prescriptions = Prescription.objects.filter(
        patient=patient,
        is_active=True
    ).order_by('-date_prescribed')

    return JsonResponse({
        'medications': [
            {
                'id': p.id,
                'name': p.medication,
                'dosage': p.dosage,
                'frequency': p.frequency,
                'instructions': p.instructions,
                'prescribed_date': p.date_prescribed.strftime('%Y-%m-%d'),
                'prescribed_by': f"Dr. {p.doctor.user.get_full_name()}"
            }
            for p in prescriptions
        ]
    })

def check_drug_interactions(medications):
    """Helper function to check for drug interactions"""
    interactions = []
    if len(medications) >= 2:
        for i in range(len(medications)):
            for j in range(i + 1, len(medications)):
                drug1 = medications[i]
                drug2 = medications[j]

                interaction = DrugInteraction.objects.filter(
                    (Q(drug1__iexact=drug1) & Q(drug2__iexact=drug2)) |
                    (Q(drug1__iexact=drug2) & Q(drug2__iexact=drug1))
                ).first()

                if interaction:
                    interactions.append(interaction)
    return interactions


# views.py
class PatientSearchView(DoctorAuthMixin, View):
    template_name = 'doctor_module/patient_search.html'

    def get(self, request):
        query = request.GET.get('q', '')
        patients = Patient.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
        return render(request, self.template_name, {'patients': patients, 'query': query})


from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class DoctorScheduleView(LoginRequiredMixin, TemplateView):
    template_name = 'doctor_module/schedule.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any context data you need
        return context

from django.http import Http404
def patient_detail(request, patient_id):
    try:
        patient = Patient.objects.get(id=patient_id)
        appointments = Appointment.objects.filter(
            patient=patient,
            healthcareprovider=request.user.healthcareprovider
        ).order_by('-date_time')

        return render(request, 'doctor_module/patient_detail.html', {
            'patient': patient,
            'appointments': appointments
        })

    except Patient.DoesNotExist:
        raise Http404("Patient not found")


from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Prescription


class PrescriptionListView(LoginRequiredMixin, ListView):
    model = Prescription
    template_name = 'prescriptions/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 10

    def get_queryset(self):
        # For doctors: show prescriptions they've written
        if hasattr(self.request.user, 'healthcareprovider'):
            return Prescription.objects.filter(
                doctor=self.request.user.healthcareprovider
            ).order_by('-date_prescribed')

        # For patients: show their prescriptions
        elif hasattr(self.request.user, 'patient'):
            return Prescription.objects.filter(
                patient=self.request.user.patient
            ).order_by('-date_prescribed')

        # Admin/staff see all prescriptions
        return Prescription.objects.all().order_by('-date_prescribed')


class PrescriptionDetailView(LoginRequiredMixin, DetailView):
    model = Prescription
    template_name = 'prescriptions/prescription_detail.html'
    context_object_name = 'prescription'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context if needed
        return context


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from .models import TreatmentPlan


class TreatmentPlanListView(LoginRequiredMixin, ListView):
    model = TreatmentPlan
    template_name = 'treatment_plans/treatmentplan_list.html'
    context_object_name = 'treatment_plans'

    def get_queryset(self):
        # For doctors: show only their treatment plans
        # For patients: show only their treatment plans
        # Admins see all
        if self.request.user.is_superuser:
            return TreatmentPlan.objects.all()
        elif hasattr(self.request.user, 'healthcareprovider'):
            return TreatmentPlan.objects.filter(doctor=self.request.user.healthcareprovider)
        elif hasattr(self.request.user, 'patient'):
            return TreatmentPlan.objects.filter(patient=self.request.user.patient)
        return TreatmentPlan.objects.none()


class TreatmentPlanCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = TreatmentPlan
    template_name = 'treatment_plans/treatmentplan_form.html'
    fields = ['patient', 'diagnosis', 'treatment_goals', 'procedures', 'medications', 'follow_up', 'notes']
    success_message = "Treatment plan was created successfully"

    def form_valid(self, form):
        # Automatically set the doctor to the current healthcare provider
        if hasattr(self.request.user, 'healthcareprovider'):
            form.instance.doctor = self.request.user.healthcareprovider
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('treatmentplan-list')


class TreatmentPlanUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TreatmentPlan
    template_name = 'treatment_plans/treatmentplan_form.html'
    fields = ['patient', 'diagnosis', 'treatment_goals', 'procedures', 'medications', 'follow_up', 'notes']
    success_message = "Treatment plan was updated successfully"

    def get_success_url(self):
        return reverse_lazy('treatmentplan-list')


class TreatmentPlanDeleteView(LoginRequiredMixin, DeleteView):
    model = TreatmentPlan
    template_name = 'treatment_plans/treatmentplan_confirm_delete.html'
    success_url = reverse_lazy('treatmentplan-list')

    def get_queryset(self):
        # Only allow deletion by the creator doctor or admin
        if self.request.user.is_superuser:
            return TreatmentPlan.objects.all()
        elif hasattr(self.request.user, 'healthcareprovider'):
            return TreatmentPlan.objects.filter(doctor=self.request.user.healthcareprovider)
        return TreatmentPlan.objects.none()