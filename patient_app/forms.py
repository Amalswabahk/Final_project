from django import forms
from .models import  Appointment, MedicalRecord, Allergy, Billing, Payment,HealthcareProvider
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date



from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Patient

class PatientRegistrationForm(UserCreationForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES)
    blood_group = forms.ChoiceField(choices=Patient.BLOOD_GROUP_CHOICES)
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    emergency_contact = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'first_name', 'last_name', 'date_of_birth',
                  'gender', 'blood_group', 'phone_number',
                  'emergency_contact', 'address']


from django import forms


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['Healthcareprovider', 'date_time', 'reason']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter healthcare providers based on user type
        if self.user and hasattr(self.user, 'patient'):
            self.fields['Healthcareprovider'].queryset = HealthcareProvider.objects.all()
        elif self.user and hasattr(self.user, 'healthcareprovider'):
            # If user is a provider, they can't select providers (only patients can)
            del self.fields['Healthcareprovider']
            if not self.instance.pk:  # Only for new appointments
                self.fields['patient'] = forms.ModelChoiceField(
                    queryset=Patient.objects.all()
                )


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'prescribed_medications', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment': forms.Textarea(attrs={'rows': 3}),
            'prescribed_medications': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class AllergyForm(forms.ModelForm):
    class Meta:
        model = Allergy
        fields = ['name', 'severity', 'reaction']
        widgets = {
            'reaction': forms.Textarea(attrs={'rows': 3}),
        }


class BillingForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Billing
        fields = ['amount', 'due_date', 'insurance_claim', 'insurance_details']
        widgets = {
            'insurance_details': forms.Textarea(attrs={'rows': 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method', 'transaction_id']

# users/forms.py
from django.contrib.auth.forms import PasswordResetForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError("There is no user registered with this email address.")
        return email


# forms.py
from django import forms
from .models import Billing
from django.core.validators import MinValueValidator
from django.utils import timezone


class BillingForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=timezone.now().date()
    )

    amount = forms.DecimalField(
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )

    class Meta:
        model = Billing
        fields = ['patient', 'invoice_number', 'due_date', 'amount',
                  'insurance_claim', 'insurance_details']
        widgets = {
            'insurance_details': forms.Textarea(attrs={'rows': 3}),
        }


class BillingStatusForm(forms.ModelForm):
    class Meta:
        model = Billing
        fields = ['status']
