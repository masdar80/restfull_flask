# %%

# libraries
import cv2
import numpy as np
from keras.preprocessing.image import img_to_array
from keras.models import model_from_json

# %%

classifier = model_from_json(open("pain_recognition/fer.json", "r").read())
# load weights
classifier.load_weights('pain_recognition/fer.h5')
face_classifier = cv2.CascadeClassifier('pain_recognition/haarcascade_frontalface_default.xml')

class_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']


# %%

def face_detector(img):
    # Convert image to grayscale
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    # gray = img
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)
    if faces is ():
        return (0, 0, 0, 0), np.zeros((48, 48), np.uint8), img

    allfaces = []
    rects = []
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
        allfaces.append(roi_gray)
        rects.append((x, w, y, h))
    return rects, allfaces, img


# %%

def face_analysis_after_Detection(faces, result):
    # i = 0
    for face in faces:
        roi = face.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)
        roi
        # make a prediction on the ROI, then lookup the class
        preds = classifier.predict_classes(roi)
        print(preds)
        label = class_labels[preds[0]]
        result.append(label)
    return result


# %%

def face_analysis_without_Detection(img, result):
    gray = cv2.cvtColor(img.copy(), cv2.COLOR_BGR2GRAY)
    roi = cv2.resize(gray, (48, 48), interpolation=cv2.INTER_AREA)
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
        img = cv2.imread(path)
        rects, faces, image = face_detector(img)
        finalResult.clear()
        if type(faces).__name__ == 'list':
            finalResult = face_analysis_after_Detection(faces, finalResult)
            # print("hi")
        elif type(faces).__name__ == 'ndarray':
            finalResult = face_analysis_without_Detection(img, finalResult)
        # print("hi2")
        return finalResult[0]
    except:
        return 0


# %%

path = 'F:\\People Faces/Pain2.jpg'
print(get_prediction_result(path))
