from django.shortcuts import render
import numpy as np
from django.core.files.storage import FileSystemStorage
from mainApp import Driver
from mainApp.Ailib import Predictions


def Login(request):
    # load login page
    if request.method == "GET":
        return render(request, 'Login/index.html')
    # register before login
    return Driver.Register(request)


def Home(request):
    # load Home page
    if request.method == "GET":
        return render(request, 'Home/home.html')
    # register after wrong login
    if 'signup' in request.POST:
        return Driver.Register(request)
    # login
    elif 'signin' in request.POST:
        return Driver.Login(request)
    return render(request, 'Login/index.html')


def user(request):
    return render(request, 'Login/index.html')


def Result(request):
    # load result page
    if request.method == 'GET':
        return render(request, 'Result/result.html')

    flag = False
    context={'flag': flag}
    # saving img
    fileObj = request.FILES['imgPath']
    fs = FileSystemStorage()
    testImgPath = fs.save(fileObj.name, fileObj)
    testImgPath = fs.url(testImgPath)  # for server use
    testimagepath = '.' + testImgPath  # for pc
    # start preditions
    bi_prediction = Predictions.biModelPrediction(testimagepath)
    # set default values
    multi_prediction = [0.00, 0.00, 0.00]
    multi_prediction_txt = "No tumor"
    if np.argmax(bi_prediction) == 1:
        flag = True  # not finished yet
        multi_prediction = Predictions.multiModelPrediction(image_path=testimagepath)
        multi_prediction_txt = Predictions.multiModelTranslate(multi_prediction)
        context.update(Driver.similar_cases(multi_prediction_txt, testimagepath))
        # insert new patient
    Driver.insertNewPatient(request, testimagepath, multi_prediction_txt)
    context.update( {'testImgPath': testImgPath,
               'bi_prediction': round(float(bi_prediction[0,1]) * 100, 3),
               'multi_prediction': multi_prediction[0],
               'multi_prediction_txt': multi_prediction_txt,
               'flag': flag
               })

    return render(request, 'Result/result.html', context)


def New(request):
    return render(request, 'New-patiant/patiant.html')


def Search(request):
    return Driver.Search(request)
