import jwt
from datetime import datetime, timedelta
from flask import request, redirect, abort
from models import User
from functools import wraps
from app import app


def create_jwt(user):
    payload = {
        "user_id": user.id,
        "role": user.user_role.name,
        "token_version": user.token_version,
        "exp": datetime.utcnow() + timedelta(minutes=720)
    }
    token = jwt.encode(payload, app.secret_key, algorithm="HS256")
    return token

def jwt_required(roles=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = request.cookies.get("access_token")
            if not token:
                return redirect("/login")

            payload = verify_jwt(token)
            if not payload:
                return redirect("/login")

            user = User.query.get(payload.get("user_id"))
            if not user or user.status != "Enable" or user.token_version != payload.get("token_version"):
                return redirect("/login")

            if roles and payload.get("role") not in roles:
                return abort (403)

            return f(*args, **kwargs, role=payload.get("role"))

        return wrapper

    return decorator


def verify_jwt(token):
    try:
        payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None