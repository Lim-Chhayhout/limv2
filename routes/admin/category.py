from app import app
from flask import render_template
from flask import request, jsonify
from app import db
from models import ProductCategory
from utils.timezone import PhnomPenhTime

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================
@app.get("/category-management/list-json")
def category_management_list_json():
    try:
        categories = db.session.query(ProductCategory).all()
        if not categories:
            return jsonify({"message": "No category found"}), 404

        results = {}
        for c in categories:
            results[c.id] = {
                "name": c.name,
                "description": c.description,
                "created_at": c.created_at,
                "updated_at": c.updated_at
            }

        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/category-management/by_id/<int:category_id>")
def category_management_by_id(category_id: int):
    try:
        category = db.session.query(ProductCategory).get(category_id)
        if not category:
            return jsonify({"error": f"ID {category_id} not found"}), 404

        result = {
            category.id: {
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at,
                "updated_at": category.updated_at
            }
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/category-management/create-json")
def category_management_create_json():
    try:
        json_form = request.json
        if not json_form:
            return jsonify({"error": f"JSON form is empty"}), 400

        name = json_form.get("name")
        if not name:
            return jsonify({"error": f"Name is requirement!"}), 400
        description = json_form.get("description")

        existing_name = db.session.query(ProductCategory).filter_by(name=name).first()
        if existing_name:
            return jsonify({"error": f"Product name '{name}' already exists"}), 400

        # transactional insert
        category = ProductCategory(
            name=name,
            description=description,
            created_at=PhnomPenhTime.now(),
        )
        db.session.add(category)

        db.session.commit()

        created_category = {
            category.id: {
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at,
                "updated_at": category.updated_at
            }
        }

        return jsonify({
            "message": "Category created successfully",
            "result": created_category
        }), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/category-management/update-json/<int:category_id>")
def category_management_update_json(category_id: int):
    try:
        json_form = request.json
        if not json_form:
            return jsonify({"message": "Nothing to update!"}), 200

        category = db.session.query(ProductCategory).get(category_id)
        if not category:
            return jsonify({"error": f"Category ID {category_id} not found"}), 404

        updated = False

        name = json_form.get("name")
        description = json_form.get("description")

        if name and name != category.name:
            existing_category = (
                db.session.query(ProductCategory)
                .filter(ProductCategory.name == name, ProductCategory.id != category_id)
                .first()
            )
            if existing_category:
                return jsonify({"error": f"Category name '{name}' already exists"}), 400
            category.name = name
            updated = True

        if description and description != category.description:
            category.description = description
            updated = True

        if not updated:
            return jsonify({"error": "Nothing to update!"}), 400

        category.updated_at = PhnomPenhTime.now()

        db.session.commit()

        updated_category = {
            category.id: {
                "name": category.name,
                "description": category.description,
                "created_at": category.created_at,
                "updated_at": category.updated_at
            }
        }

        return jsonify({
            "message": "Category updated successfully",
            "result": updated_category
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/category-management/delete-json/<int:category_id>")
def category_management_delete_json(category_id: int):
    try:
        category = db.session.query(ProductCategory).get(category_id)
        if not category:
            return jsonify({"error": f"Category ID {category_id} not found"}), 404

        db.session.delete(category)
        db.session.commit()

        return jsonify({"message": "Category deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================

@app.route("/category-management")
def category_management():
    return render_template("auth/admin/category-mgt.html", title="LIM - Category Management")

@app.route("/category-management/add-category")
def category_management_add():
    return render_template("auth/admin/category-mgt.html", title="LIM - Add Category", page="add-category")