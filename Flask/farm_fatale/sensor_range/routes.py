from flask import Blueprint, request, render_template, jsonify, session
from sqlalchemy import select, func
from static.db import engine
from sqlalchemy.orm import Session
from models import DeviceLog, AdminValue, Control
from datetime import datetime
from data.routes import readSensor
import websock

sensor_range_bp = Blueprint(
    "sensor_range",                # BluePrint 이름
    __name__
)

@sensor_range_bp.route("/sensor_range")
def sensor_range():
    with Session(engine) as db_session:
        user_seq = session.get("user_seq")

        # 센서별 단위 저장
        unit_code, _ = readSensor()

        # 현재 상태, 가장 최근 데이터만 추출
        logList = (
            select(
                DeviceLog.sensor_seq, 
                func.max(DeviceLog.recorded_at).label('recorded_at')
            ).group_by(
                DeviceLog.sensor_seq
            ).subquery()
        )

        logstmt = (
            select(
                DeviceLog.sensor_seq, 
                DeviceLog.device_value
            ).join(
                logList,
                (DeviceLog.sensor_seq == logList.c.sensor_seq) &
                (DeviceLog.recorded_at == logList.c.recorded_at)
            ).order_by(
                DeviceLog.sensor_seq
            )
        )

        logResult = db_session.execute(logstmt)

        device_log = []
        for result in logResult:
            device_log.append({
                "sensor_seq": result[0],
                "device_value": result[1]
            })
        
        # 설정범위/값 : min, max
        valueList = (
            select(
                AdminValue.sensor_seq, 
                func.max(AdminValue.recorded_at).label('recorded_at')
            ).group_by(
                AdminValue.sensor_seq
            ).subquery()
        )

        valuestmt = (
            select(
                AdminValue.sensor_seq, 
                AdminValue.min,
                AdminValue.max
            ).join(
                valueList,
                (AdminValue.sensor_seq == valueList.c.sensor_seq) &
                (AdminValue.recorded_at == valueList.c.recorded_at)
            ).order_by(
                AdminValue.sensor_seq
            )
        )
        
        valueResult = db_session.execute(valuestmt)

        admin_value = []
        for result in valueResult:
            admin_value.append({
                "sensor_seq": result[0],
                "min": result[1],
                "max": result[2]
            })

    control_mode_data = {}
    sensorList = ['temp', 'humidity', 'lux', 'water_temp', 'flow', 'ph', 'tds']

    for i in range(len(sensorList)):
        if unit_code[i] is None:
            unit_code[i] = ""
            
        control_mode_data[sensorList[i]] = {
            "current": str(device_log[i]['device_value']) + " " + unit_code[i],
            "min": admin_value[i]['min'],
            "max": admin_value[i]['max']
        }

    return render_template("sensor_range.html", sensors=control_mode_data)


# 설정범위 저장
@sensor_range_bp.post("/save-range")
def saveControl():
    sessionUser = session.get("user_seq")
    data = request.get_json()

    maxList = []
    minList = []

    maxList = data['max']
    minList = data['min']

    with Session(engine) as db_session:
        msg = ""
        for i in range(len(maxList)):
            # control DB에 자동인지 수동인지 센서의 상태 저장
            control = Control(
                sensor_seq = i + 1,
                control_mode = 1,
                recorded_at = datetime.now()
            )
            db_session.add(control)
            db_session.commit()

            # admin_value에 변경된 최적값 저장
            adminValue = AdminValue(
                user_seq = sessionUser,
                sensor_seq = i + 1,
                min = minList[i],
                max = maxList[i],
                recorded_at = datetime.now()
            )
            db_session.add(adminValue)
            db_session.commit()
            if i < 3:
                msg += "s&" + str(i + 1) + "&" + str(minList[i]) + "&" + str(maxList[i]) + "$"

    if websock.web_socket:
        websock.web_socket.send(msg)
        print(msg)


    return jsonify({
        "result" : "success"
    })

# 기본값 복원
@sensor_range_bp.post("/reset-range")
def resetControl():

    msg = ""

    with Session(engine) as db_session:
        initList = (
            select(
                func.min(AdminValue.admin_seq).label('admin_seq')
            )
            .where(AdminValue.user_seq == 1)        # 관리자 아이디 시퀀스 1번
            .where(AdminValue.sensor_seq < 8)
            .group_by(AdminValue.sensor_seq)
            .subquery()
        )

        valuestmt = (
            select(AdminValue.sensor_seq, AdminValue.min, AdminValue.max)
            .join(
                initList,
                (AdminValue.admin_seq == initList.c.admin_seq)
            )
            .order_by(AdminValue.sensor_seq)
        )

        valueResult = db_session.execute(valuestmt)
                
        initValue = []
        for result in valueResult:
            initValue.append({
                "sensor_seq": result[0],
                "min": result[1],
                "max": result[2]
            })

    return jsonify({
        "result" : "success",
        "init" : initValue
    })