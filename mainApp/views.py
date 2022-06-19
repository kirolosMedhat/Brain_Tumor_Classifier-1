from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from mainApp import Driver


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
    flag = True  # not finished yet
    # saving img
    fileObj = request.FILES['imgPath']
    fs = FileSystemStorage()
    testImgPath = fs.save(fileObj.name, fileObj)
    testImgPath = fs.url(testImgPath)
    testimagepath = '.' + testImgPath
    # insert new patient
    Driver.insertNewPatient(request, testimagepath)
    # start preditions
    bi_prediction = Driver.biModelPrediction(testimagepath)
    # set default values
    multi_prediction = [0.00, 0.00, 0.00]
    multi_prediction_txt = "No tumor"
    if bi_prediction > 0.005:
        multi_prediction = Driver.multiModelPrediction(testimagepath)
        multi_prediction_txt = Driver.multiModelTranslate(multi_prediction)
    context = {'testImgPath': testImgPath,
               'bi_prediction': round(float(bi_prediction[0]) * 100, 3),
               'multi_prediction': multi_prediction[0],
               'multi_prediction_txt': multi_prediction_txt,
               'flag':flag
               }
    return render(request, 'Result/result.html', context)


def New(request):
    return render(request, 'New-patiant/patiant.html')


def Search(request):
    return Driver.Search(request)
