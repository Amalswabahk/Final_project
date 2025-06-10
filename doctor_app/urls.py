from django.urls import path
from . import views
from .views import PatientSearchView,PrescriptionListView,PrescriptionDetailView,TreatmentPlanListView,TreatmentPlanDeleteView

urlpatterns = [
    # Doctor authentication
    path('login/', views.DoctorLoginView.as_view(), name='doctor_login'),

    # Doctor dashboard and profile
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/profile/', views.doctor_profile, name='doctor_profile'),

    # Appointments
    path('appointments/', views.DoctorAppointmentsView.as_view(), name='doctor_appointments'),
    path('appointments/<int:pk>/update/', views.AppointmentUpdateView.as_view(), name='update_appointment'),

    # Patients
    path('patients/', views.DoctorPatientListView.as_view(), name='doctor_patients'),
    path('patients/<int:patient_id>/', views.PatientDetailView.as_view(), name='patient_detail'),
    path('patients/search/', PatientSearchView.as_view(), name='patient_search'),

    # Prescriptions
    path('prescriptions/create/', views.PrescriptionCreateView.as_view(), name='create_prescription'),
    path('prescriptions/', PrescriptionListView.as_view(), name='prescription_list'),
    path('prescriptions/<int:pk>/', PrescriptionDetailView.as_view(), name='prescription_detail'),

    # Treatment Plans
    path('treatment-plans/', TreatmentPlanListView.as_view(), name='treatment_plan-list'),
    path('treatment-plans/create/', views.TreatmentPlanCreateView.as_view(), name='create_treatment_plan'),
    path('treatment-plans/<int:plan_id>/', views.TreatmentPlanDetailView.as_view(), name='treatment_plan_detail'),
    path('treatment-plans/<int:pk>/delete/', TreatmentPlanDeleteView.as_view(), name='treatment_plan-delete'),

    # API endpoints
    path('api/check-interactions/', views.check_interactions, name='check_interactions'),
    path('api/patient-medications/<int:patient_id>/', views.patient_medications_api, name='patient_medications_api'),

    path('doctor-schedule/', views.DoctorScheduleView.as_view(), name='doctor_schedule'),
]