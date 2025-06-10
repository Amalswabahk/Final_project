from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Patient, HealthcareProvider, Appointment,
    MedicalRecord, Allergy, Billing,
    Payment, HealthEducation, Department
)
from django.utils.html import format_html


class PatientInline(admin.StackedInline):
    model = Patient
    can_delete = False
    verbose_name_plural = 'Patient Profile'
    fields = ('date_of_birth', 'gender', 'blood_group', 'phone_number', 'emergency_contact', 'address')
    fk_name = 'user'


class HealthcareProviderInline(admin.StackedInline):
    model = HealthcareProvider
    can_delete = False
    verbose_name_plural = 'Healthcare Provider Profile'
    fields = ('department', 'specialization', 'license_number', 'years_of_experience', 'is_verified')
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    def get_inlines(self, request, obj):
        if obj and hasattr(obj, 'patient'):
            return [PatientInline]
        elif obj and hasattr(obj, 'Healthcareprovider'):
            return [HealthcareProviderInline]
        return []

    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type')

    def user_type(self, obj):
        if hasattr(obj, 'patient'):
            return 'Patient'
        elif hasattr(obj, 'Healthcareprovider'):
            return 'Healthcare Provider'
        return 'Staff'

    user_type.short_description = 'User Type'


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'blood_group', 'phone_number')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    list_filter = ('gender', 'blood_group')
    readonly_fields = ('age',)


@admin.register(HealthcareProvider)
class HealthcareProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'department', 'is_verified', 'image_preview')
    list_filter = ('specialization', 'department', 'is_verified')
    search_fields = ('user__first_name', 'user__last_name', 'license_number')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.profile_image.url)
        return "No image"

    image_preview.short_description = 'Profile Image Preview'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_info', 'provider_info', 'formatted_date_time', 'status')
    list_filter = ('status', 'date_time', 'Healthcareprovider__specialization')
    date_hierarchy = 'date_time'
    search_fields = (
        'patient__user__first_name',
        'patient__user__last_name',
        'Healthcareprovider__user__first_name',
        'Healthcareprovider__user__last_name',
        'reason'
    )

    def patient_info(self, obj):
        return obj.patient.user.get_full_name()

    patient_info.short_description = 'Patient'
    patient_info.admin_order_field = 'patient__user__last_name'

    def provider_info(self, obj):
        return f"Dr. {obj.Healthcareprovider.user.get_full_name()} ({obj.Healthcareprovider.specialization})"

    provider_info.short_description = 'Provider'
    provider_info.admin_order_field = 'Healthcareprovider__user__last_name'

    def formatted_date_time(self, obj):
        return obj.date_time.strftime("%Y-%m-%d %H:%M")

    formatted_date_time.short_description = 'Date & Time'
    formatted_date_time.admin_order_field = 'date_time'


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'record_date', 'diagnosis_short')
    list_filter = ('record_date',)
    date_hierarchy = 'record_date'
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'diagnosis')

    def diagnosis_short(self, obj):
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis

    diagnosis_short.short_description = 'Diagnosis'


@admin.register(Allergy)
class AllergyAdmin(admin.ModelAdmin):
    list_display = ('patient', 'name', 'severity')
    list_filter = ('severity',)
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'name')


@admin.register(Billing)
class BillingAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'patient', 'date_issued', 'due_date', 'amount', 'status')
    list_filter = ('status', 'date_issued', 'insurance_claim')
    date_hierarchy = 'date_issued'
    search_fields = ('invoice_number', 'patient__user__first_name', 'patient__user__last_name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('billing', 'amount', 'payment_date', 'payment_method')
    list_filter = ('payment_method', 'payment_date')
    date_hierarchy = 'payment_date'
    search_fields = ('billing__invoice_number', 'transaction_id')


@admin.register(HealthEducation)
class HealthEducationAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date')
    list_filter = ('category', 'published_date')
    date_hierarchy = 'published_date'
    search_fields = ('title', 'category', 'content')
    prepopulated_fields = {'slug': ('title',)}


# Unregister and re-register User if needed
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)