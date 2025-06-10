from django.db import models
from django.contrib.auth.models import User
from patient_app.models import Patient,HealthcareProvider

class PrescriptionManager(models.Manager):
    def active(self):
        return self.filter(is_active=True)


class Prescription(models.Model):
    doctor = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date_prescribed = models.DateField(auto_now_add=True)
    medication = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.medication} for {self.patient}"


class DrugInteraction(models.Model):
    drug1 = models.CharField(max_length=200)
    drug2 = models.CharField(max_length=200)
    severity = models.CharField(max_length=50, choices=[
        ('Mild', 'Mild'),
        ('Moderate', 'Moderate'),
        ('Severe', 'Severe')
    ])
    description = models.TextField()

    def __str__(self):
        return f"{self.drug1} + {self.drug2} ({self.severity})"


class TreatmentPlan(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(HealthcareProvider, on_delete=models.CASCADE)
    created_date = models.DateField(auto_now_add=True)
    diagnosis = models.TextField()
    treatment_goals = models.TextField()
    procedures = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    follow_up = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Treatment plan for {self.patient} by {self.doctor}"
