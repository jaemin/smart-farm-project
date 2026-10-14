from static.db import engine
from sqlalchemy.orm import Session
from flask_sock import Sock
from sqlalchemy import select, func
from models import DeviceLog, AdminValue, AutoControl, ManualControl
from datetime import datetime
import cctv.routes

sock = Sock()

web_socket = None
db_flag = False
fire_value = 0
clients = set()

@sock.route("/ws")
def websocket(ws):
    global web_socket, db_flag, fire_value

    web_socket = ws

    print("ESP32 WebSocket connected")

    while True:
        data = ws.receive()
        if data is None:
            print("ESP32 disconnected")
            break

        print("[ESP32 → Flask] ", data)

        # 센서 데이터의 전송
        if data[:6] == "sensor":
            insertValue(data)
            datalist = data.split('&')
            sensor = datalist[0].split('=')[1]

            if sensor == "FLAM":
                # 화재 플래그 갱신
                with Session(engine) as db_session:
                    stmt = (
                        select(DeviceLog)
                        .where(DeviceLog.sensor_seq == 8)
                        .order_by(DeviceLog.log_seq.desc())
                        .limit(1)
                    )
            
                    fire = db_session.scalar(stmt)
            
                    if fire.min < fire.device_value:
                        db_flag = False
                    else:
                        db_flag = True
                        
                    if ws:
                        if db_flag and cctv.routes.video_flag:
                            print("fire flag on")
                            if fire_value == 0:
                                print("fire flag off->on 갱신")
                                fire_value = 1
                                msg = "a&13&1$"
                                ws.send(msg)
    
                                auto_con = AutoControl(
                                    sensor_seq = 8,
                                    device_seq = 13,
                                    actuator_state = 1,
                                    recorded_at = datetime.now()
                                )
                                db_session.add(auto_con)
                                db_session.commit()
    
                        else:
                            print("fire flag off")
                            if fire_value == 1:
                                print("fire flag on->off 갱신")
                                fire_value = 0
                                msg = "a&13&0$"
                                ws.send(msg)
    
                                auto_con = AutoControl(
                                    sensor_seq = 8,
                                    device_seq = 13,
                                    actuator_state = 0,
                                    recorded_at = datetime.now()
                                )
                                db_session.add(auto_con)
                                db_session.commit()

        # STM32로부터 액추에이터 및 설정범위 상태 요청
        else:
            actuatorList = sendActuator()
            rangeList = sensorRange()
                        
            if ws:
                msg = ""
                for i in range(len(actuatorList)):
                    msg += "a&" + str(actuatorList[i]['device_seq']) + "&" + str(actuatorList[i]['actuator_state']) + "$"
                
                print("[Flask -> ESP32] Actuator State Send")                

                for i in range(len(rangeList)):
                    msg += "s&" + str(rangeList[i]['sensor_seq']) + "&" + str(rangeList[i]['min']) + "&" + str(rangeList[i]['max']) + "$"
                print("[Flask -> ESP32] Sensor Range Send")

                ws.send(msg)

def insertValue(recvData):
    recvData = str(recvData)
    datalist = recvData.split('&')
    sensor = datalist[0].split('=')[1]
    value = datalist[1].split('=')[1]

    with Session(engine) as db_session:
        if sensor == 'TEMP':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 1)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )
            
            devicelog = DeviceLog(
                sensor_seq = 1,
                device_value = float(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )
            
            db_session.add(devicelog)
            db_session.commit()

        elif sensor == 'HUMI':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 2)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )
            
            devicelog = DeviceLog(
                sensor_seq = 2,
                device_value = int(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )
            
            db_session.add(devicelog)
            db_session.commit()

        elif sensor == 'LUXV':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 3)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )
            
            devicelog = DeviceLog(
                sensor_seq = 3,
                device_value = int(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )
            
            db_session.add(devicelog)
            db_session.commit()

        elif sensor == 'WATP':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 4)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 4,
                device_value = float(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()
        elif sensor == 'FLOW':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 5)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 5,
                device_value = float(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()
        elif sensor == 'PHVL':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 6)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 6,
                device_value = float(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()
        elif sensor == 'TDSV':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 7)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 7,
                device_value = int(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()
        elif sensor == 'FLAM':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 8)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 8,
                device_value = float(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()
        elif sensor == 'GASD':
            result = db_session.scalar(
                select(AdminValue)
                .where(AdminValue.sensor_seq == 9)
                .order_by(AdminValue.admin_seq.desc())
                .limit(1)
            )

            devicelog = DeviceLog(
                sensor_seq = 9,
                device_value = int(value),
                min = result.min,
                max = result.max,
                recorded_at = datetime.now()
            )

            db_session.add(devicelog)
            db_session.commit()

        elif sensor == 'FAN_':
            sensor = value.split(',')[0]
            value = value.split(',')[1]

            auto_con = AutoControl(
                sensor_seq = sensor,
                device_seq = 9,
                actuator_state = value,
                recorded_at = datetime.now()
            )

            db_session.add(auto_con)
            db_session.commit() 

        elif sensor == 'CURT':
            sensor = value.split(',')[0]
            value = value.split(',')[1]

            auto_con = AutoControl(
                sensor_seq = sensor,
                device_seq = 10,
                actuator_state = value,
                recorded_at = datetime.now()
            )

            db_session.add(auto_con)
            db_session.commit() 

        elif sensor == 'LED_':
            sensor = value.split(',')[0]
            value = value.split(',')[1]

            auto_con = AutoControl(
                sensor_seq = sensor,
                device_seq = 11,
                actuator_state = value,
                recorded_at = datetime.now()
            )

            db_session.add(auto_con)
            db_session.commit()

        elif sensor == 'PUMP':
            sensor = value.split(',')[0]
            value = value.split(',')[1]

            auto_con = AutoControl(
                sensor_seq = sensor,
                device_seq = 12,
                actuator_state = value,
                recorded_at = datetime.now()
            )

            db_session.add(auto_con)
            db_session.commit()

def sendActuator():
    with Session(engine) as db_session:
        # 자동모드
        autoList = (
            select(
                AutoControl.device_seq, 
                func.max(AutoControl.recorded_at).label('recorded_at')
            )
            .where(AutoControl.device_seq != 10)
            .group_by(AutoControl.device_seq)
            .subquery()
        )
        autostmt = (
            select(
                AutoControl.device_seq,
                AutoControl.actuator_state,
                AutoControl.recorded_at
            )
            .join(
                autoList,
                (AutoControl.device_seq == autoList.c.device_seq) &
                (AutoControl.recorded_at == autoList.c.recorded_at)
            )
            .order_by(AutoControl.device_seq)
        )

        autoResult = db_session.execute(autostmt)
                
        auto = []
        for result in autoResult:
            auto.append({
                "device_seq": result[0],
                "actuator_state": result[1],
                "recorded_at": result[2]
            })

        # 수동모드
        manuList = (
            select(
                ManualControl.device_seq, 
                func.max(ManualControl.recorded_at).label('recorded_at')
            )
            .where(ManualControl.device_seq != 10)
            .group_by(ManualControl.device_seq)
            .subquery()
        )
        manustmt = (
            select(
                ManualControl.device_seq,
                ManualControl.actuator_state,
                ManualControl.recorded_at
            )
            .join(
                manuList,
                (ManualControl.device_seq == manuList.c.device_seq) &
                (ManualControl.recorded_at == manuList.c.recorded_at)
            )
            .order_by(ManualControl.device_seq)
        )

        manuResult = db_session.execute(manustmt)
                
        manu = []
        for result in manuResult:
            manu.append({
                "device_seq": result[0],
                "actuator_state": result[1],
                "recorded_at": result[2]
            })

        actuator = {}
        totalList = []
        
        for m in manu:
            m['control_mode'] = 0
            totalList.append(m)

        for a in auto:
            a['control_mode'] = 1
            totalList.append(a)

        for total in totalList:
            device_seq = total['device_seq']

            if device_seq not in actuator or total['recorded_at'] > actuator[device_seq]['recorded_at']:
                actuator[device_seq] = total

        actuator = list(actuator.values())
    return actuator

def sensorRange():
    initValue = []

    with Session(engine) as db_session:
        latestList = (
            select(
                func.max(AdminValue.admin_seq).label('admin_seq')
            )
            .where(AdminValue.sensor_seq < 4)
            .group_by(AdminValue.sensor_seq)
            .subquery()
        )

        valuestmt = (
            select(AdminValue.sensor_seq, AdminValue.min, AdminValue.max)
            .join(
                latestList,
                (AdminValue.admin_seq == latestList.c.admin_seq)
            )
            .order_by(AdminValue.sensor_seq)
        )

        valueResult = db_session.execute(valuestmt)
        
        for result in valueResult:
            initValue.append({
                "sensor_seq": result[0],
                "min": result[1],
                "max": result[2]
            })

    return initValue