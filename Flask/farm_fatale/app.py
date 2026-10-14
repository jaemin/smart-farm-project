from flask import Flask, session, request, redirect, render_template
from flask_cors import CORS
from websock import sock

# BluePrint
from users.routes import users_bp
from control.routes import control_bp
from dashboard.routes import dashboard_bp
from alarm.routes import alarm_bp
from data.routes import data_bp
from cctv.routes import cctv_bp
from insert.routes import insert_bp
from sensor_range.routes import sensor_range_bp

app = Flask(__name__)
CORS(app)

app.secret_key = "ktech-secret-key"

sock.init_app(app)

# BluePrint 등록
app.register_blueprint(users_bp)
app.register_blueprint(control_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(alarm_bp)
app.register_blueprint(data_bp)
app.register_blueprint(cctv_bp)
app.register_blueprint(insert_bp)
app.register_blueprint(sensor_range_bp)

@app.before_request
def login_required():
    # print("endpoint =", request.endpoint)
    # print("path =", request.path)

    # 로그인 없이 접근 가능한 페이지 목록
    public_endpoints = ["users.login", "static", "users.signup", "users.check_user_id", "users.check_email",
                        "users.check_phone", "users.find_id", "users.find_password", "users.reset_password/<int:user_seq>", 
                        "insert.insertValue", "__flask_sock.websocket"] 

    if request.endpoint in public_endpoints:
        return 

    # 전처리 (로그인 여부 체크)
    if session.get("user_id") is None:
        return redirect("/login")

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# 오류 페이지 500
@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

@app.context_processor
def setUser():
    return {
        "user_seq" : session.get("user_seq"),
        "user_name" : session.get("user_name"),
        "user_id" : session.get("user_id"),
        "email_address" : session.get("email_address"),
        "user_tel" : session.get("user_tel")
    }

# print(app.url_map)    view function 확인용

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # 다른 PC에서도 접속을 허용
    # app.run(debug=True)