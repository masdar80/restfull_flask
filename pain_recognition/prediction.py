# %%

# libraries
import cv2
import numpy as np
from PIL import Image
from keras.preprocessing.image import img_to_array
from keras.models import model_from_json

# %%

classifier = model_from_json(open("pain.json", "r").read())
# load weights
classifier.load_weights('pain.h5')
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

class_labels = ['score 0', 'score 1', 'score 2', 'score 3']


# %%
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

    # roi_color = T1
    return roi_color


# %%

def face_analysis_after_Detection(face, result):
    # i = 0
        #roi = face.astype("float") / 255.0
        gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
        roi = cv2.resize(gray, (64, 64), interpolation=cv2.INTER_AREA)
       # roi = cv2.resize(face, (64, 64), interpolation=cv2.INTER_AREA)
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        roi
        # make a prediction on the ROI, then lookup the class
        preds = classifier.predict_classes(roi)
        #print(preds)
        label = class_labels[preds[0]]
        result.append(label)
        return result


# %%

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
        img = img.resize((80, 80), Image.ANTIALIAS)
        face = face_detector(img)
        finalResult.clear()
        print(face)
        print(type(face).__name__)
        if type(face).__name__ == 'ndarray':
            finalResult = face_analysis_after_Detection(face, finalResult)
            # print("hi")
        elif type(face).__name__ != 'ndarray':
            finalResult = face_analysis_without_Detection(path, finalResult)
        # print("hi2")
        return finalResult[0]
        # return finalResult[0]
    except:
        return 4

    # %%



#path = "score 1test/ce32b645-f418-409e-8f1b-2244892aef93.jpeg"
#print(get_prediction_result(path))

# image = cv2.imread('ghena kaisar2.jpg')
# t = []
#result = face_analysis_without_Detection(image, t)
#print(result)