from flask import Blueprint, request, render_template, jsonify
from sqlalchemy import select, func
from static.db import engine
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import Session
from models import DeviceLog, Sensor
from datetime import datetime

data_bp = Blueprint(
    "data",                # BluePrint 이름
    __name__
)

# 센서 테이블에서 단위, 주의 범위 가져오기
def readSensor():
    unit_code = []
    value_range = []

    with Session(engine) as db_session:
        sensors = db_session.scalars(select(Sensor).order_by(Sensor.sensor_seq))

        for sensor in sensors:
            # 센서별 단위 저장 
            if sensor.unit_code is None:
                unit_code.append("")
            else:
                unit_code.append(sensor.unit_code)
            # 센서별 주의 범위 저장
            value_range.append(sensor.value_range)

    return unit_code, value_range

# 기간별 로그 
def getData(startDay="interval 7 day", endDay="interval 0 day"):
    with Session(engine) as db_session:
        sensorData = []                 # 평균값, 최솟값, 최댓값
        countList = []                  # 센서의 기간별 로그 갯수
        warnCount = []                  # '주의' 상태 갯수
        dangerCount = []                # '경고' 상태 갯수        
        
        # 각 센서의 기간별 로그 저장
        for sensorseq in range(1, len(nameList) + 1):
            # 기간별 로그 서브쿼리
            period = (
                select(
                    DeviceLog
                ).where(
                    DeviceLog.recorded_at <= func.date_sub(func.now(), text(endDay))
                ).where(
                    DeviceLog.recorded_at >= func.date_sub(func.now(), text(startDay))
                ).where(
                    DeviceLog.sensor_seq == sensorseq
                ).subquery()
            )

            # 기간별 전체 로그 갯수 구하기
            countstmt = db_session.scalar(select(func.count(period.c.log_seq)))
            countList.append(countstmt)

            # 기간별 로그 중 평균값, 최솟값, 최댓값 저장
            valuestmt = (
                select(
                    func.avg(period.c.device_value).label("avg"),
                    func.min(period.c.device_value).label("min"),
                    func.max(period.c.device_value).label("max")
                )
            )
            values = db_session.execute(valuestmt)

            for value in values:
                sensorData.append([i for i in value])

            # 기간별 '주의' 상태 횟수 구하기
            warnstmt = (
                select(
                    func.count(period.c.log_seq)
                ).where(
                    ((period.c.min <= period.c.device_value) &
                    (period.c.device_value <= (period.c.min + value_range[sensorseq - 1]))) |
                    (((period.c.max - value_range[sensorseq - 1]) <= period.c.device_value) &
                    (period.c.device_value <= period.c.max))
                )
            )
            warns = db_session.execute(warnstmt)

            for warn in warns:
                warnCount.append(warn[0])

            # 기간별 '경고' 상태 횟수 구하기
            dangerstmt = (
                select(
                    func.count(period.c.log_seq)
                ).where(
                    (period.c.device_value < period.c.min) |
                    (period.c.max < period.c.device_value)
                )
            )
            dangers = db_session.execute(dangerstmt)

            for danger in dangers:
                dangerCount.append(danger[0])

    # 출력값
    stats_data = []

    for i in range(7):
        if countList[i] == 0:
            msg = "-"

            stats_data.append({
                "name" : nameList[i],
                "avg" : msg,
                "min" : msg,
                "max" : msg,
                "rate" : msg,
                "warn" : str(warnCount[i]) + "회",
                "danger" : str(dangerCount[i]) + "회"
            })
        else:
            rate = round((countList[i] - warnCount[i] - dangerCount[i]) / countList[i] * 100, 2)

            stats_data.append({
                "name" : nameList[i],
                "avg" : str(round(sensorData[i][0], 2)) + " " + unit_code[i],
                "min" : str(round(sensorData[i][1], 2)) + " " + unit_code[i],
                "max" : str(round(sensorData[i][2], 2)) + " " + unit_code[i],
                "rate" : str(rate) + "%",
                "warn" : str(warnCount[i]) + "회",
                "danger" : str(dangerCount[i]) + "회"
            })

    return stats_data

nameList = ['온도', '습도', '조도', '수온', '유량', 'pH', 'TDS']
unit_code, value_range = readSensor()

@data_bp.route('/data')
def data():
    stats_data = getData()

    return render_template('data.html', stats=stats_data)

@data_bp.post("/data-system")
def data_system():
    data = request.get_json()['day']

    if data == 7:
        stats_data = getData(startDay="interval 7 day")
    else:
        stats_data = getData(startDay="interval 30 day")

    return jsonify({"stats_data": stats_data})

@data_bp.post("/data-user")
def data_user():
    start = request.get_json()['start']
    end = request.get_json()['end']

    today = datetime.now()
    startdate = datetime.strptime(start, "%Y%m%d")
    enddate = datetime.strptime(end, "%Y%m%d")

    startday = "interval " + str((today - startdate).days) + " day"
    endday = "interval " + str((today - enddate).days) + " day"
    
    stats_data = getData(startday, endday)

    return jsonify({"stats_data": stats_data})