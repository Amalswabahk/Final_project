from django.db import models
from django.db import models
from django.contrib.auth.models import User
from admin_app.models import Department
from django.core.validators import MinValueValidator, MaxValueValidator



from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from datetime import date


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say')
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('U', 'Unknown')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(default=date.today)  # Changed to date.today
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, default='U')
    phone_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        # Only create user if this is a new Patient AND no user is assigned
        if not self.pk and not self.user_id:
            if not self.phone_number:
                raise ValueError("Phone number is required to create a new patient")

            username = f"patient_{self.phone_number}"
            user = User.objects.create_user(
                username=username,
                password=None  # Will set unusable password
            )
            self.user = user
        super().save(*args, **kwargs)

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
import os


def healthcare_provider_image_path(instance, filename):
    # Upload to: media/healthcare_providers/<username>/<filename>
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.user.username)}-profile.{ext}"
    return os.path.join('healthcare_providers', instance.user.username, filename)


class HealthcareProvider(models.Model):

    user = models.OneToOneField(User,
            on_delete=models.CASCADE,
            related_name='healthcareprovider')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                   null=True, blank=True,
                                   related_name='providers')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50)
    profile_image = models.ImageField(
        upload_to=healthcare_provider_image_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        blank=True,
        null=True,
        help_text="Upload a professional profile photo (JPEG or PNG)"
    )
    bio = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialization}"

    def save(self, *args, **kwargs):
        # Delete old image when updating
        try:
            old = HealthcareProvider.objects.get(pk=self.pk)
            if old.profile_image and old.profile_image != self.profile_image:
                old.profile_image.delete(save=False)
        except HealthcareProvider.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return '/static/images/default-provider.jpg'  # Default image path


import random
import string
class Appointment(models.Model):

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    Healthcareprovider = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE,
                                        verbose_name="Healthcare Provider")  # Added verbose_name
    date_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Rescheduled', 'Rescheduled')
    ])
    reason = models.TextField()

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return f"{self.patient} with {self.Healthcareprovider} on {self.date_time}"  # Changed to Healthcareprovider

    @property
    def provider(self):
        """Alias for Healthcareprovider for backward compatibility"""
        return self.Healthcareprovider

    def save(self, *args, **kwargs):
        created = not self.pk  # Check if this is a new instance
        super().save(*args, **kwargs)

        if created:
            # Generate a unique invoice number
            def generate_invoice_number():
                date_part = timezone.now().strftime('%Y%m%d')
                random_part = ''.join(random.choices(string.digits, k=6))
                return f"INV-{date_part}-{random_part}"

            # Calculate due date (7 days from now)
            due_date = timezone.now().date() + timezone.timedelta(days=7)

            # Create the billing record
            Billing.objects.create(
                patient=self.patient,
                invoice_number=generate_invoice_number(),
                due_date=due_date,
                amount=500.00,  # Set your default appointment fee here
                status='Pending',
                insurance_claim=False
            )


class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    record_date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment = models.TextField()
    prescribed_medications = models.TextField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.patient} - {self.diagnosis[:50]}..."


class Allergy(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=[
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe')
    ])
    reaction = models.TextField()

    def __str__(self):
        return f"{self.patient} - {self.name}"

from django.utils import timezone
class Billing(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    date_issued = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Overdue', 'Overdue')
    ])
    service_description = models.CharField(max_length=200, default='Consultation')
    service_date = models.DateField(default=timezone.now)
    insurance_claim = models.BooleanField(default=False)
    insurance_details = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.patient}"


from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('insurance', 'Insurance'),
        ('cash', 'Cash'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]

    billing = models.ForeignKey('Billing', on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    # Stripe-specific fields
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_charge_id = models.CharField(max_length=100, blank=True)
    stripe_receipt_url = models.URLField(blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)

    # Audit fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_payments'
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['billing']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment #{self.id} - ${self.amount} for {self.billing} ({self.get_status_display()})"

    @property
    def is_paid(self):
        return self.status == 'completed'

    @property
    def remaining_balance(self):
        return self.billing.total_amount - sum(
            p.amount for p in self.billing.payments.filter(status='completed')
        )

    # models.py
    def create_stripe_payment_intent(self):
        """Create a Stripe PaymentIntent for this payment in INR"""
        if not hasattr(settings, 'STRIPE_SECRET_KEY'):
            raise ValueError("Stripe secret key not configured")

        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Create customer if not exists
        if not self.stripe_customer_id and self.billing.patient.user.email:
            customer = stripe.Customer.create(
                email=self.billing.patient.user.email,
                name=str(self.billing.patient),
                address={
                    'country': 'IN'  # Set country to India
                },
                metadata={
                    "patient_id": self.billing.patient.id,
                    "billing_id": self.billing.id
                }
            )
            self.stripe_customer_id = customer.id
            self.save()

        intent = stripe.PaymentIntent.create(
            amount=int(self.amount * 100),  # Convert rupees to paise (100 paise = 1 INR)
            currency=settings.STRIPE_CURRENCY,  # Will use 'inr' from settings
            customer=self.stripe_customer_id if self.stripe_customer_id else None,
            metadata={
                "payment_id": self.id,
                "billing_id": self.billing.id,
                "patient_id": self.billing.patient.id
            },
            description=f"Payment for billing #{self.billing.id}",
            receipt_email=self.billing.patient.user.email if self.billing.patient.user.email else None,
            shipping={
                'name': str(self.billing.patient),
                'address': {
                    'country': 'IN'
                }
            }
        )
        self.stripe_payment_intent_id = intent.id
        self.save()
        return intent


class HealthEducation(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)  # Added slug field
    content = models.TextField()
    category = models.CharField(max_length=100)
    published_date = models.DateField(auto_now_add=True)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)




# models.py
class PaymentHistory(models.Model):
    """Tracks all changes to Payment records"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='history_entries')
    status = models.CharField(max_length=20, choices=Payment.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-changed_at']
        verbose_name_plural = 'Payment Histories'
        indexes = [
            models.Index(fields=['payment']),
            models.Index(fields=['status']),
            models.Index(fields=['changed_at']),
        ]

    def __str__(self):
        return f"{self.payment} - {self.get_status_display()} at {self.changed_at}"
