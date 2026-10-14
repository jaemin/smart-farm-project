from flask import Blueprint, render_template, Response
import cv2
import os
from ultralytics import YOLO

cctv_bp = Blueprint(
    "cctv",                # BluePrint 이름
    __name__
)

# 웹페이지에서 보이는 영상 크기 고정
height = 630
width = 1120

red_model = YOLO("yolo_model/tomato_yolov8n.pt")
fire_model = YOLO("yolo_model/best.pt")

original_frame = None
video_flag = False

def video_capture():
    global original_frame

    # 동영상 열기
    video = cv2.VideoCapture(os.getenv("VIDEO_URL"))

    if not video.isOpened() :
        exit()

    while True:
        global video_flag

        ret, cap = video.read()

        if not ret:
            break
        else:
            original_frame = cap.copy()

            detect_red_fruits(cap)
            video_flag = detect_fire(cap)

        result = draw_rect(cap)

        _, buffer = cv2.imencode('.jpg', result)
        
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

# 과실 탐지 범위 저장
red_x1 = []
red_y1 = []
red_x2 = []
red_y2 = []

def detect_red_fruits(frame):

    red_results = red_model.predict(source=frame, imgsz=640, verbose=False, conf=0.5, classes=0, show_labels=False, show_conf = False)

    for box in red_results[0].boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            red_x1.append(x1)
            red_y1.append(y1)
            red_x2.append(x2)
            red_y2.append(y2)

fire_x1 = []
fire_y1 = []
fire_x2 = []
fire_y2 = []
    
# 불꽃탐지센서가 작동할 때 한번 더 확인
def detect_fire(frame):

    fire_results = fire_model.predict(source=frame, imgsz=640, verbose=False, conf=0.1, classes=0, show_labels=False, show_conf = False)

    boxes = fire_results[0].boxes

    for box in fire_results[0].boxes.xyxy:
        x1, y1, x2, y2 = map(int, box)
        fire_x1.append(x1)
        fire_y1.append(y1)
        fire_x2.append(x2)
        fire_y2.append(y2)

    if len(boxes) > 0:          # YOLO로 화재가 검출
        return True
    else:
        return False

def draw_rect(frame):
    for cnt in range(len(fire_x1)):
        cv2.rectangle(frame, (fire_x1[cnt], fire_y1[cnt]), (fire_x2[cnt], fire_y2[cnt]), (0, 0, 255), 2)

    for cnt in range(len(red_x1)):
        cv2.rectangle(frame, (red_x1[cnt], red_y1[cnt]), (red_x2[cnt], red_y2[cnt]), (0, 255, 0), 2)

    # rectangle clear
    red_x1.clear()
    red_y1.clear()
    red_x2.clear()
    red_y2.clear()
    
    fire_x1.clear()
    fire_y1.clear()
    fire_x2.clear()
    fire_y2.clear()

    return frame    

@cctv_bp.route('/camera')
def getCamera():
    return Response(video_capture(), mimetype="multipart/x-mixed-replace; boundary=frame")

# cctv 화면
@cctv_bp.route('/cctv')
def cctv():
    return render_template('cctv.html')

@cctv_bp.route('/original')
def original():
    global original_frame
    _, buffer = cv2.imencode('.jpg', original_frame)
    return Response(buffer.tobytes(), mimetype="image/jpeg")