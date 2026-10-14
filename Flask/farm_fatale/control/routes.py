from flask import Blueprint, render_template
from sqlalchemy import select, func
from static.db import engine
from sqlalchemy.orm import Session
from models import AutoControl, ManualControl

control_bp = Blueprint(
    "control",                # BluePrint 이름
    __name__
)

@control_bp.route("/control_mode")
def control_mode():
    with Session(engine) as db_session:
        # 액추에이터 제어모드 자동 수동, 가장 최근 데이터만 추출
        # 자동모드
        autoList = (
            select(
                AutoControl.device_seq, 
                func.max(AutoControl.recorded_at).label('recorded_at')
            )
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

    actuator_status = {}
    actuatorList = ['fan', 'curtain', 'led']
    for i in range(len(actuatorList)):

        if actuator[i]['actuator_state'] == 0:
            actuator[i]['actuator_state'] = 'OFF'
        else:
            actuator[i]['actuator_state'] = 'ON'

        actuator_status[actuatorList[i]] = {
            "current": actuator[i]['actuator_state'],
            "is_auto": actuator[i]['control_mode']
        }

    return render_template("control_mode.html", actuators=actuator_status)