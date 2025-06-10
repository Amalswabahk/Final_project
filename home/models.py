from django.db import models

# Create your models here.
from django.db import models
from django_resized import ResizedImageField


class HospitalProfile(models.Model):
    name = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True)
    description = models.TextField()
    established_date = models.DateField()
    logo = ResizedImageField(size=[200, 200], upload_to='hospital/logo/', blank=True)
    banner_image = ResizedImageField(size=[1200, 400], upload_to='hospital/banner/', blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class DepartmentHighlight(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")

    def __str__(self):
        return self.name


class DoctorHighlight(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='doctors')
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    photo = ResizedImageField(size=[300, 300], upload_to='doctors/highlights/', blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"


class Testimonial(models.Model):
    hospital = models.ForeignKey(HospitalProfile, on_delete=models.CASCADE, related_name='testimonials')
    patient_name = models.CharField(max_length=100)
    content = models.TextField()
    photo = ResizedImageField(size=[100, 100], upload_to='testimonials/', blank=True)
    rating = models.PositiveSmallIntegerField(default=5)

    def __str__(self):
        return f"Testimonial from {self.patient_name}"
