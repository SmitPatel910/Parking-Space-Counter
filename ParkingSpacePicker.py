from collections import Counter
import cv2
import pickle
import math
width, height = 107, 48
id_list = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500,510,520,530,540,550,560,570,580,590,600,610,620,630,640,650,660,670,680,690,700,710,720,730,740,750,760,770,780,790,800,810,820,830]

try:
    with open('CarParkPos', 'rb') as f:
        posList = pickle.load(f)
    with open('CarParkPos_id', 'rb') as f:
        id_distance_file = pickle.load(f)
        count = pickle.load(f)
except:
    posList = []
    id_distance_file= []
    count = 0

def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
        global count
        cal_entry_dis = math.sqrt(math.pow(x + (width/2),2) + math.pow(y+ (height/2),2))
        cal_exit_dis = math.sqrt(math.pow(1000 - (x + (width/2)),2) + math.pow(720 - (y+ (height/2)),2))
        cal_indoor_dis = math.sqrt(math.pow(500 - (x + (width/2)),2) + math.pow(500 - (y+ (height/2)),2))
        id_distance_file.append(((x,y),id_list[count], cal_entry_dis, cal_exit_dis, cal_indoor_dis))
        count = count + 1
        # print(id_distance_file) 
        
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)
                id_distance_file.pop(i)
                count = count - 1
    
    with open('CarParkPos', 'wb') as f:
        pickle.dump(posList, f)
    with open('CarParkPos_id', 'wb') as f:
        pickle.dump(id_distance_file,f)
        pickle.dump(count,f)
    
        

while True:
    img = cv2.imread('carParkImg.png')
    for pos in posList:
        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)
    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouseClick)
    cv2.waitKey(1)