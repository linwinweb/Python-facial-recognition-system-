import sys
import cv2
import numpy as np
import face_recognition
import os
import pyautogui
import filetype
from playsound import playsound
from datetime import datetime
#               TBD
# - Make a timer for each user register and fix debug mode.
# - Cleanup libraries.
# - Remove console output or make it optional.

sys.stdout = open(os.devnull, "w")
sys.stderr = open(os.devnull, "w")

path = 'Images'
images = []
classNames = []
if not os.path.exists(path):
    os.makedirs(path)
myList = os.listdir(path)
c = 0
print('[INFO] - Started process...')

def mark(name):
    name = name.upper()
    with open("register.csv", 'a') as f:
        now = datetime.now()
        dtstring = now.strftime('%H:%M:%S')
        datestring = now.strftime('%d/%m/%y')
        usrconf = pyautogui.confirm('Insert register for {}?'.format(name),
                                 buttons=['Yes', 'No'])
        if usrconf == 'Yes':
            classtype = pyautogui.confirm('Please select a register type:',
                                          buttons=['Entry', 'Exit'])
            resp = pyautogui.confirm(
                'Mark register?\n\nName: {}\nTime: {} \nDate: {}\n\nType: {}'.format(name, dtstring,
                                                                                               datestring, classtype),
                'Confirmation', buttons=['Yes', 'No'])
            if resp == 'Yes':
                now = datetime.now()
                dtstring = now.strftime('%H:%M:%S')
                datestring = now.strftime('%d/%m/20%y')
                f.writelines(f'\n{name},{dtstring},{datestring},{classtype}')
                f.close()
                playsound('success.wav')
                pyautogui.alert('System registered {} successfully.'.format(name))
                msgdef()
            else:
                f.close()
                msgdef()
        else:
            f.close()
            msgdef()

#WORK IN PROGRESS
def imgcap():
    name = pyautogui.prompt('Insert name:')
    if name is None:
        msgdef()
    else: 
        cam = cv2.VideoCapture(0)
        s, img = cam.read()
        if s:
            cv2.imshow(" ", img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            cv2.imwrite("{}.png".format(name), img)
            msgdef()

def msgdef():
    vmsgd = pyautogui.confirm('Registry system', buttons=['Automatic registration', 'Manual registration', 'Quit', 'DEBUG'])
    if vmsgd == 'Quit':
        sys.exit()
    if vmsgd == 'Manual registration':
        manual()
        #  V do this with a working webcam
    if vmsgd == 'DEBUG':
        pyautogui.alert('NOTE: WORK IN PROGRESS')
        svimg = cv2.VideoCapture(0)
        cv2.imwrite("output.vif", svimg)
        msgdef()
def manual():
    name = pyautogui.prompt('Insert name:')
    if name is None:
        msgdef()
    mark(name)

for cl in myList:
    curImg = cv2.imread('{}/{}'.format(path, cl))
    try:
        cl.encode('ascii')
    except UnicodeEncodeError:
        print(
            '[ERROR] - Image "{}" failed to load.'
            '.'.format(cl))
    else:
        if filetype.is_image('{}/{}'.format(path, cl)):
            print('[INFO] - Image "{}" loaded.'.format(cl))
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        else:
            print(
                '[ERRO] - Image "{}" failed to load.'.format(
                    cl))


def findencodings(images):
    encodelist = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist


print('[INFO] - Processing images...')
if len(images) == 0:
    playsound('error.wav')
    pyautogui.alert(
        'No images detected. Please verify you have at least 1 valid image, and rerun the program.'.format(
            path),
        'ERROR', button='Quit')
    sys.exit()
encodeListKnown = findencodings(images)
cap = cv2.VideoCapture(0)
print('[INFO] - Done.')
msgdef()
while True:
    c += 1
    #if c == 200:
     #   cv2.destroyAllWindows()
     #   timeout = pyautogui.confirm('Não foi possível detetar qualquer rosto.\n\nRegistar novamente a assiduidade. ', buttons=['Reiniciar', 'Registo manual', 'Cancelar'])
     #   if timeout == 'Registo manual':
     #       manual()
     #   if timeout == 'Cancelar':
     #       msgdef()
     #   c = 0
    success, img = cap.read()
    cv2.imshow(None, img)
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex]
            cv2.destroyAllWindows()
            mark(name)
    cv2.waitKey(1)
