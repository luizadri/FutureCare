from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser 

# Create your models here.

class CustomUser(AbstractUser):
    user_type = models.CharField(default = 1, max_length=10)

class Patients(models.Model):

    user_member = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=100)
    number = models.BigIntegerField()
    image = models.ImageField(blank=True,upload_to='images/',null=True)
    # def current_assignment(self):
    #     return self.assignment_set.last()

class Departments(models.Model):

    department_name = models.CharField(max_length=255,null=True)

class Doctors(models.Model):

    user_department = models.ForeignKey(Departments,on_delete=models.CASCADE,null=True)
    user_member = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=100)
    number = models.BigIntegerField()
    cv = models.FileField(upload_to='CV/', null=True, blank=True)
    image = models.ImageField(blank=True,upload_to='images/',null=True)
    # def current_assignment(self):
    #     return self.assignment_set.last()

class DoctorLeave(models.Model):
    doctor_name = models.ForeignKey(Doctors, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    attendance = models.CharField(max_length=20)

class Appoinment(models.Model):

    user_member = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True)
    patient = models.ForeignKey(Patients,on_delete=models.CASCADE,null=True)
    doctor = models.ForeignKey(Doctors,on_delete=models.CASCADE,null=True)
    department = models.ForeignKey(Departments,on_delete=models.CASCADE,null=True)
    description = models.CharField(max_length=250, null=True, blank = True)
    date = models.DateField()
    status = models.CharField(max_length=250, default = 'PENDING')

class Notification(models.Model):

    doctor = models.ForeignKey(Doctors,on_delete=models.CASCADE,null=True)
    status = models.CharField(max_length=250, default = 'NEW')
