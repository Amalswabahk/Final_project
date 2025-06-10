from django import forms
from .models import Patient,Prescription,TreatmentPlan


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['patient', 'medication', 'dosage', 'frequency', 'instructions', 'duration']

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctor = doctor
        # Customize form fields if needed
        self.fields['patient'].queryset = Patient.objects.all()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.doctor:
            instance.doctor = self.doctor
        if commit:
            instance.save()
        return instance


class TreatmentPlanForm(forms.ModelForm):
    class Meta:
        model = TreatmentPlan
        fields = ['patient', 'diagnosis', 'treatment_goals', 'procedures', 'medications', 'follow_up', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment_goals': forms.Textarea(attrs={'rows': 3}),
            'procedures': forms.Textarea(attrs={'rows': 3}),
            'medications': forms.Textarea(attrs={'rows': 3}),
            'follow_up': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        doctor = kwargs.pop('doctor', None)
        super().__init__(*args, **kwargs)
        if doctor:
            self.fields['patient'].queryset = Patient.objects.filter(
                appointment__provider=doctor
            ).distinct()


from django import forms
from patient_app.models import HealthcareProvider, Appointment
from doctor_app.models import Prescription, TreatmentPlan

class HealthcareProviderProfileForm(forms.ModelForm):
    class Meta:
        model = HealthcareProvider
        fields = [
            'department', 'specialization', 'license_number',
            'profile_image', 'bio', 'years_of_experience'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['status', 'reason']
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

# Include your existing PrescriptionForm and TreatmentPlanForm