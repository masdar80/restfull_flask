# libraries
import cv2
import numpy as np
from PIL import Image
from keras.preprocessing.image import img_to_array
from keras.models import model_from_json


classifier = model_from_json(open("pain.json", "r").read())
# load weights
classifier.load_weights('pain.h5')
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
class_labels = ['0', '1', '2', '3']
global roi_color
def face_detector(img):

    roi_color = []
    faces = []
    # Convert image to grayscale
    image = np.array(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faceCascade1 = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    faceCascade2 = cv2.CascadeClassifier('haarcascade_profileface.xml')

    faces1 = faceCascade1.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)
    check = False
    if type(faces1).__name__ == 'ndarray':
        check = True
        faces = faces1
    else:
        faces1 = faceCascade1.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=4)
        check = False
        if type(faces1).__name__ == 'ndarray':
            check = True
            faces = faces1

    if type(faces1).__name__ != 'ndarray':
        faces2 = faceCascade2.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4)
        check = False
        if type(faces2).__name__ == 'ndarray':
            check = True
            faces = faces2
        else:
            faces2 = faceCascade2.detectMultiScale(gray, scaleFactor=1.01, minNeighbors=4)
            check = False
        if type(faces2).__name__ == 'ndarray':
            check = True
            faces = faces2

    last = 0
    lastFace = []

    for (x, y, w, h) in faces:
        temp = x + y + w + h
        if (last < temp):
            last = temp
            lastFace.clear()
            lastFace.append(x)
            lastFace.append(y)
            lastFace.append(w)
            lastFace.append(h)
            roi_color = []
            roi_color = image[y:lastFace[1] + lastFace[3] + 10, x:lastFace[0] + lastFace[2] + 10]
    return roi_color

def face_analysis_after_Detection(face, result):
       #gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
       # roi = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
        roi = cv2.resize(face, (64, 64), interpolation=cv2.INTER_AREA)
        roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        #roi = roi.flatten().reshape(1, 64, 64, 1)
        #roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        #roi = roi.reshape(1, 64, 64, 1)
        preds = classifier.predict_classes(roi)
        label = class_labels[preds[0]]
        result.append(label)
        return result

def face_analysis_without_Detection(path, result):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    roi = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
    roi = img_to_array(roi)
    roi = np.expand_dims(roi, axis=0)
    preds = classifier.predict_classes(roi)
    label = class_labels[preds[0]]
    result.append(label)
    return result


# %%

def get_prediction_result(path):
    try:
        global finalResult
        finalResult = []
        img = Image.open(path, "r")
        img = img.resize((200,200), Image.ANTIALIAS)
        face = face_detector(img)
        finalResult.clear()
        if type(face).__name__ == 'ndarray':
            finalResult = face_analysis_after_Detection(face, finalResult)
        elif type(face).__name__ != 'ndarray':
          finalResult = face_analysis_without_Detection(path, finalResult)
        return finalResult[0]
    except Exception as error:
        print('Caught this error: ' + repr(error))





#path = "F:/uploads/degree_only/26-03-2021_13-57-18_ba15e5aa-281e-43ca-9e43-a6a3d7b08733146190228196765456.jpg"
# #path="im21.png"
#print(get_prediction_result(path))

