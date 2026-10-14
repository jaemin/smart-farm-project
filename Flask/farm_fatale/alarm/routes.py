from flask import Blueprint, request, render_template, jsonify, Response
from sqlalchemy import text
from static.db import engine
from sqlalchemy.orm import Session
from datetime import datetime
from dashboard.routes import evaluate_status, readRange
import csv
import io

alarm_bp = Blueprint(
    "alarm",                # BluePrint 이름
    __name__
)

# -------------------------------------------------------------
# 알람
@alarm_bp.route("/alarm")
def alarm():
    return render_template("alarm.html", logs=[])

# 알람 api
@alarm_bp.route("/api/alarms")
def get_alarm_data():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    filter_type = request.args.get("filter", "ALL")
    
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    with Session(engine) as session:
        sql = """
            SELECT 
                dl.sensor_seq,
                dl.recorded_at, 
                dl.device_value, 
                dl.min, 
                dl.max,
                CASE dl.sensor_seq
                    WHEN 1 THEN '온도'
                    WHEN 2 THEN '습도'
                    WHEN 3 THEN '조도'
                    WHEN 4 THEN '수온'
                    WHEN 5 THEN '유량'
                    WHEN 6 THEN 'pH'
                    WHEN 7 THEN 'TDS'
                    WHEN 8 THEN '불꽃'
                    WHEN 9 THEN '가스'
                    ELSE '기타 센서'
                END AS device_name
            FROM device_log dl
            WHERE 1=1
        """
        params = {}

        if start_date:
            sql += " AND dl.recorded_at >= :start_date"
            params["start_date"] = f"{start_date} 00:00:00"
        if end_date:
            sql += " AND dl.recorded_at <= :end_date"
            params["end_date"] = f"{end_date} 23:59:59"

        sql += " ORDER BY dl.recorded_at DESC"
        result = session.execute(text(sql), params).fetchall()

    sensor_range = readRange()

    all_logs = []
    for row in result:
        try:
            val = float(row.device_value) if row.device_value is not None else 0.0
            min_v = float(row.min) if row.min is not None else 0.0
            max_v = float(row.max) if row.max is not None else 0.0
        except (ValueError, TypeError):
            val, min_v, max_v = 0.0, 0.0, 0.0
            
        status_label, status_class, desc = evaluate_status(val, min_v, max_v, float(sensor_range[row.sensor_seq - 1]))

        # 예외 처리 (양호 제외하고 주의, 경고만 뜨도록)
        if status_class not in ['warning', 'danger']:
            continue

        # 주의, 경고
        if filter_type == 'WARNING' and status_class != 'warning':
            continue
        if filter_type == 'DANGER' and status_class != 'danger':
            continue

        device_name = row.device_name

        rec_time = row.recorded_at
        if isinstance(rec_time, datetime):
            formatted_time = rec_time.strftime("%Y-%m-%d %H:%M:%S")
        elif rec_time:
            formatted_time = str(rec_time)
        else:
            formatted_time = "-"

        all_logs.append({
            "recorded_at": formatted_time,
            "device_name": device_name,
            "status": status_label,
            "status_class": status_class,
            "message": f"{device_name} 주의 : 적정 범위 가까움 ({val})",
            "action": desc
        })

    total_count = len(all_logs)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_table = all_logs[start_idx:end_idx]
    total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

    return jsonify({
        "table": paginated_table,
        "pagination": {
            "current_page": page,
            "total_pages": total_pages,
            "total_count": total_count
        }
    })

# CSV
@alarm_bp.route("/api/alarms/download_csv")
def download_alarm_csv():
    filter_type = request.args.get("filter", "ALL")

    with Session(engine) as session:
        sql = """
            SELECT 
                dl.sensor_seq,
                dl.recorded_at, 
                dl.device_value, 
                dl.min, 
                dl.max,
                CASE dl.sensor_seq
                    WHEN 1 THEN '온도'
                    WHEN 2 THEN '습도'
                    WHEN 3 THEN '조도'
                    WHEN 4 THEN '수온'
                    WHEN 5 THEN '유량'
                    WHEN 6 THEN 'pH'
                    WHEN 7 THEN 'TDS'
                    WHEN 8 THEN '불꽃'
                    WHEN 9 THEN '가스'
                    ELSE '기타 센서'
                END AS device_name
            FROM device_log dl
            ORDER BY dl.recorded_at DESC
        """
        result = session.execute(text(sql)).fetchall()

    sensor_range = readRange()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["번호", "시간", "장치", "상태", "알람 내용", "조치 내용"])

    count = 1
    for row in result:
        try:
            val = float(row.device_value) if row.device_value is not None else 0.0
            min_v = float(row.min) if row.min is not None else 0.0
            max_v = float(row.max) if row.max is not None else 0.0
        except (ValueError, TypeError):
            val, min_v, max_v = 0.0, 0.0, 0.0

        status_label, status_class, desc = evaluate_status(val, min_v, max_v, float(sensor_range[row.sensor_seq - 1]))

        if status_class not in ['warning', 'danger']:
            continue

        if filter_type == 'WARNING' and status_class != 'warning':
            continue
        if filter_type == 'DANGER' and status_class != 'danger':
            continue

        rec_time = row.recorded_at.strftime("%Y-%m-%d %H:%M:%S") if isinstance(row.recorded_at, datetime) else str(row.recorded_at)

        writer.writerow([
            count,
            rec_time,
            row.device_name,
            status_label,
            f"{row.device_name} 주의 : 적정 범위 가까움 ({val})",
            desc
        ])
        count += 1

    csv_data = output.getvalue().encode('utf-8-sig')
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=alarm_log_{filter_type.lower()}.csv"}
    )