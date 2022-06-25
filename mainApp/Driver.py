"""This class is specific to database operations."""
from django.shortcuts import render
import pyodbc
from mainApp.Ailib import Index,SearchImage
from mainApp.models import insertnewpatient, insertdata

# start sql connection
sql_connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=DESKTOP-8A7J2CA;'
                                'Database=Brain_tumor;'
                                'Trusted_Connection=yes;')
connection = sql_connection.cursor()


def Register(request):
    request.POST.get('doctorname') and request.POST.get('password')
    insertvalues = insertdata()
    insertvalues.doctorname = request.POST.get('doctorname')
    insertvalues.password = request.POST.get('password')
    insertvalues.save()
    connection.execute("insert into Doctor values ('" + insertvalues.doctorname + "','" + insertvalues.password + "')")
    doctor_id = connection.execute("select doctorID from doctor where doctorID = (select MAX(doctorID)from doctor) ").fetchone()
    connection.commit()
    return render(request, 'Login/index.html',{'doctor_id':doctor_id,'id_alert':True})


def Login(request):
    data = request.POST
    for key, value in data.items():
        sql_command = "SELECT doctorID, password from Doctor where doctorID='" + request.POST.get(
            "auth_name") + "'and password=" + "'" + request.POST.get("pswd") + "';"
        connection.execute(sql_command)
        result = tuple(connection.fetchall())
        if result == ():
            return render(request, 'Login/index.html',{'login_alert':True}) # login error alert will show up if true
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


    result = connection.execute(
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

def similar_cases(tumor_type, testimagepath):
    treatment_one = "No more Similar cases"
    treatment_two = "No more Similar cases"
    treatment_three = "No more Similar cases"
    treatment_four = "No more Similar cases"
    treatment_five = "No more Similar cases"
    context = {'treatment_one': treatment_one,
               'treatment_two': treatment_two,
               'treatment_three': treatment_three,
               'treatment_four': treatment_four,
               'treatment_five': treatment_five}

    connection.execute("select imgPath from patient where tumortype= '" + tumor_type + "';")
    cases = connection.fetchall()
    image_list = [testimagepath]
    for row in cases:
        image_list.append(row[0])

    Index(image_list).Start()
    result = SearchImage().get_similar_images(image_path=image_list[0],number_of_images=6)
    image_list = []
    result.pop(0) # pop the test image from dic.
    for item,key in zip(result,context):
        context[key] =connection.execute( "select PatientID, age, gender, diabetic, bloodpressure, heartdiseases, "
                                          "prescriptions from patient Where imgPath = '"+result[item]+"'").fetchone()
        image_list.append(result[item].lstrip("."))

    print(result)
    context.update({'similar_image': image_list })# in result start count from 1
    return context



