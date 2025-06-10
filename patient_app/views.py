from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db import models
from .models import Patient, Appointment, MedicalRecord, Allergy, Billing, Payment, HealthEducation,PaymentHistory
from .forms import (PatientRegistrationForm, AppointmentForm,
                    MedicalRecordForm, AllergyForm, BillingForm, PaymentForm)
from django.utils import timezone
from datetime import timedelta


from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("patient_dashboard")  # Redirect to the dashboard after login
    else:
        form = AuthenticationForm()

    return render(request, "patient_module/login.html", {"form": form})

# In views.py
from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('homepage')  # Redirect to your login page after logout


from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import PatientRegistrationForm
from .models import Patient



from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse  # Add this import
from .forms import PatientRegistrationForm
from django.db import transaction
from .models import Patient


def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():  # Ensures database integrity
                    # Create the User
                    user = form.save(commit=False)
                    user.save()  # Save the user first

                    # Create the Patient profile
                    Patient.objects.create(
                        user=user,
                        date_of_birth=form.cleaned_data['date_of_birth'],
                        gender=form.cleaned_data['gender'],
                        address=form.cleaned_data['address'],
                        phone_number=form.cleaned_data['phone_number'],
                        blood_group=form.cleaned_data['blood_group'],
                        emergency_contact=form.cleaned_data.get('emergency_contact', '')
                    )

                    # Log the user in
                    login(request, user)
                    messages.success(request, 'Registration successful! Welcome to your dashboard!')
                    return redirect(reverse('patient_dashboard'))  # Secure reverse URL lookup

            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
                # No need to manually delete user - transaction.atomic will rollback
    else:
        form = PatientRegistrationForm()

    return render(request, 'patient_module/register.html', {'form': form})


from django.views.generic import TemplateView
from django.utils import timezone
from .models import Appointment, Billing,  MedicalRecord
from doctor_app.models import Prescription


class PatientDashboardView(TemplateView):
    template_name = 'patient_module/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.request.user.patient
        now = timezone.now()

        # Appointments
        upcoming_appointments = Appointment.objects.filter(
            patient=patient,
            date_time__gte=now,
            status='Scheduled'
        ).select_related('Healthcareprovider__user').order_by('date_time')[:5]

        past_appointments = Appointment.objects.filter(
            patient=patient,
            date_time__lt=now
        ).select_related('Healthcareprovider__user').order_by('-date_time')[:5]

        # Bills and Payments
        unpaid_bills = Billing.objects.filter(
            patient=patient,
            status='Pending'
        ).order_by('due_date')[:3]

        # Medical Information
        active_prescriptions = Prescription.objects.filter(
            patient=patient,
            is_active=True
        ).select_related('doctor__user').order_by('-date_prescribed')[:3]

        recent_records = MedicalRecord.objects.filter(
            patient=patient
        ).order_by('-record_date')[:3]

        # Next appointment info
        next_appointment = upcoming_appointments.first()

        context.update({
            'patient': patient,
            'upcoming_appointments': upcoming_appointments,
            'past_appointments': past_appointments,
            'unpaid_bills': unpaid_bills,
            'active_prescriptions': active_prescriptions,
            'recent_records': recent_records,
            'next_appointment': next_appointment,
            'now': now,
            'next_appointment_days': (next_appointment.date_time.date() - now.date()).days
            if next_appointment else None,
        })
        return context


@login_required
def appointment_list(request):
    patient = get_object_or_404(Patient, user=request.user)
    appointments = Appointment.objects.filter(patient=patient).order_by('-date_time')
    return render(request, 'patient_module/dashboard.html', {'appointments': appointments})


@login_required
def medical_records(request):
    patient = get_object_or_404(Patient, user=request.user)
    records = MedicalRecord.objects.filter(patient=patient).order_by('-record_date')
    allergies = Allergy.objects.filter(patient=patient)
    return render(request, 'patient_module/medical_records.html', {
        'records': records,
        'allergies': allergies
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import stripe
from .models import Payment, Billing

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import CreateView
from .models import Billing, Payment
import stripe


class PaymentCreateView(CreateView):
    model = Payment
    fields = ['payment_method', 'notes']  # Removed amount since we'll take it from billing
    template_name = 'payments/make_payment.html'

    def dispatch(self, request, *args, **kwargs):
        self.billing = get_object_or_404(Billing, pk=self.kwargs['billing_id'])

        # Check if billing is already paid
        if self.billing.status == 'Paid':
            messages.warning(request, "This invoice has already been paid.")
            return redirect('billing_detail', pk=self.billing.id)

        # Check if billing is overdue
        if self.billing.due_date < timezone.now().date() and self.billing.status != 'Overdue':
            self.billing.status = 'Overdue'
            self.billing.save()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['billing'] = self.billing
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        context['is_overdue'] = self.billing.due_date < timezone.now().date()
        return context

    def form_valid(self, form):
        payment = form.save(commit=False)
        payment.billing = self.billing
        payment.amount = self.billing.amount  # Set amount from billing
        payment.created_by = self.request.user

        if payment.payment_method == 'credit_card':
            try:
                # Create Stripe PaymentIntent
                intent = stripe.PaymentIntent.create(
                    amount=int(payment.amount * 100),  # Amount in cents
                    currency='usd',
                    metadata={
                        'billing_id': self.billing.id,
                        'invoice_number': self.billing.invoice_number,
                        'patient_id': self.billing.patient.id
                    }
                )
                payment.stripe_payment_intent = intent.id
                payment.save()

                return render(self.request, 'payments/stripe_payment.html', {
                    'payment': payment,
                    'billing': self.billing,
                    'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
                    'client_secret': intent.client_secret
                })
            except Exception as e:
                messages.error(self.request, f"Payment processing error: {str(e)}")
                return self.form_invalid(form)

        # For non-Stripe payment methods
        payment.status = 'completed'
        payment.save()

        # Update billing status
        self.billing.status = 'Paid'
        self.billing.save()

        messages.success(self.request,
                         f"Payment of ${payment.amount} recorded successfully for Invoice #{self.billing.invoice_number}")
        return redirect('billing_detail', pk=self.billing.id)


class PaymentDetailView(DetailView):
    model = Payment
    template_name = 'payments/payment_detail.html'
    context_object_name = 'payment'


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)

    return HttpResponse(status=200)


def handle_payment_success(payment_intent):
    payment_id = payment_intent.metadata.get('payment_id')
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'completed'
        payment.transaction_id = payment_intent.id

        # Retrieve the charge details
        try:
            charges = stripe.Charge.list(payment_intent=payment_intent.id)
            if charges.data:
                payment.stripe_charge_id = charges.data[0].id
                payment.stripe_receipt_url = charges.data[0].receipt_url
        except stripe.error.StripeError:
            pass

        payment.save()
        send_payment_receipt(payment)  # Implement this function

    except Payment.DoesNotExist:
        pass


def handle_payment_failure(payment_intent):
    payment_id = payment_intent.metadata.get('payment_id')
    try:
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'failed'
        payment.save()
        send_payment_failure_notification(payment)  # Implement this function
    except Payment.DoesNotExist:
        pass


def send_payment_receipt(payment):
    """Send payment receipt email to patient"""
    # Implement your email sending logic here
    # Example using Django's send_mail:
    from django.core.mail import send_mail

    subject = f'Payment Receipt for Billing #{payment.billing.id}'
    message = f'''
    Thank you for your payment of ${payment.amount}.

    Billing ID: {payment.billing.id}
    Payment ID: {payment.id}
    Date: {payment.payment_date}

    Receipt URL: {payment.stripe_receipt_url or "Not available"}
    '''

    if payment.billing.patient.user.email:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [payment.billing.patient.user.email],
            fail_silently=False,
        )


def send_payment_failure_notification(payment):
    """Send payment failure notification to patient and admin"""
    # Implement your notification logic here
    pass


# views.py
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

class PaymentHistoryListView(LoginRequiredMixin, ListView):
    model = PaymentHistory
    template_name = 'payments/history_list.html'
    context_object_name = 'history_entries'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'payment',
            'changed_by',
            'payment__billing',
            'payment__billing__patient'
        )

        # Filter by payment ID if provided
        if payment_id := self.request.GET.get('payment_id'):
            queryset = queryset.filter(payment_id=payment_id)

        # Filter by billing ID if provided
        if billing_id := self.request.GET.get('billing_id'):
            queryset = queryset.filter(payment__billing_id=billing_id)

        # Filter by patient ID if provided
        if patient_id := self.request.GET.get('patient_id'):
            queryset = queryset.filter(payment__billing__patient_id=patient_id)

        # Filter by status if provided
        if status := self.request.GET.get('status'):
            queryset = queryset.filter(status=status)

        # Date range filtering
        if date_from := self.request.GET.get('date_from'):
            queryset = queryset.filter(changed_at__gte=date_from)
        if date_to := self.request.GET.get('date_to'):
            queryset = queryset.filter(changed_at__lte=date_to)

        # Search
        if search := self.request.GET.get('search'):
            queryset = queryset.filter(
                Q(payment__transaction_id__icontains=search) |
                Q(payment__stripe_payment_intent_id__icontains=search) |
                Q(notes__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Payment.STATUS_CHOICES
        return context

class PaymentHistoryDetailView(LoginRequiredMixin, DetailView):
    model = PaymentHistory
    template_name = 'payments/history_detail.html'
    context_object_name = 'history_entry'



@login_required
def health_education(request):
    articles = HealthEducation.objects.all().order_by('-published_date')
    categories = HealthEducation.objects.values_list('category', flat=True).distinct()

    selected_category = request.GET.get('category')
    if selected_category:
        articles = articles.filter(category=selected_category)

    return render(request, 'patient_module/health_education.html', {
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category
    })


@login_required
def view_article(request, article_id):
    article = get_object_or_404(HealthEducation, pk=article_id)
    return render(request, 'patient_module/view_article.html', {'article': article})




from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin

from django.utils import timezone
from django.contrib import messages
from django.db.models import F, ExpressionWrapper, DateTimeField
from django.db.models import Value, CharField
from django.db.models.functions import Cast, Concat

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse
from django.utils import timezone

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass user to form for filtering
        return kwargs

    def form_valid(self, form):
        # Automatically set the patient if user is a patient
        if hasattr(self.request.user, 'patient'):
            form.instance.patient = self.request.user.patient
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("appointment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Create New Appointment"
        return context


from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView, DeleteView
from django.utils import timezone


class AppointmentListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Appointment
    template_name = "appointments/appointment_list.html"
    context_object_name = "appointments"
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_authenticated

    def get_queryset(self):
        # Filter appointments based on whether user is a patient or provider
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'patient'):
            return queryset.filter(patient=self.request.user.patient)
        elif hasattr(self.request.user, 'healthcareprovider'):
            return queryset.filter(Healthcareprovider=self.request.user.healthcareprovider)
        return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        queryset = self.get_queryset()  # Get the filtered queryset

        context['upcoming_appointments'] = queryset.filter(date_time__gte=now)
        context['past_appointments'] = queryset.filter(date_time__lt=now)
        return context

class AppointmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = "appointments/appointment_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass user to form for filtering
        return kwargs

    def get_queryset(self):
        queryset = super().get_queryset()
        # Restrict to only appointments owned by the user
        if hasattr(self.request.user, 'patient'):
            return queryset.filter(patient=self.request.user.patient)
        elif hasattr(self.request.user, 'healthcareprovider'):
            return queryset.filter(Healthcareprovider=self.request.user.healthcareprovider)
        return queryset.none()

    def get_success_url(self):
        return reverse("appointment_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Update Appointment"
        return context
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

class AppointmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Appointment
    template_name = "appointments/appointment_delete.html"
    success_url = reverse_lazy("appointment_list")

    def get_queryset(self):
        queryset = super().get_queryset()
        # Restrict to only appointments owned by the user
        if hasattr(self.request.user, 'patient'):
            return queryset.filter(patient=self.request.user.patient)
        elif hasattr(self.request.user, 'healthcareprovider'):
            return queryset.filter(Healthcareprovider=self.request.user.healthcareprovider)
        return queryset.none()

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Appointment was deleted successfully.")
        return super().delete(request, *args, **kwargs)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from django.contrib import messages


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointments/appointment_detail.html"
    context_object_name = "appointment"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Restrict to only appointments the user is involved with
        if hasattr(self.request.user, 'patient'):
            return queryset.filter(patient=self.request.user.patient)
        elif hasattr(self.request.user, 'healthcareprovider'):
            return queryset.filter(Healthcareprovider=self.request.user.healthcareprovider)
        return queryset.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointment = self.object

        # Add related information to context
        context['is_upcoming'] = appointment.date_time >= timezone.now()
        context['can_edit'] = appointment.status == 'Scheduled'

        return context

# views.py
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Billing
from .forms import BillingForm, BillingStatusForm


class BillingListView(ListView):
    model = Billing
    template_name = 'billings/billing_list.html'
    context_object_name = 'billings'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('patient')

        # Search functionality
        if search := self.request.GET.get('search'):
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(patient__user__first_name__icontains=search) |
                Q(patient__user__last_name__icontains=search)
            )

        # Filter by status if provided
        if status := self.request.GET.get('status'):
            queryset = queryset.filter(status=status)

        # Filter by insurance claims if requested
        if self.request.GET.get('insurance_claims') == 'true':
            queryset = queryset.filter(insurance_claim=True)

        # Order by due date (overdue first, then pending, then paid)
        queryset = queryset.order_by(
            'status',  # Pending comes before Paid alphabetically
            'due_date'
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = Billing.status
        context['total_amount'] = sum(b.amount for b in context['billings'])
        return context


class BillingCreateView(CreateView):
    model = Billing
    form_class = BillingForm
    template_name = 'billings/billing_form.html'
    success_url = reverse_lazy('billing_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f'Invoice #{self.object.invoice_number} created successfully')
        return response


class BillingDetailView(DetailView):
    model = Billing
    template_name = 'billings/billing_detail.html'
    context_object_name = 'billing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_form'] = BillingStatusForm(instance=self.object)
        return context


class BillingUpdateView(UpdateView):
    model = Billing
    form_class = BillingForm
    template_name = 'billings/billing_form.html'

    def get_success_url(self):
        return reverse_lazy('billing_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Invoice #{self.object.invoice_number} updated successfully')
        return response


class BillingStatusUpdateView(UpdateView):
    model = Billing
    form_class = BillingStatusForm
    template_name = 'billings/billing_status_update.html'

    def get_success_url(self):
        return reverse_lazy('billing_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Invoice #{self.object.invoice_number} status updated to {self.object.status}')
        return response


class PatientBillingListView(ListView):
    model = Billing
    template_name = 'billings/patient_billing_list.html'
    context_object_name = 'billings'
    paginate_by = 10

    def get_queryset(self):
        patient = get_object_or_404(Patient, pk=self.kwargs['patient_id'])
        return super().get_queryset().filter(patient=patient).select_related('patient')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(Patient, pk=self.kwargs['patient_id'])
        return context

# For list view
def health_education_list(request):
    articles = HealthEducation.objects.all().order_by('-published_date')
    categories = HealthEducation.objects.values_list('category', flat=True).distinct()
    return render(request, 'health_education.html', {
        'articles': articles,
        'categories': categories
    })

# For detail view
def health_education_detail(request, slug):
    article = get_object_or_404(HealthEducation, slug=slug)
    return render(request, 'health_education.html', {
        'health_education': article
    })