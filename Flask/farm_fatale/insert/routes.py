from flask import Blueprint, request, abort, session
import os
from dotenv import load_dotenv
from static.db import engine
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import DeviceLog, AdminValue
from datetime import datetime

load_dotenv()

insert_bp = Blueprint(
    "insert",                # BluePrint 이름
    __name__
)

access_api = os.getenv("API")

@insert_bp.post('/insertValue')
def insertValue():
    sensor = request.form["sensor"]
    value = request.form["value"]
    api = request.form["api"]

    user_seq = session.get("user_seq")

    with Session(engine) as db_session:
        if api == access_api:
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
            else:
                abort(404)
            
            return "OK", 200
        
        else:
            abort(404)