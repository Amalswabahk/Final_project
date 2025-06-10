from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.utils.text import slugify
from .models import Facility, Department, Resource
from patient_app.models import (
    Appointment, Patient, HealthcareProvider,
    MedicalRecord, Allergy, Billing,
    Payment, HealthEducation
)


class HealthcareAdminSite(AdminSite):
    site_header = "Healthcare System Administration"
    site_title = "Healthcare System Admin Portal"
    index_title = "Welcome to Healthcare System Administration"
    site_url = "/"


healthcare_admin_site = HealthcareAdminSite(name='healthcare_admin')


# Custom Admin Classes
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_info', 'provider_info', 'formatted_date_time', 'status']
    list_filter = ['status', 'date_time', 'Healthcareprovider__specialization']
    search_fields = [
        'patient__user__first_name',
        'patient__user__last_name',
        'Healthcareprovider__user__first_name',
        'Healthcareprovider__user__last_name',
        'reason'
    ]
    date_hierarchy = 'date_time'
    ordering = ['-date_time']
    raw_id_fields = ['patient', 'Healthcareprovider']

    def patient_info(self, obj):
        return obj.patient.user.get_full_name()

    patient_info.short_description = 'Patient'

    def provider_info(self, obj):
        return f"Dr. {obj.Healthcareprovider.user.get_full_name()}"

    provider_info.short_description = 'Provider'

    def formatted_date_time(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M")

    formatted_date_time.short_description = 'Appointment Time'


class PatientAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'age_display', 'gender', 'blood_group', 'contact_info']
    search_fields = ['user__first_name', 'user__last_name', 'phone_number']
    list_filter = ['gender', 'blood_group']
    raw_id_fields = ['user']

    def user_info(self, obj):
        return obj.user.get_full_name()

    user_info.short_description = 'Patient Name'

    def age_display(self, obj):
        return obj.age

    age_display.short_description = 'Age'

    def contact_info(self, obj):
        return format_html('{}<br>Emergency: {}', obj.phone_number, obj.emergency_contact)

    contact_info.short_description = 'Contact Information'


class HealthcareProviderAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'specialization', 'license_number', 'is_verified']
    search_fields = ['user__first_name', 'user__last_name', 'specialization', 'license_number']
    list_filter = ['specialization', 'is_verified']
    raw_id_fields = ['user']

    def user_info(self, obj):
        return f"Dr. {obj.user.get_full_name()}"

    user_info.short_description = 'Provider Name'


class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient_info', 'record_date', 'diagnosis_short']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'diagnosis']
    date_hierarchy = 'record_date'
    raw_id_fields = ['patient']

    def patient_info(self, obj):
        return obj.patient.user.get_full_name()

    patient_info.short_description = 'Patient'

    def diagnosis_short(self, obj):
        return f"{obj.diagnosis[:50]}..." if len(obj.diagnosis) > 50 else obj.diagnosis

    diagnosis_short.short_description = 'Diagnosis'


class AllergyAdmin(admin.ModelAdmin):
    list_display = ['patient_info', 'name', 'severity']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'name']
    list_filter = ['severity']
    raw_id_fields = ['patient']

    def patient_info(self, obj):
        return obj.patient.user.get_full_name()

    patient_info.short_description = 'Patient'


class BillingAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'patient_info', 'date_issued', 'amount', 'status']
    search_fields = ['invoice_number', 'patient__user__first_name', 'patient__user__last_name']
    date_hierarchy = 'date_issued'
    list_filter = ['status', 'insurance_claim']
    raw_id_fields = ['patient']

    def patient_info(self, obj):
        return obj.patient.user.get_full_name()

    patient_info.short_description = 'Patient'


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['billing_info', 'amount', 'payment_date', 'payment_method']
    search_fields = ['billing__invoice_number', 'transaction_id']
    date_hierarchy = 'payment_date'
    list_filter = ['payment_method']

    def billing_info(self, obj):
        return f"Invoice #{obj.billing.invoice_number}"

    billing_info.short_description = 'Billing'


class HealthEducationAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'published_date']
    search_fields = ['title', 'category', 'content']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    list_filter = ['category']


# Register models
healthcare_admin_site.register(User)
healthcare_admin_site.register(Group)
healthcare_admin_site.register(Facility)
healthcare_admin_site.register(Department)
healthcare_admin_site.register(Resource)
healthcare_admin_site.register(Appointment, AppointmentAdmin)
healthcare_admin_site.register(Patient, PatientAdmin)
healthcare_admin_site.register(HealthcareProvider, HealthcareProviderAdmin)
healthcare_admin_site.register(MedicalRecord, MedicalRecordAdmin)
healthcare_admin_site.register(Allergy, AllergyAdmin)
healthcare_admin_site.register(Billing, BillingAdmin)
healthcare_admin_site.register(Payment, PaymentAdmin)
healthcare_admin_site.register(HealthEducation, HealthEducationAdmin)

# Register with default admin if needed
admin.site.register(Facility)

admin.site.register(Resource)