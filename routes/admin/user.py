from app import app
from flask import render_template
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import db
from models import User, UserRole
from utils.timezone import PhnomPenhTime
import os

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================
@app.post("/user-management/create-role-json")
def user_management_create_role():
    try:
        json_data = request.json
        if not json_data:
            return jsonify({"message": "No Data Provided"}), 400

        name = json_data.get("name")
        if not name:
            return jsonify({"message": "No Name Provided"}), 400

        status = json_data.get("status")
        if not status:
            return jsonify({"message": "No Status Provided"}), 400

        if status and status not in ("Enable", "Disable"):
            return jsonify({"error": "Status must be Enable or Disable"}), 400

        existing = UserRole.query.filter_by(name=name).first()
        if existing:
            return jsonify({"error": "Role name already exists"}), 409

        new_role = UserRole(name=name, status=status)
        db.session.add(new_role)
        db.session.commit()

        return jsonify({"message": "Role created successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/user-management/list-json")
def user_management_list_json():
    try:
        users = db.session.query(User).all()
        if not users:
            return jsonify({"message": "No users found"}), 404

        results = {}
        for u in users:
            role_name = u.user_role.name if u.user_role else None
            results[u.id] = {
                "role_name": role_name,
                "profile_pic": u.profile_pic,
                "name": u.name,
                "email": u.email,
                "telephone": u.telephone,
                "password": u.password,
                "status": u.status,
                "created_at": u.created_at,
                "updated_at": u.updated_at
            }

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

@app.post("/user-management/create-form-data")
def user_management_create_form_data():
    try:
        form = request.form
        if not form:
            return jsonify({"error": "Request body is empty"}), 400

        upload_folder = "./static/images/users"
        os.makedirs(upload_folder, exist_ok=True)
        allowed_extensions = {"jpg", "jpeg", "png", "svg"}

        def save_file(file, prefix="user"):
            if file and file.filename.strip() != "":
                safe_name = secure_filename(file.filename)
                ext = safe_name.rsplit(".", 1)[-1].lower()
                if ext not in allowed_extensions:
                    raise ValueError(f"Only JPG, PNG, SVG files are allowed: {file.filename}")
                file_name = f"{prefix}_{PhnomPenhTime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
                file_path = os.path.join(upload_folder, file_name)
                file.save(file_path)
                return file_name
            return None

        profile_pic = save_file(request.files.get("profile_pic"))

        # extract form data
        name = form.get("name")
        email = form.get("email")
        telephone = form.get("telephone")
        password = form.get("password")
        role_id = form.get("role_id")
        status = form.get("status")

        # validation
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
            return jsonify({"error": f"Status must be one of Enable, Disable"}), 400

        role = db.session.get(UserRole, int(role_id))
        if not role:
            return jsonify({"error": f"Role ID {role_id} not found"}), 404

        # duplicate
        exist_name = db.session.query(User).filter_by(name=name).first()
        exist_email = db.session.query(User).filter_by(email=email).first()
        exist_telephone = db.session.query(User).filter_by(telephone=telephone).first()
        if exist_name:
            return jsonify({"error": f"User: '{name}' already exists!"}), 400
        if exist_email:
            return jsonify({"error": f"User: '{email}' already exists!"}), 400
        if exist_telephone:
            return jsonify({"error": f"User: '{telephone}' already exists!"}), 400

        # transaction insert
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

        created_user = {
            user.id:{
                "role": role.name,
                "profile_pic": user.profile_pic,
                "name": user.name,
                "email": user.email,
                "telephone": user.telephone,
                "password": user.password,
                "status": user.status,
            }
        }

        return jsonify(
            {
                "message": "User created!",
                "result": created_user
            }
        )

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/user-management/update-form-data/<int:user_id>")
def user_management_update_form_data(user_id: int):
    try:
        form = request.form
        if not form:
            return jsonify({"message": "Nothing to update"}), 200

        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({"error": f"User ID {user_id} not found"}), 404

        updated = False

        # image upload
        upload_folder = "./static/images/users"
        os.makedirs(upload_folder, exist_ok=True)
        allowed_extensions = {"jpg", "jpeg", "png", "svg"}

        def save_file(file, prefix="user"):
            if file and file.filename.strip() != "":
                safe_name = secure_filename(file.filename)
                ext = safe_name.rsplit(".", 1)[-1].lower()
                if ext not in allowed_extensions:
                    raise ValueError(f"Only JPG, PNG, SVG files are allowed: {file.filename}")
                file_name = f"{prefix}_{PhnomPenhTime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
                file_path = os.path.join(upload_folder, file_name)
                file.save(file_path)
                return file_name
            return None

        profile_pic = save_file(request.files.get("profile_pic"))

        # extract form data
        name = form.get("name")
        email = form.get("email")
        telephone = form.get("telephone")
        password = form.get("password")
        role_id = form.get("role_id")
        status = form.get("status")

        # validate status
        if status and status not in ("Enable", "Disable"):
            return jsonify({"error": "Status must be Enable or Disable"}), 400

        # validate role
        role = None
        if role_id:
            role = db.session.get(UserRole, int(role_id))
            if not role:
                return jsonify({"error": f"Role ID {role_id} not found"}), 404

        # update fields if changed
        if name and name != user.name:
            user.name = name
            updated = True
        if email and email != user.email:
            user.email = email
            updated = True
        if telephone and telephone != user.telephone:
            user.telephone = telephone
            updated = True
        if password:
            user.password = password
            updated = True
        if profile_pic:
            user.profile_pic = profile_pic
            updated = True
        if role and role.id != user.role_id:
            user.role_id = role.id
            updated = True
        if status and status != user.status:
            user.status = status
            updated = True

        if not updated:
            return jsonify({"message": "Nothing to update"}), 200

        now = PhnomPenhTime.now()
        user.updated_at = now

        db.session.commit()

        updated_user = db.session.query(User).get(user_id)

        user_data = {
            "id": updated_user.id,
            "name": updated_user.name,
            "email": updated_user.email,
            "telephone": updated_user.telephone,
            "role_id": updated_user.role_id,
            "status": updated_user.status,
            "profile_pic": updated_user.profile_pic,
            "updated_at": updated_user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if updated_user.updated_at else None
        }

        return jsonify({"message": "User updated successfully", "updated_user": user_data}), 200

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/user-management/delete-data/<int:user_id>")
def user_management_delete_data(user_id: int):
    try:
        if user_id < 1:
            return jsonify({"error": "User ID must be greater than 0"}), 400

        user = db.session.query(User).get(user_id)
        if not user:
            return jsonify({"error": f"User ID {user_id} not found"}), 404

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front
# ===============================================================================================================
@app.route("/user-management")
def user_management():
    return render_template("auth/admin/user-mgt.html", title="LIM - User Management")

@app.route("/user-management/add-user")
def user_management_add():
    return render_template("auth/admin/user-mgt.html", title="LIM - Add User", page="add-user")

@app.route("/user-management/show-user")
def user_management_show():
    return render_template("auth/admin/user-mgt.html", title="LIM - Show User", page="show-user")

@app.route("/user-management/edit-user")
def user_management_edit():
    return render_template("auth/admin/user-mgt.html", title="LIM - Edit User", page="edit-user")
