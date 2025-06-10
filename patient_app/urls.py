from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm
from .views import Appointment,AppointmentListView,AppointmentCreateView,AppointmentDeleteView,AppointmentUpdateView,AppointmentDetailView
from patient_app.views import PaymentCreateView,PaymentDetailView,stripe_webhook,PaymentHistoryListView, PaymentHistoryDetailView
from .views import (BillingListView, BillingCreateView, BillingDetailView,
                   BillingUpdateView, BillingStatusUpdateView, PatientBillingListView,PatientDashboardView)



urlpatterns = [
    path("patient-login/", views.login_view, name="patient-login"),
    path('logout/', views.custom_logout, name='logout'),
    path('register/', views.register_patient, name='register_patient'),
    # urls.py (with parameter)

    path('patient-dashboard/', PatientDashboardView.as_view(), name='patient-dashboard'),



    path("appointments/", AppointmentListView.as_view(), name="appointment_list"),
    path("appointments/create/", AppointmentCreateView.as_view(), name="create_appointment"),
    path("appointments/update/<int:pk>/", AppointmentUpdateView.as_view(), name="appointment_update"),
    path("appointments/delete/<int:pk>/", AppointmentDeleteView.as_view(), name="appointment_delete"),
    path("appointments/detail/<int:pk>/", AppointmentDetailView.as_view(), name="appointment_detail"),
    path('medical-records/', views.medical_records, name='medical_records'),

    path('health-education/', views.health_education, name='health_education'),
    path('health-education/<int:article_id>/', views.view_article, name='view_article'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             form_class=CustomPasswordResetForm,
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ),
         name='password_reset'),
    path('billing/<int:billing_id>/pay/', PaymentCreateView.as_view(), name='create_payment'),
    path('payment/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    path('stripe-webhook/', stripe_webhook, name='stripe_webhook'),
    path('payment-history/', PaymentHistoryListView.as_view(), name='payment_history'),
    path('payment-history/<int:pk>/', PaymentHistoryDetailView.as_view(), name='payment_history_detail'),
    path('billing/<int:billing_id>/payment-history/', PaymentHistoryListView.as_view(), name='billing_payment_history'),
    path('patient/<int:patient_id>/payment-history/', PaymentHistoryListView.as_view(), name='patient_payment_history'),

    path('billings/', BillingListView.as_view(), name='billing_list'),
    path('billings/create/', BillingCreateView.as_view(), name='billing_payments'),
    path('billings/<int:pk>/', BillingDetailView.as_view(), name='billing_detail'),
    path('billings/<int:pk>/update/', BillingUpdateView.as_view(), name='billing_update'),
    path('billings/<int:pk>/update-status/', BillingStatusUpdateView.as_view(), name='billing_status_update'),
    path('patients/<int:patient_id>/billings/', PatientBillingListView.as_view(), name='patient_billing_list'),



]



