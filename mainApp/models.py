from django.db import models

# Create your models here.
from django import db
from django.db import models


class insertdata(models.Model):
    doctorname = models.CharField(max_length=100)
    password = models.CharField(max_length=100)



class insertnewpatient(models.Model):
    pname = models.CharField(max_length=50)
    age = models.IntegerField()
    gender = models.CharField(max_length=100)
    diabetic = models.CharField(max_length=100)
    bloodpressure = models.CharField(max_length=100)
    heartdiseases = models.CharField(max_length=100)
    prescriptions = models.CharField(max_length=300)
    treatmentplan = models.CharField(max_length=500)
    imgPath = models.CharField(max_length=100)
    tumortype = models.CharField(max_length=100)
    patientID = models.CharField(max_length=100)

    class Meta:
        db_table = 'patient'


