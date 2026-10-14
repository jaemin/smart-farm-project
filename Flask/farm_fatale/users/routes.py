from flask import Blueprint, render_template, request, session, redirect, jsonify, flash
from sqlalchemy.orm import Session
from sqlalchemy import select
from static.db import engine
from werkzeug.security import generate_password_hash, check_password_hash
import re
import datetime

from models import User

users_bp = Blueprint(
    "users",                # BluePrint 이름
    __name__
)

@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        user_id = request.form["user_id"]
        password = request.form["password"]

        with Session(engine) as db:

            user = db.scalar(
                select(User).where(User.user_id == user_id)
            )

            if user is None:
                flash("아이디 또는 비밀번호가 잘못되었습니다.")
                return redirect("/login")

            # =========================
            # 관리자 초기 비밀번호 확인
            # =========================
            if user.user_id == "admin" and user.password == "admin":

                if password != "admin":
                    flash("아이디 또는 비밀번호가 잘못되었습니다.")
                    return redirect("/login")

                session["user_seq"] = user.user_seq
                session["user_id"] = user.user_id
                session["user_name"] = user.user_name
                session["email_address"] = user.email_address
                session["user_tel"] = user.user_tel

                return redirect(
                    f"/reset_password/{user.user_seq}"
                )

            # =========================
            # 일반 비밀번호 확인
            # =========================
            if not check_password_hash(user.password, password):
                flash("아이디 또는 비밀번호가 잘못되었습니다.")
                return redirect("/login")

            session["user_seq"] = user.user_seq
            session["user_id"] = user.user_id
            session["user_name"] = user.user_name
            session["email_address"] = user.email_address
            session["user_tel"] = user.user_tel

            return redirect("/dashboard")

    return render_template("login.html")

@users_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# 아이디 중복 확인
@users_bp.route("/check_user_id")
def check_user_id():
    user_id = request.args.get("user_id", "").strip()

    if not user_id:
        return jsonify({
            "available": False,
            "message": "아이디를 입력해주세요."
        })

    if not re.fullmatch(r"[A-Za-z0-9]{4,20}", user_id):
        return jsonify({
            "available": False,
            "message": "아이디는 영문과 숫자를 사용하여 4~20자로 입력해주세요."
        })

    with Session(engine) as db:

        user = db.scalar(
            select(User).where(User.user_id == user_id)
        )

        if user:
            return jsonify({
                "available": False,
                "message": "이미 사용중인 아이디입니다."
            })

    return jsonify({
        "available": True,
        "message": "사용 가능한 아이디입니다."
    }).route("/check_user_id")

def check_user_id():

    user_id = request.args.get("user_id", "").strip()

    if not user_id:
        return jsonify({
            "available": False,
            "message": "아이디를 입력해주세요."
        })

    if not re.fullmatch(r"[A-Za-z0-9]{4,20}", user_id):
        return jsonify({
            "available": False,
            "message": "아이디는 영문과 숫자를 사용하여 4~20자로 입력해주세요."
        })

    with Session(engine) as db:

        user = db.scalar(
            select(User).where(User.user_id == user_id)
        )

        if user:
            return jsonify({
                "available": False,
                "message": "이미 사용중인 아이디입니다."
            })

    return jsonify({
        "available": True,
        "message": "사용 가능한 아이디입니다."
    })

# 이메일 중복 확인
@users_bp.route("/check_email")
def check_email():

    email = request.args.get("email", "").strip()

    if not email:
        return jsonify({
            "available": False,
            "message": "이메일을 입력해주세요."
        })

    if not re.fullmatch(
        r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
        email
    ):
        return jsonify({
            "available": False,
            "message": "올바른 이메일 형식을 입력해주세요."
        })

    with Session(engine) as db:

        user = db.scalar(
            select(User).where(User.email_address == email)
        )

        if user:
            return jsonify({
                "available": False,
                "message": "이미 사용중인 이메일입니다."
            })

    return jsonify({
        "available": True,
        "message": "사용 가능한 이메일입니다."
    })

# 전화번호 중복 확인
@users_bp.route("/check_phone")
def check_phone():

    user_tel = request.args.get("user_tel", "").strip()

    if not user_tel:
        return jsonify({
            "available": False,
            "message": "전화번호를 입력해주세요."
        })

    if not re.fullmatch(r"01[0-9]-?[0-9]{3,4}-?[0-9]{4}", user_tel):
        return jsonify({
            "available": False,
            "message": "올바른 전화번호를 입력해주세요."
        })

    with Session(engine) as db:

        user = db.scalar(
            select(User).where(User.user_tel == user_tel)
        )

        if user:
            return jsonify({
                "available": False,
                "message": "이미 등록된 전화번호입니다."
            })

    return jsonify({
        "available": True,
        "message": "사용 가능한 전화번호입니다."
    })

# 회원가입 페이지
@users_bp.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        user_id = request.form.get("user_id", "").strip()
        password = request.form.get("password", "")
        password_confirm = request.form.get("password_confirm", "")
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        user_tel = request.form.get("user_tel", "").strip()

        # 1. 필수값 검사
        if not user_id or not password or not password_confirm \
                or not name or not email or not user_tel:
            return "필수 항목을 모두 입력해주세요."

        # 2. 아이디 형식 검사
        if not re.fullmatch(r"[A-Za-z0-9]{4,20}", user_id):
            return "아이디는 영문과 숫자를 사용하여 4~20자로 입력해주세요."

        # 3. 비밀번호 형식 검사
        if len(password) < 8:
            return "비밀번호는 8자 이상 입력해주세요."

        # 4. 비밀번호 확인
        if password != password_confirm:
            return "비밀번호가 일치하지 않습니다."

        # 5. 이메일 형식 검사
        if not re.fullmatch(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email
        ):
            return "올바른 이메일 형식을 입력해주세요."

        # 6. 전화번호 형식 검사
        if not re.fullmatch(r"01[0-9]-?[0-9]{3,4}-?[0-9]{4}", user_tel):
            return "올바른 전화번호를 입력해주세요."

        # 7. DB 중복 검사
        with Session(engine) as db:

            # 아이디 중복
            exist_id = db.scalar(
                select(User).where(
                    User.user_id == user_id
                )
            )

            if exist_id:
                return "이미 사용중인 아이디입니다."

            # 이메일 중복
            exist_email = db.scalar(
                select(User).where(
                    User.email_address == email
                )
            )

            if exist_email:
                return "이미 사용중인 이메일입니다."

            # 회원 저장
            new_user = User(
                user_id=user_id,
                password=generate_password_hash(password),
                user_name=name,
                email_address=email,
                user_tel=user_tel,
                create_at=datetime.datetime.now()
            )

            db.add(new_user)
            db.commit()

        flash("회원가입이 완료되었습니다.")
        return redirect("/login")

    return render_template("signup.html")

# 아이디 찾기 페이지
@users_bp.route("/find_id", methods=["GET", "POST"])
def find_id():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            return "이름과 이메일을 모두 입력해주세요."

        with Session(engine) as db:

            user = db.scalar(
                select(User).where(
                    User.user_name == name,
                    User.email_address == email
                )
            )

        if user is None:
            flash("일치하는 회원 정보를 찾을 수 없습니다.")
            return redirect("/find_id")

        return render_template(
            "find_id_result.html",
            user_id=user.user_id
        )

    return render_template("find_id.html")

# 비밀번호 찾기 페이지
@users_bp.route("/find_password", methods=["GET", "POST"])
def find_password():

    if request.method == "POST":

        user_id = request.form.get("user_id", "").strip()
        email = request.form.get("email", "").strip()

        if not user_id or not email:
            flash("아이디와 이메일을 모두 입력해주세요.")
            return redirect("/find_password")

        with Session(engine) as db:

            user = db.scalar(
                select(User).where(
                    User.user_id == user_id,
                    User.email_address == email
                )
            )

            if user is None:
                flash("일치하는 회원 정보를 찾을 수 없습니다.")
                return redirect("/find_password")

            return render_template(
                "reset_password.html",
                user_seq=user.user_seq
            )

    return render_template("find_password.html")

# 비밀번호 변경 페이지
@users_bp.route("/reset_password/<int:user_seq>", methods=["GET", "POST"])
def reset_password(user_seq):

    # =========================
    # 비밀번호 변경 페이지 표시
    # =========================
    if request.method == "GET":
        return render_template(
            "reset_password.html",
            user_seq=user_seq
        )

    # =========================
    # 비밀번호 변경 처리
    # =========================
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")

    if not password or not password_confirm:
        return "비밀번호를 입력해주세요."

    if len(password) < 8:
        return "비밀번호는 8자 이상 입력해주세요."

    if password != password_confirm:
        return "비밀번호가 일치하지 않습니다."

    with Session(engine) as db:

        user = db.get(User, user_seq)

        if user is None:
            return "사용자를 찾을 수 없습니다."

        user.password = generate_password_hash(password)

        db.commit()

    flash("비밀번호 변경이 완료되었습니다.")
    return redirect("/login")