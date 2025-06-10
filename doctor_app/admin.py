from django.contrib import admin

# Register your models here.
from .models import Prescription, DrugInteraction, TreatmentPlan


class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'medication', 'date_prescribed', 'is_active')
    list_filter = ('is_active', 'date_prescribed')
    search_fields = ('patient__user__username', 'doctor__user__username', 'medication')


class DrugInteractionAdmin(admin.ModelAdmin):
    list_display = ('drug1', 'drug2', 'severity')
    search_fields = ('drug1', 'drug2')


class TreatmentPlanAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'created_date', 'diagnosis_short')
    search_fields = ('patient__user__username', 'doctor__user__username', 'diagnosis')

    def diagnosis_short(self, obj):
        return obj.diagnosis[:50] + '...' if len(obj.diagnosis) > 50 else obj.diagnosis

    diagnosis_short.short_description = 'Diagnosis'


admin.site.register(Prescription, PrescriptionAdmin)
admin.site.register(DrugInteraction, DrugInteractionAdmin)
admin.site.register(TreatmentPlan, TreatmentPlanAdmin)
