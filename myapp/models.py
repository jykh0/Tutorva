from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    uname = models.CharField("Username", max_length=50, unique=True)
    email = models.EmailField("Email", max_length=50, unique=True)
    password = models.CharField(max_length=128)
    user_type = models.CharField("User Type", max_length=10, choices=(('student', 'Student'), ('tutor', 'Tutor')))
    reset_token = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField("Is Active", default=True)

def __str__(self):
    return self.uname

class Student(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField("Full Name", max_length=50)
    gender = models.CharField("Gender", max_length=10, choices=(('male', 'Male'), ('female', 'Female')))
    phone = models.CharField("Phone", max_length=10, unique=True)
    level = models.CharField("Level", max_length=20, choices=(('high school', 'High School'), ('secondary', 'Secondary')))
    subject = models.CharField("Subject", max_length=50)
    street = models.CharField("Street", max_length=100)
    city = models.CharField("City", max_length=50)
    state = models.CharField("State", max_length=50)
    pincode = models.CharField("Pincode", max_length=10)
    location_type = models.CharField("Location Type", max_length=20, choices=(('home tuition', 'Home Tuition'), ('tutor location', 'Tutor Location')))
    profile_picture = models.ImageField(
        upload_to='profile_pics/students/', default='profile_pics/default_profile.jpg', null=True, blank=True)

    def __str__(self):
        return self.fullname

class Tutor(models.Model):
    uid = models.ForeignKey(User, on_delete=models.CASCADE)
    fullname = models.CharField("Full Name", max_length=50)
    gender = models.CharField("Gender", max_length=10, choices=(('male', 'Male'), ('female', 'Female')))
    phone = models.CharField("Phone", max_length=10, unique=True)
    qualifications = models.CharField("Qualifications", max_length=100)
    subjects_offered = models.CharField("Subjects Offered", max_length=100)
    level = models.CharField("Level", max_length=20, choices=(('high school', 'High School'), ('secondary', 'Secondary')))
    street = models.CharField("Street", max_length=100)
    city = models.CharField("City", max_length=50)
    state = models.CharField("State", max_length=50)
    pincode = models.CharField("Pincode", max_length=10)
    availability = models.CharField("Availability", max_length=20, choices=(('offline', 'Offline'), ('online', 'Online'), ('both', 'Both')))
    location_type = models.CharField("Location Type", max_length=20, choices=(('home tuition', 'Home Tuition'), ('tutor location', 'Tutor Location')))
    profile_picture = models.ImageField(upload_to='profile_pics/tutors/', default='profile_pics/default_profile.jpg', null=True, blank=True)

    def __str__(self):
        return self.fullname

class Admin(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.email


class Enquiry(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enquiries')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, related_name='responses')
    message = models.TextField("Enquiry Message")
    response = models.TextField("Tutor Response", blank=True, null=True)
    status = models.CharField("Status", max_length=20, choices=[
        ('pending', 'Pending'),
        ('answered', 'Answered'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tutor_x = models.BooleanField(default=False)
    student_x = models.BooleanField(default=False)

    def __str__(self):
        return f"Enquiry from {self.student.fullname} to {self.tutor.fullname}"

class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    tutor_x = models.BooleanField(default=False)
    student_x = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rejection_time = models.DateTimeField(null=True, blank=True)

    def can_rebook(self):
        if self.is_rejected and self.rejection_time:
            return timezone.now() > self.rejection_time + timedelta(days=7)
        return True

class StudentTutorRelation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.fullname} - {self.tutor.fullname}"