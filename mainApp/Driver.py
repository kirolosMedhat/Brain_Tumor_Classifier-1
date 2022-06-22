import cv2
import imutils
from django.shortcuts import render
import os
from tensorflow import keras
import numpy as np
import pyodbc
from mainApp.similar_search import Index,SearchImage
from mainApp.models import insertnewpatient, insertdata

sql_connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=DESKTOP-8A7J2CA;'
                                'Database=Brain_tumor;'
                                'Trusted_Connection=yes;')
bi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                   r'\mlModels\bi_model.h5')

multi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                      r'\mlModels\multi_model.h5')


def Register(request):
    request.POST.get('doctorname') and request.POST.get('password')
    insertvalues = insertdata()
    insertvalues.doctorname = request.POST.get('doctorname')
    insertvalues.password = request.POST.get('password')
    insertvalues.save()
    cursor = sql_connection.cursor()
    cursor.execute("insert into Doctor values ('" + insertvalues.doctorname + "','" + insertvalues.password + "')")
    cursor.commit()
    return render(request, 'Login/index.html')


def Login(request):
    cursor = sql_connection.cursor()
    d = request.POST
    for key, value in d.items():
        sql_command = "SELECT doctorID, password from Doctor where doctorID='" + request.POST.get(
            "auth_name") + "'and password=" + "'" + request.POST.get("pswd") + "';"
        cursor.execute(sql_command)
        t = tuple(cursor.fetchall())
        if t == ():
            return render(request, 'Login/index.html')
        else:
            print('hello')
            return render(request, "Home/home.html")


def Search(request):
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


def insertNewPatient(request, testimagepath,tumor_type):
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
    insertpatient.save()
    cursor = sql_connection.cursor()
    cursor.execute("insert into patient(pname,age,gender,diabetic,bloodpressure,heartdiseases,surgery1,surgery2,"
                   "surgery3,prescriptions,imgPath,tumortype) values ('" + insertpatient.pname + "','" + str(insertpatient.age) + "',"
                                                                                                               "'" +
                   insertpatient.gender + "','" + insertpatient.diabetic + "','" + insertpatient.bloodpressure
                   + "','" + insertpatient.heartdiseases + "','" + insertpatient.surgery1
                   + "','" + insertpatient.surgery2 + "','" + insertpatient.surgery3 + "','" +
                   insertpatient.prescriptions + "','" + testimagepath + "','"+tumor_type+"');")

    cursor.commit()


def biModelPrediction(image_path):
    image = preprocessData(image_path)
    image = np.reshape(image, [1, 224, 224, 3])
    image = np.array(image)
    return bi_model.predict(image)


def multiModelPrediction(image_path):
    image = preprocessData(image_path)
    image = np.reshape(image, [1, 224, 224, 3])
    image = np.array(image)
    multi_prediction = multi_model.predict(image)
    return multi_prediction.tolist()


def multiModelTranslate(multiModelPrediction):
    class_names = ['glioma', 'meningioma', 'ptitutary']
    index = np.argmax(multiModelPrediction)
    return class_names[index]


def similar_cases(tumor_type, testimagepath):
    treatment_one = "No more Similar cases"
    treatment_two = "No more Similar cases"
    treatment_three = "No more Similar cases"
    treatment_four = "No more Similar cases"
    treatment_five = "No more Similar cases"

    connection = sql_connection.cursor()
    connection.execute("select imgPath from patient where tumortype= '" + tumor_type + "';")
    cases = connection.fetchall()
    image_list = [testimagepath]
    for row in cases:
        image_list.append(row[0])

    Index(image_list).Start()
    result = SearchImage().get_similar_images(image_path=image_list[0],number_of_images=6)
    image_list = []
    for item in result:
        image_list.append(result[item].lstrip("."))

    print(result)
    context = {'treatment_one': treatment_one,
               'treatment_two': treatment_two,
               'treatment_three': treatment_three,
               'treatment_four': treatment_four,
               'treatment_five': treatment_five,
               'similar_image': image_list
               }
    return context


def preprocessData(ImagePath):
    img = cv2.imread(str(ImagePath))

    img_resized = cv2.resize(img, (224, 224))
    gray = cv2.cvtColor(img_resized, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(gray, 45, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=2)
    outline = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    outline = imutils.grab_contours(outline)
    area = max(outline, key=cv2.contourArea)
    max_left = tuple(area[area[:, :, 0].argmin()][0])
    max_right = tuple(area[area[:, :, 0].argmax()][0])
    max_top = tuple(area[area[:, :, 1].argmin()][0])
    max_bottom = tuple(area[area[:, :, 1].argmax()][0])
    ADD_PIXELS = 0
    final_image = img_resized[max_top[1] - ADD_PIXELS:max_bottom[1] + ADD_PIXELS,
                  max_left[0] - ADD_PIXELS:max_right[0] + ADD_PIXELS].copy()
    final_image = cv2.resize(final_image, (224, 224))
    return final_image
