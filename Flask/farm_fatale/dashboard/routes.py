from flask import Blueprint, request, render_template, jsonify, Response, session
from sqlalchemy import text
from static.db import engine
from sqlalchemy.orm import Session
from datetime import datetime
import csv
import io
from data.routes import readSensor
from sqlalchemy import select, func
from models import Sensor, AutoControl, ManualControl
import websock
import cctv.routes

dashboard_bp = Blueprint(
    "dashboard",                # BluePrint 이름
    __name__
)

# 최적 범위
def evaluate_status(val, min_v, max_v, range):

    if min_v <= val <= max_v:
        if (val <= min_v + range) or (val >= max_v - range):
            return (
                "주의",
                "warning",
                "수치가 최적 범위 경계에 가까워 주의가 필요합니다.",
            )
        return "양호", "good", "현재 수치는 적정 범위 내에 있습니다."
    else:
        return "경고", "danger", "적정 범위를 이탈했습니다."

def readRange():
    sensor_range = []

    with Session(engine) as db_session:
        rangeResult = db_session.execute(select(Sensor.value_range))
    
        for result in rangeResult:
            sensor_range.append(result[0])
    return sensor_range

sensor_list = ["temp", "humid", "light", "watertemp", "flow", "ph", "TDS", "fire"]

@dashboard_bp.route("/dashboard")
def dashboard():

    sensor_map = {}
    sensors_data = {}

    unit_code, _ = readSensor()
    sensor_range = readRange()   
    
    with Session(engine) as db_session:
        for i in range(len(sensor_list)):
            sensor_map[sensor_list[i]] = {"seq": i + 1, "unit": unit_code[i], "is_int": False, "range_v": sensor_range[i]}
      
        for key, info in sensor_map.items():
            query = text("""
                SELECT device_value, min, max 
                FROM device_log 
                WHERE sensor_seq = :seq 
                ORDER BY recorded_at DESC LIMIT 1
            """)
            row = db_session.execute(query, {"seq": info["seq"]}).fetchone()

            if row:
                val = float(row.device_value)
                min_v = float(row.min)
                max_v = float(row.max)
                range_v = float(info["range_v"])

                # 양호/주의/경고 판별
                label, status, _ = evaluate_status(val, min_v, max_v, range_v)

                if info["is_int"]:
                    val_display = int(round(val))
                    min_display = int(min_v)
                    max_display = int(max_v)
                else:
                    val_display = val
                    min_display = min_v
                    max_display = max_v

                sensors_data[key] = {
                    "value": val_display,
                    "unit": info["unit"],
                    "min": min_v - 5 if min_v > 5 else 0,
                    "max": max_v + 10,
                    "opt_min": min_display,
                    "opt_max": max_display,
                    "status": status,  # 'good', 'warning', 'danger'
                    "label": label,  # '양호', '주의', '경고'
                }
            else:
                sensors_data[key] = {
                    "value": 0,
                    "unit": info["unit"],
                    "min": 0,
                    "max": 100,
                    "opt_min": 0,
                    "opt_max": 0,
                    "status": "good",
                    "label": "미수신",
                }

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

    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html", sensors=sensors_data, update_time=now_time, actuators=actuator_status, video_flag=cctv.routes.video_flag
    )

# -------------------------------------------------------------
# 2. 환경 센서
@dashboard_bp.route("/temp")
def temp():
    return render_template("s_temp.html")

@dashboard_bp.route("/humid")
def humid():
    return render_template("s_humid.html")

@dashboard_bp.route("/light")
def light():
    return render_template("s_light.html")

@dashboard_bp.route("/watertemp")
def watertemp():
    return render_template("s_watertemp.html")

@dashboard_bp.route("/flow")
def flow():
    return render_template("s_flow.html")

@dashboard_bp.route("/ph")
def ph():
    return render_template("s_ph.html")

@dashboard_bp.route("/tds")
def tds():
    return render_template("s_tds.html")

# -------------------------------------------------------------
# 3. 센서 데이터 API (s_*.html JS Fetch)
@dashboard_bp.route("/api/sensor/<int:sensor_seq>/data")
def get_sensor_data(sensor_seq):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    sensor_range = readRange()

    with Session(engine) as session:
        query = text("""
                SELECT device_value, min, max, recorded_at 
                FROM device_log 
                WHERE sensor_seq = :seq and
                recorded_at > date_sub(now(), interval 24 hour)
                ORDER BY recorded_at DESC
            """)
        result = session.execute(query, {"seq": sensor_seq}).fetchall()

    all_logs = []

    for row in result:
        val = float(row.device_value)
        min_v = float(row.min)
        max_v = float(row.max)

        # 공통 판별 함수 적용
        status_label, status_class, desc = evaluate_status(val, min_v, max_v, float(sensor_range[sensor_seq - 1]))

        all_logs.append({
            "recorded_at": row.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "time_short": row.recorded_at.strftime("%H:%M"),
            "value": val,
            "min": min_v,
            "max": max_v,
            "status": status_label,  # '양호', '주의', '경고'
            "status_class": status_class,  # 'good', 'warning', 'danger'
            "desc": desc,
        })

    chart_source = list(reversed(all_logs[:25]))
    chart_labels = [item["time_short"] for item in chart_source]
    chart_values = [item["value"] for item in chart_source]
    min_limit = chart_source[0]["min"] if chart_source else 0
    max_limit = chart_source[0]["max"] if chart_source else 100

    current_info = all_logs[0] if all_logs else {}

    total_count = len(all_logs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_table = all_logs[start_idx:end_idx]
    total_pages = (total_count + per_page - 1) // per_page

    return jsonify({
        "current": current_info,
        "chart": {
            "labels": chart_labels,
            "values": chart_values,
            "min_limit": min_limit,
            "max_limit": max_limit,
        },
        "table": paginated_table,
        "pagination": {"current_page": page, "total_pages": total_pages},
    })

# CSV 다운로드 API
@dashboard_bp.route("/api/sensor/<int:sensor_seq>/download_csv")
def download_sensor_csv(sensor_seq):
    with Session(engine) as session:
        query = text("""
                SELECT device_value, min, max, recorded_at 
                FROM device_log 
                WHERE sensor_seq = :seq and
                recorded_at > date_sub(now(), interval 24 hour)
                ORDER BY recorded_at DESC
            """)
        result = session.execute(query, {"seq": sensor_seq}).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["기록 일시", "측정값", "최소 기준", "최대 기준", "상태"]
    )

    sensor_range = readRange()

    for row in result:
        val = float(row.device_value)
        min_v = float(row.min)
        max_v = float(row.max)

        status_label, _, _ = evaluate_status(val, min_v, max_v, float(sensor_range[sensor_seq - 1]))

        writer.writerow([
            row.recorded_at.strftime("%Y-%m-%d %H:%M:%S"),
            val,
            min_v,
            max_v,
            status_label,
        ])

    response = Response(
        "\ufeff" + output.getvalue(), mimetype="text/csv; charset=utf-8"
    )

    response.headers["Content-Disposition"] = (
        f"attachment; filename=sensor_{sensor_seq}_log.csv"
    )
    return response


# -------------------------------------------------------------
# 4. 액추에이터 데이터 API
# 2026. 09. 30. 추가
# -------------------------------------------------------------
# API : LED 로그 조회
# 2026. 09. 30. 추가
@dashboard_bp.route("/api/led/logs")
def get_led_logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    LED_DEVICE_SEQ = 11 # LED

    with Session(engine) as session:
        query = text("""
            SELECT recorded_at, actuator_state, control_source
            FROM (
                SELECT recorded_at, actuator_state, '자동 제어' AS control_source
                FROM auto_control
                WHERE device_seq = :device_seq
                AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                UNION ALL
                SELECT recorded_at, actuator_state, '수동 제어' AS control_source
                FROM manual_control
                WHERE device_seq = :device_seq
                AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ) AS led_logs
            ORDER BY recorded_at DESC
        """)
        result = session.execute(query, {"device_seq": LED_DEVICE_SEQ}).fetchall()
    all_logs = []

    for row in result:
        is_on = int(row.actuator_state) == 1
        action = "ON" if is_on else "OFF"
        if row.control_source == "자동 제어":
            if is_on:
                description = "조도 기준치 미달로 LED를 점등하였습니다."
            else:
                description = "조도 기준치 초과로 LED를 소등하였습니다."
        else:
            if is_on:
                description = "사용자 제어 명령에 의해 LED를 점등하였습니다."
            else:
                description = "사용자 제어 명령에 의해 LED를 소등하였습니다."
        all_logs.append({
            "recorded_at": row.recorded_at.strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "control_source": row.control_source,
            "description": description
        })

    # LED 최근로그(24시간 기록) 페이지네이션
    total_count    = len(all_logs)
    start_idx      = (page - 1) * per_page
    end_idx        = start_idx + per_page
    paginated_logs = all_logs[start_idx:end_idx]
    total_pages = (
        (total_count + per_page - 1) // per_page
        if total_count > 0
        else 0
    )
    return jsonify({
        "logs": paginated_logs,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    })

# -------------------------------------------------------------
# API : FAN 로그 조회
# 2026. 09. 30. 추가
@dashboard_bp.route("/api/fan/logs")
def get_fan_logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    FAN_DEVICE_SEQ = 9 # FAN

    with Session(engine) as session:
        query = text("""
            SELECT recorded_at, actuator_state, control_source
            FROM (
                SELECT
                    recorded_at,
                    actuator_state,
                    '자동 제어' AS control_source
                FROM auto_control
                WHERE device_seq = :device_seq
                  AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)

                UNION ALL

                SELECT
                    recorded_at,
                    actuator_state,
                    '수동 제어' AS control_source
                FROM manual_control
                WHERE device_seq = :device_seq
                  AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ) AS fan_logs
            ORDER BY recorded_at DESC
        """)
        result = session.execute(query, {"device_seq": FAN_DEVICE_SEQ}).fetchall()

    all_logs = []

    for row in result:
        is_on = int(row.actuator_state) == 1
        # ON / OFF
        action = "ON" if is_on else "OFF"
        if row.control_source == "자동 제어":
            if is_on:
                description = "온도 및 습도 기준치 초과로 FAN을 동작합니다."
            else:
                description = "온도 및 습도 기준치 적정으로 FAN을 멈춥니다."
        else:
            if is_on:
                description = "사용자 제어 명령에 의해 FAN을 동작하였습니다."
            else:
                description = "사용자 제어 명령에 의해 FAN을 멈췄습니다."
        all_logs.append({
            "recorded_at": row.recorded_at.strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "control_source": row.control_source,
            "description": description
        })

    # 최근 로그(24시간 기록) 페이지네이션
    total_count    = len(all_logs)
    start_idx      = (page - 1) * per_page
    end_idx        = start_idx + per_page
    paginated_logs = all_logs[start_idx:end_idx]
    total_pages    = ((total_count + per_page - 1) // per_page
                     if total_count > 0
                     else 0
    )
    # return 페이지네이션
    return jsonify({
                    "logs": paginated_logs,
                    "pagination": {
                        "current_page": page,
                        "total_pages": total_pages,
                        "total_count": total_count
                    }
                })


# -------------------------------------------------------------
# API : 커튼 로그 조회
# 2026. 10. 01. 추가
@dashboard_bp.route("/api/curtain/logs")
def get_curtain_logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    CURTAIN_DEVICE_SEQ = 10 # 커튼

    with Session(engine) as session:
        query = text("""
            SELECT recorded_at, actuator_state, control_source
            FROM (
                SELECT recorded_at, actuator_state, '자동 제어' AS control_source
                FROM auto_control
                WHERE device_seq = :device_seq
                AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
                UNION ALL
                SELECT recorded_at, actuator_state, '수동 제어' AS control_source
                FROM manual_control
                WHERE device_seq = :device_seq
                AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ) AS curtain_logs
            ORDER BY recorded_at DESC
        """)
        result = session.execute(query, {"device_seq": CURTAIN_DEVICE_SEQ}).fetchall()
    all_logs = []

    for row in result:
        is_on = int(row.actuator_state) == 1
        action = "ON" if is_on else "OFF"
        if row.control_source == "자동 제어":
            if is_on:
                description = "조도 기준치 미달로 커튼을 열었습니다."
            else:
                description = "조도 기준치 초과로 커튼을 닫았습니다."
        else:
            if is_on:
                description = "사용자 제어 명령에 의해 커튼을 열었습니다."
            else:
                description = "사용자 제어 명령에 의해 커튼을 닫았습니다."
        all_logs.append({
            "recorded_at": row.recorded_at.strftime("%Y-%m-%d %H:%M"),
            "action": action,
            "control_source": row.control_source,
            "description": description
        })

    # 커튼 최근로그(24시간 기록) 페이지네이션
    total_count    = len(all_logs)
    start_idx      = (page - 1) * per_page
    end_idx        = start_idx + per_page
    paginated_logs = all_logs[start_idx:end_idx]
    total_pages = (
        (total_count + per_page - 1) // per_page
        if total_count > 0
        else 0
    )
    return jsonify({
        "logs": paginated_logs,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    })


# -------------------------------------------------------------
# API : 화재 감지(불꽃 센서) 로그 조회
# sensor_seq : 8, device_seq : 7
# 2026. 10. 01. 추가
@dashboard_bp.route("/api/fire/logs")
def get_fire_logs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)
    #FIRE_DEVICE_SEQ = 7 # 불꽃 센서

    with Session(engine) as session:
        query = text("""
            SELECT recorded_at, device_value, min, max
            FROM device_log
            WHERE sensor_seq = 8
            AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        result = session.execute(query).fetchall()

        all_logs = []

        for row in result:
            val = float(row.device_value)
            min_v = float(row.min)
            max_v = float(row.max)
            status_label, status_class, desc = evaluate_status(
                val,
                min_v,
                max_v,
                float(readRange()[7])
            )
            if status_class == "danger":
                all_logs.append({
                    "recorded_at": row.recorded_at.strftime("%Y-%m-%d %H:%M"),
                    "action": "ON",
                    "control_source": "자동 감지",
                    "description": "불꽃 센서 값이 적정 범위를 이탈하여 화재가 감지되었습니다."
                })

    # 화재 감지 최근로그(24시간 기록) 페이지네이션
    total_count    = len(all_logs)
    start_idx      = (page - 1) * per_page
    end_idx        = start_idx + per_page
    paginated_logs = all_logs[start_idx:end_idx]
    total_pages = (
        (total_count + per_page - 1) // per_page
        if total_count > 0
        else 0
    )
    return jsonify({
        "logs": paginated_logs,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    })

# -------------------------------------------------------------
# 액추에이터
# -------------------------------------------------------------
# FAN 로그 조회
# 2026. 10. 01. 추가
@dashboard_bp.route("/fan")
def fan():
    fan_data = {'status': 'OFF'}
    fan_logs = []
    with Session(engine) as db_session:

        # 1) 현재 FAN 상태
        state_query = text("""
            SELECT actuator_state, recorded_at
            FROM (
                SELECT actuator_state, recorded_at
                FROM auto_control
                WHERE device_seq = 9
                UNION ALL
                SELECT actuator_state, recorded_at
                FROM manual_control
                WHERE device_seq = 9
            ) AS fan_state
            ORDER BY recorded_at DESC
            LIMIT 1
        """)
        state_result = db_session.execute(state_query).fetchone()

        if state_result:
            fan_data['status'] = (
                'ON' if int(state_result.actuator_state) == 1
                else 'OFF'
            )

        # 2) 자동 제어 로그
        auto_query = text("""
            SELECT recorded_at, actuator_state, sensor_seq
            FROM auto_control
            WHERE device_seq = 9
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        auto_result = db_session.execute(auto_query).fetchall()

        for row in auto_result:
            state = "ON" if int(row.actuator_state) == 1 else "OFF"
            if state == "ON":
                description = "온도 또는 습도 기준치 초과로 FAN을 동작합니다."
            else:
                description = "온도 및 습도가 적정 범위로 FAN을 멈춥니다."
            fan_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "자동 제어",
                "description": description
            })

        # 3) 수동 제어 로그
        manual_query = text("""
            SELECT recorded_at, actuator_state
            FROM manual_control
            WHERE device_seq = 9
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        manual_result = db_session.execute(manual_query).fetchall()

        for row in manual_result:
            state = "ON" if int(row.actuator_state) == 1 else "OFF"
            if state == "ON":
                description = "사용자 제어 명령에 의해 FAN을 동작하였습니다."
            else:
                description = "사용자 제어 명령에 의해 FAN을 멈췄습니다."
            fan_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "수동 제어",
                "description": description
            })

    # 4) 자동 + 수동 로그 시간순 정렬
    fan_logs.sort(
        key=lambda x: x["recorded_at"],
        reverse=True
    )

    fan_logs = fan_logs[:5]

    for log in fan_logs:
        log["recorded_at"] = log["recorded_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    is_active = fan_data['status'] == 'ON'

    return render_template(
        "a_fan.html",
        fan_data=fan_data,
        fan_logs=fan_logs,
        is_active=is_active
    )

# -------------------------------------------------------------
# 커튼
@dashboard_bp.route("/curtain")
def curtain():

    curtain_data = {'status': 'OFF'}
    curtain_logs = []

    with Session(engine) as db_session:

        # 1) 현재 커튼 상태
        state_query = text("""
            SELECT actuator_state, recorded_at
            FROM (
                SELECT actuator_state, recorded_at
                FROM auto_control
                WHERE device_seq = 10
                UNION ALL
                SELECT actuator_state, recorded_at
                FROM manual_control
                WHERE device_seq = 10
            ) AS curtain_state
            ORDER BY recorded_at DESC
            LIMIT 1
        """)
        state_result = db_session.execute(state_query).fetchone()

        if state_result:
            curtain_data['status'] = (
                'ON' if int(state_result.actuator_state) == 1
                else 'OFF')

        # 2) 자동 제어 로그
        auto_query = text("""
            SELECT recorded_at, actuator_state
            FROM auto_control
            WHERE device_seq = 10
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        auto_result = db_session.execute(auto_query).fetchall()

        for row in auto_result:
            state = (
                "ON"
                if int(row.actuator_state) == 1
                else "OFF"
            )
            if state == "ON":
                description = "조도 설정 범위를 초과하여 커튼이 작동 중입니다."
            else:
                description = "조도가 적정 범위 내에 있어 커튼이 정지된 상태입니다."

            curtain_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "자동 제어",
                "description": description
            })

        # 3) 수동 제어 로그
        manual_query = text("""
            SELECT recorded_at, actuator_state
            FROM manual_control
            WHERE device_seq = 10
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        manual_result = db_session.execute(manual_query).fetchall()

        for row in manual_result:
            state = (
                "ON"
                if int(row.actuator_state) == 1
                else "OFF"
            )
            if state == "ON":
                description = "사용자 제어 명령에 의해 커튼을 열었습니다."
            else:
                description = "사용자 제어 명령에 의해 커튼을 닫았습니다."
            curtain_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "수동 제어",
                "description": description
            })

        # 4) 자동 + 수동 로그 시간순 정렬
        curtain_logs.sort(
              key=lambda x: x["recorded_at"]
            , reverse=True
        )
        curtain_logs = curtain_logs[:5]

        for log in curtain_logs:
            log["recordd_at"] = log["recorded_at"].strftime(
                "%Y-%m-%d %H:%M:%S")

        # 5) HTML에 전달
        return render_template(
                "a_curtain.html",
                curtain_data=curtain_data,
                curtain_logs=curtain_logs
        )

# -------------------------------------------------------------
# LED
@dashboard_bp.route("/led")
def led():
    led_data = {'status': 'OFF'}
    led_logs = []
    with Session(engine) as db_session:

        # 1) 현재 LED 상태
        state_query = text("""
            SELECT actuator_state, recorded_at
            FROM (
                SELECT actuator_state, recorded_at
                FROM   auto_control
                WHERE  device_seq = 11
                UNION ALL
                SELECT actuator_state, recorded_at
                FROM   manual_control
                WHERE  device_seq = 11
            ) AS led_state
            ORDER BY recorded_at DESC
            LIMIT 1
        """)
        state_result = db_session.execute(state_query).fetchone()

        if state_result:
            led_data['status'] = (
                'ON' if int(state_result.actuator_state) == 1
                else 'OFF'
            )

        # 2) 자동 제어 로그
        auto_query = text("""
            SELECT recorded_at, actuator_state
            FROM auto_control
            WHERE device_seq = 11
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        auto_result = db_session.execute(auto_query).fetchall()

        for row in auto_result:
            state = "ON" if int(row.actuator_state) == 1 else "OFF"
            if state == "ON":
                description = "조도 기준치 미만으로 LED를 점등합니다."
            else:
                description = "조도 기준치 이상으로 LED를 소등합니다."
            led_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "자동 제어",
                "description": description
            })

        # 3) 수동 제어 로그
        manual_query = text("""
            SELECT recorded_at, actuator_state
            FROM manual_control
            WHERE device_seq = 11
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        manual_result = db_session.execute(manual_query).fetchall()

        for row in manual_result:
            state = "ON" if int(row.actuator_state) == 1 else "OFF"
            if state == "ON":
                description = "사용자 제어 명령에 의해 LED를 점등하였습니다."
            else:
                description = "사용자 제어 명령에 의해 LED를 소등하였습니다."
            led_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "수동 제어",
                "description": description
            })
    # 4) 자동 + 수동 로그 시간순 정렬
    led_logs.sort(
        key=lambda x: x["recorded_at"],
        reverse=True
    )
    led_logs = led_logs[:5]

    for log in led_logs:
        log["recorded_at"] = log["recorded_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    # 5) HTML에 전달
    return render_template(
        "a_led.html",
        led_data=led_data,
        led_logs=led_logs
    )

# -------------------------------------------------------------
# 화재 (불꽃 감지 센서)
# sensor_seq : 8, device_seq : 7
@dashboard_bp.route("/fire")
def fire():
    fire_data = {
          'status': 'OFF'
        , 'flame_detected': True
    }
    fire_logs = []
    with Session(engine) as db_session:

        # 1) 현재 불꽃 센서 상태
        state_query = text("""
            SELECT device_value, min, max, recorded_at
            FROM device_log
            WHERE sensor_seq = 8
            ORDER BY recorded_at DESC
            LIMIT 1
        """)

        state_result = db_session.execute(state_query).fetchone()

        if state_result:
            val = float(state_result.device_value)
            min_v = float(state_result.min)
            max_v = float(state_result.max)

            if val < min_v or val > max_v:
                fire_data['status'] = 'ON'
            else:
                fire_data['status'] = 'OFF'

        # 2) 자동 제어 로그
        auto_query = text("""
            SELECT recorded_at, actuator_state
            FROM auto_control
            WHERE device_seq = 7
              AND recorded_at > DATE_SUB(NOW(), INTERVAL 24 HOUR)
            ORDER BY recorded_at DESC
        """)
        auto_result = db_session.execute(auto_query).fetchall()

        for row in auto_result:
            state = "ON" if int(row.actuator_state) == 1 else "OFF"
            if state == "ON":
                description = "불꽃 센서 기준치 초과로 화재가 감지되었습니다."
            else:
                description = "불꽃 센서 기준치 미만으로 화재가 감지되지 않았습니다."
            fire_logs.append({
                "recorded_at": row.recorded_at,
                "state": state,
                "control_type": "자동 제어",
                "description": description
            })

        # 3) 수동 제어 로그 : 불꽃 센서 해당 없음

    # 4) 자동 로그 시간순 정렬
    fire_logs.sort(
        key=lambda x: x["recorded_at"],
        reverse=True
    )
    fire_logs = fire_logs[:5]

    for log in fire_logs:
        log["recorded_at"] = log["recorded_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    # 5) HTML에 전달
    return render_template(
        "a_fire.html",
        fire_data=fire_data,
        fire_logs=fire_logs
    )

@dashboard_bp.post("/change-actuator")
def changeActuator():
    sessionUser = session.get("user_seq")
    data = request.get_json()

    actuator = data['actuator']
    is_auto = data['is_auto']

    actuatorList = {
        "FAN" : 9,
        "CURTAIN" : 10,
        "LED" : 11
    }

    with Session(engine) as db_session:
        manual = ManualControl(
            user_seq = sessionUser,
            device_seq = actuatorList[actuator],
            actuator_state = is_auto,
            recorded_at = datetime.now()
        )
        db_session.add(manual)
        db_session.commit()

    msg = "a&" + str(actuatorList[actuator]) + "&" + str(is_auto) + "$"
    
    if websock.web_socket:
        websock.web_socket.send(msg)
        print(msg)

    return jsonify({
        "result" : "success"
    })