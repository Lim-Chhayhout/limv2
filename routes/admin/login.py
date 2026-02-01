from app import app
from flask import render_template, redirect
from models import User
from werkzeug.security import check_password_hash
from flask import request, jsonify, make_response
from middleware.jwt import create_jwt, verify_jwt

@app.post("/login-post")
def login_post():
    form = request.form
    email = form.get("email")
    password = form.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Login failed: Incorrect Email or Password!"}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"error": "Login failed: Incorrect Email or Password!"}), 401

    if user.status != "Enable" or user.user_role.status != "Enable":
        return jsonify({"error": "Login failed: Account disabled!"}), 403

    token = create_jwt(user)
    if user.user_role.name == "Superadmin":
        redirect_url = "/dashboard"
    else:
        redirect_url = "/product-management"

    resp = make_response(redirect(redirect_url))
    resp.set_cookie("access_token", token, httponly=True, max_age=24 * 60 * 60)  # 24h
    return resp

@app.route("/login")
def login():
    token = request.cookies.get("access_token")
    payload = verify_jwt(token) if token else None

    if payload:
        user = User.query.get(payload.get("user_id"))
        if user and user.status == "Enable" and user.token_version == payload.get("token_version"):
            role = payload.get("role")
            if role == "Admin":
                return redirect("/product-management")
            elif role == "Superadmin":
                return redirect("/dashboard")
            else:
                return redirect("/login")

    return render_template("auth/login.html", title="LIM - Kdmv")