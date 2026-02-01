from flask import redirect, make_response, request
from models import User
from app import app, db
from middleware.jwt import verify_jwt

@app.route("/logout")
def logout():
    token = request.cookies.get("access_token")
    payload = verify_jwt(token) if token else None

    if payload:
        user = User.query.get(payload.get("user_id"))
        if user:
            user.token_version += 1
            db.session.commit()

    resp = make_response(redirect("/login"))
    resp.delete_cookie("access_token")
    return resp
