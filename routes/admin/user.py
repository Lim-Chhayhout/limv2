from werkzeug.security import generate_password_hash
from middleware.jwt import jwt_required
from app import app, db
from flask import render_template, make_response, request, jsonify
from werkzeug.utils import secure_filename
from models import User, UserRole
from utils.timezone import PhnomPenhTime
import os

# ===============================================================================================================
# api with backend
# ===============================================================================================================
@app.get("/user-management/by-id/<int:user_id>")
def user_management_by_id(user_id):
    try:
        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({"error": f"User ID {user_id} not found"}), 404

        role_name = user.user_role.name if user.user_role else None
        result = {
            user.id: {
                "role_name": role_name,
                "profile_pic": user.profile_pic,
                "name": user.name,
                "email": user.email,
                "telephone": user.telephone,
                "password": user.password,
                "status": user.status,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 5004

@app.post("/user-management/create-user")
def user_management_create_user():
    try:
        form = request.form
        if not form:
            return jsonify({"error": "Form is empty!"}), 400

        file_obj = request.files.get("profile_pic")

        name = form.get("name")
        email = form.get("email")
        telephone = form.get("telephone")
        password = generate_password_hash(form.get("password"))
        role_id = form.get("role_id")
        status = form.get("status")

        required_fields = {
            "name": name,
            "email": email,
            "telephone": telephone,
            "password": password,
            "status": status,
            "role_id": role_id,
        }
        for key, value in required_fields.items():
            if not value:
                return jsonify({"error": f"{key.capitalize()} is required"}), 400

        if status not in ("Enable", "Disable"):
            return jsonify({"error": "Status must be one of Enable, Disable"}), 400

        role = db.session.get(UserRole, int(role_id))
        if not role:
            return jsonify({"error": f"Role ID {role_id} not found"}), 404

        if db.session.query(User).filter_by(name=name).first():
            return jsonify({"error": f"User '{name}' already exists!"}), 400
        if db.session.query(User).filter_by(email=email).first():
            return jsonify({"error": f"Email '{email}' already exists!"}), 400
        if db.session.query(User).filter_by(telephone=telephone).first():
            return jsonify({"error": f"Telephone '{telephone}' already exists!"}), 400

        profile_pic = "user_icon.png"
        if file_obj and file_obj.filename.strip() != "":
            safe_name = secure_filename(file_obj.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG files are allowed"}), 400

            upload_folder = "./static/images/users"
            os.makedirs(upload_folder, exist_ok=True)
            file_name = f"user_{PhnomPenhTime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
            file_path = os.path.join(upload_folder, file_name)
            file_obj.save(file_path)
            profile_pic = file_name

        user = User(
            profile_pic=profile_pic,
            name=name,
            email=email,
            telephone=telephone,
            password=password,
            status=status,
            role_id=role_id,
        )
        db.session.add(user)
        db.session.commit()

        return jsonify({"success": "New user created!", "user_id": user.id})

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/user-management/update-user/<int:user_id>")
def user_management_update_user(user_id: int):
    try:
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        form = request.form
        if not form:
            return jsonify({"error": "Form is empty!"}), 400

        file_obj = request.files.get("profile_pic")

        updated = False
        logout = False

        name = form.get("name")
        email = form.get("email")
        telephone = form.get("telephone")
        new_role = form.get("role")
        status = form.get("status")

        required_fields = {
            "name": name,
            "email": email,
            "telephone": telephone,
            "status": status,
            "new_role": new_role,
        }
        for key, value in required_fields.items():
            if not value:
                return jsonify({"error": f"{key.capitalize()} is required"}), 400

        if status not in ("Enable", "Disable"):
            return jsonify({"error": "Status must be one of Enable, Disable"}), 400

        role = db.session.get(UserRole, int(new_role))
        if not role:
            return jsonify({"error": f"Role ID {new_role} not found"}), 404

        if db.session.query(User).filter(User.name==name, User.id!=user_id).first():
            return jsonify({"error": f"User '{name}' already exists!"}), 400
        if db.session.query(User).filter(User.email==email, User.id!=user_id).first():
            return jsonify({"error": f"Email '{email}' already exists!"}), 400
        if db.session.query(User).filter(User.telephone==telephone, User.id!=user_id).first():
            return jsonify({"error": f"Telephone '{telephone}' already exists!"}), 400

        if file_obj and file_obj.filename.strip() != "":
            safe_name = secure_filename(file_obj.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG allowed"}), 400
            upload_folder = "./static/images/users"
            os.makedirs(upload_folder, exist_ok=True)
            file_name = f"user_{PhnomPenhTime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
            file_path = os.path.join(upload_folder, file_name)
            file_obj.save(file_path)
            user.profile_pic = file_name
            updated = True

        if user.name != name:
            user.name = name
            updated = True

        if user.email != email:
            user.email = email
            updated = True

        if user.telephone != telephone:
            user.telephone = telephone
            updated = True

        if user.status != status:
            user.status = status
            logout = True

        if user.role_id != int(new_role):
            user.role_id = int(new_role)
            logout = True

        if updated:
            db.session.commit()
            return jsonify({"success": "User updated successfully!", "user_id": user.id})

        if logout:
            user.token_version += 1
            db.session.commit()

            resp = make_response(jsonify({"success": "User updated successfully!, logging out...", "user_id": user.id}))
            resp.set_cookie("access_token", "", expires=0)
            return resp

        return jsonify({"error": "Nothing to updated!", "user_id": user.id})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/user-management/delete-user/<int:user_id>")
def user_management_delete_user(user_id: int):
    try:
        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({"error": f"User ID {user_id} not found"}), 404

        if user.profile_pic and user.profile_pic != "user_icon.png":
            image_path = os.path.join(app.root_path, "static/images/users", user.profile_pic)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(user)
        db.session.commit()

        return jsonify({"success": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front
# ===============================================================================================================
@app.route("/user-management")
@jwt_required(roles=["Superadmin"])
def user_management(role):
    users = db.session.query(User).order_by(User.name.asc()).all()
    return render_template(
        "auth/admin/user-mgt.html",
        title="LIM - User Management",
        users=users,
        user_role=role
    )

@app.route("/user-management/add-user")
@jwt_required(roles=["Superadmin"])
def user_management_add(role):
    roles = db.session.query(UserRole).filter_by(status="Enable").all()
    return render_template(
        "auth/admin/user-mgt.html",
        title="LIM - Add User",
        page="add-user",
        roles=roles,
        user_role=role
    )

@app.route("/user-management/show-user/<int:user_id>")
@jwt_required(roles=["Superadmin"])
def user_management_show(user_id, role):
    user = db.session.query(User).get(user_id)

    return render_template(
        "auth/admin/user-mgt.html",
        title=f"LIM - Show {user.name}",
        page="show-user",
        user=user,
        user_role = role
    )

@app.route("/user-management/edit-user/<int:user_id>")
@jwt_required(roles=["Superadmin"])
def user_management_edit(user_id, role):
    user = db.session.query(User).get(user_id)
    if not user:
        return "User not found", 404

    roles = db.session.query(UserRole).filter(UserRole.status == "Enable").all()

    return render_template(
        "auth/admin/user-mgt.html",
        title="LIM - Edit User",
        page="edit-user",
        user=user,
        roles=roles,
        user_role = role
    )