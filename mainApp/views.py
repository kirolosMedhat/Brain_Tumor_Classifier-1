import cv2
import imutils
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from tensorflow import keras
import numpy as np
import pyodbc
from mainApp import Prediction
from mainApp.models import insertnewpatient,insertdata,treatmentplan
from django.db import models


# load ml models.

bi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                   r'\mlModels\bi_model.h5')

multi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                      r'\mlModels\multi_model.h5')

sql_connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=DESKTOP-8A7J2CA;'
                                'Database=Brain_tumor;'
                                'Trusted_Connection=yes;')


def Login(request):
    global dn, pwd
    if request.method == "GET":
        return render(request, 'Login/index.html')
    request.POST.get('doctorname') and request.POST.get('password')
    insertvalues = insertdata()
    insertvalues.doctorname = request.POST.get('doctorname')
    insertvalues.password = request.POST.get('password')
    insertvalues.save
    cursor = sql_connection.cursor()
    try:
        cursor.execute("insert into Doctor values ('" + insertvalues.doctorname + "','" + insertvalues.password + "')")
    except:
        print("*********************************************")
    cursor.commit()
    return render(request, 'Login/index.html')


def Register(request):
    request.POST.get('doctorname') and request.POST.get('password')
    insertvalues = insertdata()
    insertvalues.doctorname = request.POST.get('doctorname')
    insertvalues.password = request.POST.get('password')
    insertvalues.save
    cursor = sql_connection.cursor()
    try:
        cursor.execute("insert into Doctor values ('" + insertvalues.doctorname + "','" + insertvalues.password + "')")
    except:
        print("*********************************************")
    cursor.commit()
    return render(request, 'Login/index.html')

def Home(request):
    global dn, pwd
    if request.method == "GET":
        return render(request, 'Home/home.html')
    print(request.POST.get("signin")+"________________________________________")
    #print(request.POST.get("signup")+"************************")
    if request.POST.get("signup"):
        request.POST.get('doctorname') and request.POST.get('password')
        insertvalues = insertdata()
        insertvalues.doctorname = request.POST.get('doctorname')
        insertvalues.password = request.POST.get('password')
        insertvalues.save
        cursor = sql_connection.cursor()
        try:
            cursor.execute(
                "insert into Doctor values ('" + insertvalues.doctorname + "','" + insertvalues.password + "')")
        except:
            print("*********************************************")
        cursor.commit()
        return render(request, 'Login/index.html')
    #login
    cursor = sql_connection.cursor()
    d = request.POST
    for key, value in d.items():
        c = "SELECT doctorID, password from Doctor where doctorID='" + request.POST.get(
            "auth_name") + "'and password=" + "'" + request.POST.get("pswd") + "';"
        print(c)
        cursor.execute(c)
        t = tuple(cursor.fetchall())
        if t == ():
            return render(request, 'Login/index.html')
        else:
            print('hello')
            return render(request, "Home/home.html")



def user(request):
    return render(request, 'Login/index.html')


def Result(request):
    if request.method == 'GET':
        return render(request, 'Result/result.html')
    x = False
    # saving img
    fileObj = request.FILES['imgPath']
    fs = FileSystemStorage()
    testImgPath = fs.save(fileObj.name, fileObj)
    testImgPath = fs.url(testImgPath)
    testimagepath = '.' + testImgPath
    #insert new patient
    patient(request, testimagepath)
# start preditions
    bi_prediction = Prediction.biModelPrediction(testimagepath)

    multi_prediction = [0.00, 0.00, 0.00]
    multi_prediction_txt = "No tumor"
    if bi_prediction > 0.005:
        multi_prediction = Prediction.multiModelPrediction(testimagepath)
        multi_prediction_txt = Prediction.multiModelTranslate(multi_prediction)

    context = {'testImgPath': testImgPath,
               'bi_prediction': round(float(bi_prediction[0]) * 100, 3),
               'multi_prediction': multi_prediction[0],
               'multi_prediction_txt': multi_prediction_txt
               }
    return render(request, 'Result/result.html', context)


# skip for now
def translate(predict, class_names):
    index = np.argmax(predict)
    return class_names[index]


def patient(request, testimagepath):

    request.POST.get('pname') and request.POST.get('age') and request.POST.get('gender') and request.POST.get(
        'diabetic') and request.POST.get('bloodpressure') and request.POST.get('heartdiseases') and request.POST.get(
        'surgery1') and request.POST.get('surgery2') and request.POST.get('surgery3') and request.POST.get(
        'prescriptions') and request.POST.get('imgPath') and request.POST.get('tumortype')
    insertpatient = insertnewpatient()
    insertpatient.pname = request.POST.get('pname')
    insertpatient.age = request.POST.get('age')
    insertpatient.gender = request.POST.get('gender')
    insertpatient.diabetic = request.POST.get('diabetic')
    insertpatient.bloodpressure = request.POST.get('bloodpressure')
    insertpatient.heartdiseases = request.POST.get('heartdiseases')
    insertpatient.surgery1 = request.POST.get('surgery1')
    insertpatient.surgery2 = request.POST.get('surgery2')
    insertpatient.surgery3 = request.POST.get('surgery3')
    insertpatient.prescriptions = request.POST.get('prescriptions')
    insertpatient.imgPath = testimagepath
    insertpatient.tumortype = request.POST.get('tumortype')
    insertpatient.save
    cursor = sql_connection.cursor()
    cursor.execute("insert into patient values ('" + insertpatient.pname + "','" + str(
        insertpatient.age) + "','" + insertpatient.gender + "','" + insertpatient.diabetic + "','" + insertpatient.bloodpressure
                   + "','" + insertpatient.bloodpressure + "','" + insertpatient.surgery1
                   + "','" + insertpatient.surgery2 + "','" + insertpatient.surgery3 + "','" +
                   insertpatient.prescriptions + "','" + testimagepath + "','" + insertpatient.tumortype + "')")

    cursor.commit()


def New(request):
    return render(request, 'New-patiant/patiant.html')






def Search(request):
    if request.method == 'GET':
        getvalue = insertnewpatient()
        getvalue.pname = request.POST.get('pname')
        getvalue.age = request.POST.get('age')
        getvalue.gender = request.POST.get('gender')
        getvalue.diabetic = request.POST.get('diabetic')
        getvalue.bloodpressure = request.POST.get('bloodpressure')
        getvalue.heartdiseases = request.POST.get('heartdiseases')
        getvalue.surgery1 = request.POST.get('surgery1')
        getvalue.surgery2 = request.POST.get('surgery2')
        getvalue.surgery3 = request.POST.get('surgery3')
        getvalue.prescriptions = request.POST.get('prescriptions')
        getvalue.tumortype = request.POST.get('tumortype')

        cursor = sql_connection.cursor()
        result = cursor.execute(
            "select PatientID, pname, age, gender, diabetic ,bloodpressure "
            ",heartdiseases , surgery1 , surgery2 , surgery3, prescriptions, imgPath  from patient")


        return render(request, 'Search/search.html', {"result": result})





    #cursor.execute("select  imgPath from patient where PatientID ='"+request.GET.get("PatientId")+"';")
    #x= cursor.fetchall()



    #return render(request, 'Search/search.html', {"result": result})




