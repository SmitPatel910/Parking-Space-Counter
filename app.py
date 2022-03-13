from flask import Flask, render_template, request, Response
import cv2
import pickle
import cvzone
import numpy as np
import array as ar
import time 

app = Flask(__name__, static_folder='static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

width, height = 107, 48

#  Three Dictionaries to store Ids and three different distances
Dict = {} # Id and Entrance Distance 
Dict2 = {} # Id and Exit Distance
Dict3 = {} # Id and Indoor Distance 

# Three id and Distance variable to print Id and Distance from Dictionary.
id_fetch = 0
id_fetch2 = 0
id_fetch3 = 0
entry_dis_fetch = 0
exit_dis_fetch = 0
indoor_dis_fetch = 0

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)
with open('CarParkPos_id', 'rb') as f:
    id_distance_file = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/after', methods=['GET', 'POST'])

def after():
    cap = cv2.VideoCapture('./static/carPark.mp4')
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def checkParkingSpace(imgPro,img):
    spaceCounter=0
    for i in range(len(id_distance_file)):
        for j in range(len(id_distance_file[0])):
            if(j==0):
                x, y = id_distance_file[i][j]    
                imgCrop = imgPro[y:y + height, x:x + width]
                count = cv2.countNonZero(imgCrop)
                if count < 900:
                    color = (0, 255, 0)
                    thickness = 5
                    spaceCounter += 1
                    Dict[id_distance_file[i][1]] = (id_distance_file[i][2])
                else:
                    color = (0, 0, 255)
                    thickness = 2
                    if id_distance_file[i][2] in Dict.values():
                        del Dict[id_distance_file[i][1]]
                    
                    # Sort these three Dictionaries to get minimum Distance
                    sort_Dict = sorted(Dict.items(), key=lambda x: x[1])
                    Dict_keys = list(sort_Dict)

                    if(len(Dict_keys)!=0):
                        global id_fetch, entry_dis_fetch
                        id_fetch, entry_dis_fetch = Dict_keys[0]

                cvzone.putTextRect(img, "1", (5,20), scale=2, thickness=2, offset=2, colorR=(255,0,0))

                cv2.rectangle(img, id_distance_file[i][j], (x + width, y + height), color, thickness)    
                cvzone.putTextRect(img, str(id_distance_file[i][1]), (x + width - 70, y + height - 15), scale=1.4, thickness=4, offset=0, colorR=color)
            
            cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)} ',  (100, 50), scale=2, thickness=4, offset=20, colorR=(0,200,0))
            cvzone.putTextRect(img, f'Entry: {id_fetch} , {"{0:.2f}".format(entry_dis_fetch)}',  (350, 50), scale=2, thickness=4, offset=20, colorR=(0,200,0))
            
# generate frame by frame from camera
def gen_frames():  
    cap = cv2.VideoCapture('./static/carPark.mp4')
    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        if not success:
            break
        else:
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV, 25, 16)
            imgMedian = cv2.medianBlur(imgThreshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
            checkParkingSpace(imgDilate,img)
            cv2.waitKey(10)
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

   
    


if __name__ == "__main__":
    app.run()


