from app import app
from flask import render_template
from flask import request, jsonify
from app import db
from models import ProductCategory
from utils.timezone import PhnomPenhTime
from middleware.jwt import jwt_required

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================

@app.post("/category-management/create-category")
def category_management_create_category():
    try:
        form = request.form
        if not form:
            return jsonify({"error": f"JSON form is empty"}), 400

        name = form.get("name")
        if not name:
            return jsonify({"error": f"Name is requirement!"}), 400
        description = form.get("description")

        existing_name = db.session.query(ProductCategory).filter_by(name=name).first()
        if existing_name:
            return jsonify({"error": f"Product name '{name}' already exists"}), 400

        category = ProductCategory(
            name=name,
            description=description,
            created_at=PhnomPenhTime.now(),
        )
        db.session.add(category)

        db.session.commit()

        return jsonify({
            "success": "Category created successfully"
        }), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/category-management/delete-category/<int:category_id>")
def category_management_delete_category(category_id: int):
    try:
        category = db.session.query(ProductCategory).get(category_id)
        if not category:
            return jsonify({"error": f"Category ID {category_id} not found"}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({"success": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================

@app.route("/category-management")
@jwt_required(roles=["Admin", "Superadmin"])
def category_management(role):
    categories = db.session.query(ProductCategory).all()

    return render_template(
        "auth/admin/category-mgt.html",
        title="LIM - Category Management",
        categories=categories,
        user_role=role
    )

@app.route("/category-management/add-category")
@jwt_required(roles=["Admin", "Superadmin"])
def category_management_add(role):
    return render_template("auth/admin/category-mgt.html", title="LIM - Add Category",user_role=role, page="add-category")