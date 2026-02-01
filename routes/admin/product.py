from app import app
from flask import render_template
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import db
from models import Product, ProductDetail, ProductStock, ProductCategory
from utils.timezone import PhnomPenhTime
import os
from middleware.jwt import jwt_required
# ===============================================================================================================
# api with backend
# ===============================================================================================================
@app.post("/product-management/create-product")
def product_management_create_product():
    try:
        form = request.form
        if not form:
            return jsonify({"error": "Request body is empty"}), 400

        file_obj1 = request.files.get("image1")
        file_obj2 = request.files.get("image2")

        code = form.get("code")
        category_id = form.get("category_id")
        product_status = form.get("product_status")
        detail_status = form.get("detail_status")
        brand = form.get("brand")
        name = form.get("name")
        price = form.get("price")
        discount = form.get("discount") or 0
        condition = form.get("condition")
        description = form.get("description")
        review = form.get("review")
        qty = form.get("qty") or 0

        required_fields = {
            "code": code,
            "category_id": category_id,
            "name": name,
            "price": price,
            "brand": brand,
            "condition": condition
        }
        for key, value in required_fields.items():
            if not value:
                return jsonify({"error": f"{key.capitalize()} is required"}), 400

        category = db.session.get(ProductCategory, int(category_id))
        if not category:
            return jsonify({"error": f"Category ID {category_id} not found"}), 400

        if product_status not in ("Pending", "Active"):
            return jsonify({"error": f"Status must be one of Pending, Active"}), 400

        if detail_status not in ("In-stock", "Pre-order"):
            return jsonify({"error": f"Detail status must be one of In-stock, Pre-order"}), 400

        if condition not in ["New", "LikeNew", "2ndHand"]:
            return jsonify({"error": f"Condition must be one of New, LikeNew, 2ndHand"}), 400

        existing_product = db.session.query(Product).filter_by(code=code).first()
        if existing_product:
            return jsonify({"error": f"Product code '{code}' already exists"}), 400

        image1 = "product_icon.png"
        if file_obj1 and file_obj1.filename.strip() != "":
            safe_name = secure_filename(file_obj1.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG files are allowed"}), 400

            upload_folder = "./static/images/products"
            os.makedirs(upload_folder, exist_ok=True)
            file_name = f"product_image1_{code}_{safe_name}"
            file_path = os.path.join(upload_folder, file_name)
            file_obj1.save(file_path)
            image1 = file_name

        image2 = "product_icon.png"
        if file_obj2 and file_obj2.filename.strip() != "":
            safe_name = secure_filename(file_obj2.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG files are allowed"}), 400

            upload_folder = "./static/images/products"
            os.makedirs(upload_folder, exist_ok=True)
            file_name = f"product_image2_{code}_{safe_name}"
            file_path = os.path.join(upload_folder, file_name)
            file_obj2.save(file_path)
            image2 = file_name

        product = Product(
            code=code,
            category_id=int(category_id),
            status=product_status,
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
            status=detail_status,
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

        return jsonify({
            "success": "Product created successfully",
            "product_id" : product.id
        }), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/product-management/update-product/<int:product_id>")
def product_management_update_product(product_id):
    try:
        form = request.form
        if not form:
            return jsonify({"error": "Request body is empty"}), 400

        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        detail = product.detail
        stock = product.stock
        updated = False

        file_obj1 = request.files.get("image1")
        file_obj2 = request.files.get("image2")

        code = form.get("code")
        category_id = form.get("category_id")
        product_status = form.get("product_status")
        detail_status = form.get("detail_status")
        brand = form.get("brand")
        name = form.get("name")
        price = form.get("price")
        discount = form.get("discount") or 0
        condition = form.get("condition")
        description = form.get("description")
        review = form.get("review")
        qty = form.get("qty") or 0

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

        if product_status and product_status != product.status:
            if product_status not in ["Pending", "Active"]:
                return jsonify({"error": "Status must be Pending or Active"}), 400
            product.status = product_status
            updated = True

        upload_folder = "./static/images/products"
        os.makedirs(upload_folder, exist_ok=True)

        if file_obj1 and file_obj1.filename.strip():
            safe_name = secure_filename(file_obj1.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG files are allowed"}), 400
            file_name = f"product_image1_{product.code}_{safe_name}"
            file_obj1.save(os.path.join(upload_folder, file_name))
            detail.image1 = file_name
            updated = True

        if file_obj2 and file_obj2.filename.strip():
            safe_name = secure_filename(file_obj2.filename)
            ext = safe_name.rsplit(".", 1)[-1].lower()
            if ext not in {"jpg", "jpeg", "png", "svg"}:
                return jsonify({"error": "Only JPG, JPEG, PNG, SVG files are allowed"}), 400
            file_name = f"product_image2_{product.code}_{safe_name}"
            file_obj2.save(os.path.join(upload_folder, file_name))
            detail.image2 = file_name
            updated = True

        if not detail:
            detail = ProductDetail(product_id=product.id)
            db.session.add(detail)

        if brand: detail.brand = brand; updated = True
        if name: detail.name = name; updated = True
        if price: detail.price = float(price); updated = True
        if discount: detail.discount = float(discount); updated = True
        if condition:
            if condition not in ["New", "LikeNew", "2ndHand"]:
                return jsonify({"error": "Condition must be New, LikeNew, or 2ndHand"}), 400
            detail.condition = condition; updated = True
        if detail_status and detail_status != detail.status:
            if detail_status not in ["In-stock", "Pre-order"]:
                return jsonify({"error": "Detail status must be In-stock or Pre-order"}), 400
            detail.status = detail_status; updated = True
        if description: detail.description = description; updated = True
        if review: detail.review = review; updated = True

        # Update stock
        if not stock:
            stock = ProductStock(product_id=product.id)
            db.session.add(stock)
        if qty:
            stock.qty = int(qty); updated = True

        if not updated:
            return jsonify({"message": "Nothing to update"}), 200

        product.updated_at = PhnomPenhTime.now()
        detail.updated_at = PhnomPenhTime.now()
        stock.updated_at = PhnomPenhTime.now()

        db.session.commit()

        return jsonify({"success": "Product updated successfully", "product_id": product.id}), 200

    except ValueError as ve:
        db.session.rollback()
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/product-management/delete-product/<int:product_id>")
def product_management_delete_product(product_id):
    try:
        product = db.session.query(Product).get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        detail = db.session.query(ProductDetail).filter_by(product_id=product_id).first()
        stock = db.session.query(ProductStock).filter_by(product_id=product_id).first()

        if detail:
            folder = "./static/images/products"
            if detail.image1 and detail.image1 != "product_icon.png":
                path1 = os.path.join(folder, detail.image1)
                if os.path.exists(path1):
                    os.remove(path1)
            if detail.image2 and detail.image2 != "product_icon.png":
                path2 = os.path.join(folder, detail.image2)
                if os.path.exists(path2):
                    os.remove(path2)
            db.session.delete(detail)

        if stock:
            db.session.delete(stock)

        db.session.delete(product)
        db.session.commit()

        return jsonify({"success": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================

@app.route("/product-management")
@jwt_required(roles=["Admin", "Superadmin"])
def product_management(role):
    products = db.session.query(Product).order_by(Product.code.asc()).all()
    return render_template(
        "auth/admin/product-mgt.html",
        title="LIM - Product Management",
        products=products,
        user_role=role,
    )

@app.route("/product-management/add-product")
@jwt_required(roles=["Admin", "Superadmin"])
def product_management_add(role):
    categories = db.session.query(ProductCategory).all()
    return render_template("auth/admin/product-mgt.html", title="LIM - Add Product", page="add-product", user_role=role, categories=categories)

@app.route("/product-management/show-product/<int:product_id>")
@jwt_required(roles=["Admin", "Superadmin"])
def product_management_show(product_id, role):
    product = db.session.query(Product).get(product_id)
    if not product:
        return "Product not found", 404
    return render_template("auth/admin/product-mgt.html", user_role=role, title=f"LIM - Show {product.detail.name}", page="show-product", product=product)

@app.route("/product-management/edit-product/<int:product_id>")
@jwt_required(roles=["Admin", "Superadmin"])
def product_management_edit(product_id, role):
    product = db.session.query(Product).get(product_id)
    categoies = db.session.query(ProductCategory).all()
    if not product:
        return "Product not found", 404
    return render_template("auth/admin/product-mgt.html",user_role=role, title=f"LIM - Edit {product.detail.name}", page="edit-product", product=product, categories=categoies)