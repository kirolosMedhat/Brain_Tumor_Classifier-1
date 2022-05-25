import cv2
import imutils
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
import tensorflow as tf
from tensorflow import keras
import numpy as np
import pyodbc
sql_connection = pyodbc.connect('Driver={SQL Server};'
                                'Server=DESKTOP-8A7J2CA;'
                                'Database=Brain_tumor;'
                                'Trusted_Connection=yes;')
bi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                   r'\mlModels\bi_model.h5')

multi_model = keras.models.load_model((os.path.dirname(os.path.dirname(__file__))) +
                                      r'\mlModels\multi_model.h5')
def biModelPrediction(image_path):
    image =preprocessData(image_path)
    image = np.reshape(image, [1, 224, 224, 3])
    image = np.array(image)
    return bi_model.predict(image)

def multiModelPrediction(image_path):
    image =preprocessData(image_path)
    image = np.reshape(image, [1, 224, 224, 3])
    image = np.array(image)
    multi_prediction = multi_model.predict(image)
    return multi_prediction.tolist()

def multiModelTranslate(multiModelPrediction):
    class_names = ['glioma', 'meningioma', 'ptitutary']
    index = np.argmax(multiModelPrediction)
    return class_names[index]

def similar_cases():
    treatment_one = "No more Similar cases"
    treatment_two = "No more Similar cases"
    treatment_three = "No more Similar cases"
    treatment_four = "No more Similar cases"
    treatment_five = "No more Similar cases"

    context = {'treatment_one': treatment_one,
               'treatment_two': treatment_two,
               'treatment_three': treatment_three,
               'treatment_four': treatment_four,
               'treatment_five': treatment_five,
               }

    connection= sql_connection.cursor()
    connection.execute("select paths from patient where tumortype =")
    return

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