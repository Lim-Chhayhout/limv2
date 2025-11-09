from app import app
from flask import render_template
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import db
from models import Product, ProductDetail, ProductStock, ProductCategory
from utils.timezone import PhnomPenhTime
import os

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================
@app.get("/product-management/list-json")
def product_management_list_json():
    try:
        products = db.session.query(Product).all()
        if not products:
            return jsonify({"message": "No Product found."}), 200

        results = {}
        for p in products:
            detail = p.detail
            stock = p.stock
            category = p.category

            results[p.id] = {
                "code": p.code,
                "status": p.status,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "category_name": category.name,
                "stock_qty": stock.qty if stock else 0,
                "brand": detail.brand,
                "name": detail.name,
                "price": detail.price,
                "discount": detail.discount if detail else 0,
                "condition": detail.condition,
                "description": detail.description,
                "review": detail.review,
                "image1": detail.image1,
                "image2": detail.image2
            }

        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/product-management/by-id/<int:product_id>")
def product_management_by_id(product_id):
    try:
        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        detail = product.detail
        stock = product.stock
        category = product.category

        result = {
            product.id: {
                "code": product.code,
                "status": product.status,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "category_name": category.name,
                "stock_qty": stock.qty,
                "brand": detail.brand,
                "name": detail.name,
                "price": detail.price,
                "discount": detail.discount,
                "condition": detail.condition,
                "description": detail.description,
                "review": detail.review,
                "image1": detail.image1,
                "image2": detail.image2
            }
        }

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/product-management/create-form-data")
def product_management_create_form_data():
    try:
        form = request.form
        if not form:
            return jsonify({"error": "Request body is empty"}), 400

        # images upload
        upload_folder = "./static/images/products"
        os.makedirs(upload_folder, exist_ok=True)
        allowed_extensions = {"jpg", "jpeg", "png", "svg"}

        def save_file(file, prefix="product"):
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

        image1 = save_file(request.files.get("image1"))
        image2 = save_file(request.files.get("image2"))

        # extract form data
        code = form.get("code")
        category_id = form.get("category_id")
        status = form.get("status")
        brand = form.get("brand")
        name = form.get("name")
        price = form.get("price")
        discount = form.get("discount") or 0
        condition = form.get("condition")
        description = form.get("description")
        review = form.get("review")
        qty = form.get("qty") or 0

        # validation
        required_fields = {
            "code": code,
            "category_id": category_id,
            "name": name,
            "price": price,
            "brand": brand,
            "condition": condition,
            "status": status
        }
        for key, value in required_fields.items():
            if not value:
                return jsonify({"error": f"{key.capitalize()} is required"}), 400

        category = db.session.get(ProductCategory, int(category_id))
        if not category:
            return jsonify({"error": f"Category ID {category_id} not found"}), 400

        if status not in ("Pending", "Active"):
            return jsonify({"error": f"Status must be one of Pending, Active"}), 400

        if condition not in ["New", "LikeNew", "2ndHand"]:
            return jsonify({"error": f"Condition must be one of New, LikeNew, 2ndHand"}), 400

        # duplicate
        existing_product = db.session.query(Product).filter_by(code=code).first()
        if existing_product:
            return jsonify({"error": f"Product code '{code}' already exists"}), 400

        # transactional insert
        product = Product(
            code=code,
            category_id=int(category_id),
            status=status,
            created_at=PhnomPenhTime.now(),
        )
        db.session.add(product)
        db.session.flush()

        detail = ProductDetail(
            product_id=product.id,
            brand=brand,
            name=name,
            price=float(price),
            discount=float(discount),
            condition=condition,
            description=description,
            review=review,
            image1=image1,
            image2=image2,
            created_at=PhnomPenhTime.now(),
            updated_at=PhnomPenhTime.now()
        )
        db.session.add(detail)

        stock = ProductStock(
            product_id=product.id,
            qty=int(qty),
            created_at=PhnomPenhTime.now(),
            updated_at=PhnomPenhTime.now()
        )
        db.session.add(stock)

        db.session.commit()

        created_product = {
            product.id: {
                "code": product.code,
                "status": product.status,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "category_name": category.name if category else None,
                "stock_qty": stock.qty if stock else 0,
                "brand": detail.brand if detail else None,
                "name": detail.name if detail else None,
                "price": detail.price if detail else None,
                "discount": detail.discount if detail else 0,
                "condition": detail.condition if detail else None,
                "description": detail.description if detail else None,
                "review": detail.review if detail else None,
                "image1": detail.image1 if detail else None,
                "image2": detail.image2 if detail else None
            }
        }

        return jsonify({
            "message": "Product created successfully",
            "result": created_product
        }), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/product-management/update-form-data/<int:product_id>")
def product_management_update_form_data(product_id: int):
    try:
        form = request.form
        if not form:
            return jsonify({"message": "Nothing to update"}), 200

        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        detail = product.detail
        stock = product.stock
        updated = False

        # images upload
        upload_folder = "./static/images/products"
        os.makedirs(upload_folder, exist_ok=True)
        allowed_extensions = {"jpg", "jpeg", "png", "svg"}

        def save_file(file, prefix="product"):
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

        image1 = save_file(request.files.get("image1"))
        image2 = save_file(request.files.get("image2"))

        # extract form data
        code = form.get("code")
        category_id = form.get("category_id")
        status = form.get("status")
        brand = form.get("brand")
        name = form.get("name")
        price = form.get("price")
        discount = form.get("discount")
        condition = form.get("condition")
        description = form.get("description")
        review = form.get("review")
        qty = form.get("qty")

        # product fields
        if code and code != product.code:
            existing_product = db.session.query(Product).filter(Product.code == code, Product.id != product_id).first()
            if existing_product:
                return jsonify({"error": f"Product code '{code}' already exists"}), 400
            product.code = code
            updated = True

        if category_id and int(category_id) != product.category_id:
            category = db.session.get(ProductCategory, int(category_id))
            if not category:
                return jsonify({"error": f"Category ID {category_id} not found"}), 400
            product.category_id = int(category_id)
            updated = True

        if status and status != product.status:
            if status not in ["Pending", "Active"]:
                return jsonify({"error": "Status must be Pending or Active"}), 400
            product.status = status
            updated = True

        # detail fields
        if not detail:
            detail = ProductDetail(product_id=product.id)
            db.session.add(detail)
        if brand:
            detail.brand = brand
            updated = True
        if name:
            detail.name = name
            updated = True
        if price:
            detail.price = float(price)
            updated = True
        if discount:
            detail.discount = float(discount)
            updated = True
        if condition:
            if condition not in ["New", "LikeNew", "2ndHand"]:
                return jsonify({"error": "Condition must be New, LikeNew, or 2ndHand"}), 400
            detail.condition = condition
            updated = True
        if description:
            detail.description = description
            updated = True
        if review:
            detail.review = review
            updated = True
        if image1:
            detail.image1 = image1
            updated = True
        if image2:
            detail.image2 = image2
            updated = True

        # stock
        if not stock:
            stock = ProductStock(product_id=product.id)
            db.session.add(stock)
        if qty:
            stock.qty = int(qty)
            updated = True

        if not updated:
            return jsonify({"message": "Nothing to update"}), 200

        product.updated_at = PhnomPenhTime.now()
        detail.updated_at = PhnomPenhTime.now()
        stock.updated_at = PhnomPenhTime.now()

        db.session.commit()

        updated_product = db.session.query(Product).get(product.id)
        detail = updated_product.detail
        stock = updated_product.stock

        product_data = {
            "id": updated_product.id,
            "code": updated_product.code,
            "category_id": updated_product.category_id,
            "status": updated_product.status,
            "brand": detail.brand if detail else None,
            "name": detail.name if detail else None,
            "price": detail.price if detail else None,
            "discount": detail.discount if detail else None,
            "condition": detail.condition if detail else None,
            "description": detail.description if detail else None,
            "review": detail.review if detail else None,
            "image1": detail.image1 if detail else None,
            "image2": detail.image2 if detail else None,
            "qty": stock.qty if stock else None,
            "updated_at": updated_product.updated_at.strftime(
                "%Y-%m-%d %H:%M:%S") if updated_product.updated_at else None
        }

        return jsonify({"message": "Product updated successfully", "updated_product": product_data}), 200
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/product-management/delete-data/<int:product_id>")
def product_management_delete_data(product_id: int):
    try:
        if product_id < 1:
            return jsonify({"error": "Product ID must be greater than 0"}), 400

        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        detail = db.session.query(ProductDetail).filter_by(product_id=product_id).first()
        stock = db.session.query(ProductStock).filter_by(product_id=product_id).first()

        if detail:
            db.session.delete(detail)
        if stock:
            db.session.delete(stock)

        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================
@app.route("/product-management")
def product_management():
    return render_template("auth/admin/product-mgt.html", title="LIM - Product Management")

@app.route("/product-management/add-product")
def product_management_add():
    return render_template("auth/admin/product-mgt.html", title="LIM - Add Product", page="add-product")

@app.route("/product-management/show-product")
def product_management_show():
    return render_template("auth/admin/product-mgt.html", title="LIM - Show Product", page="show-product")

@app.route("/product-management/edit-product")
def product_management_edit():
    return render_template("auth/admin/product-mgt.html", title="LIM - Edit User", page="edit-product")