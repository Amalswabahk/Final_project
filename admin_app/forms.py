from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import Group
from .models import *
from django import forms

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        fields = '__all__'

class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = '__all__'
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['head'].queryset = HealthcareProvider.objects.all()

class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class GroupPermissionForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'permissions']
        widgets = {
            'permissions': forms.SelectMultiple(attrs={'class': 'select2'}),
        }


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from patient_app.models import HealthcareProvider

class HealthcareProviderUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

class HealthcareProviderForm(forms.ModelForm):
    class Meta:
        model = HealthcareProvider
        fields = ['department', 'specialization', 'license_number',
                 'profile_image', 'bio', 'years_of_experience']