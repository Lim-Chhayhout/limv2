from app import app
from flask import render_template
from flask import request, jsonify
from app import db
from models import Order, OrderDetail, Customer, ShippingMethod, Product, PaymentMethod
from utils.timezone import PhnomPenhTime

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================
@app.get("/sale-management/list-json")
def sale_management_list_json():
    try:
        orders = db.session.query(Order).all()
        if not orders:
            return jsonify({"message": "No Sale found."}), 200

        results = {}
        for o in orders:
            details = db.session.query(OrderDetail).filter_by(order_id=o.id).all()
            detail_list = [
                {
                    "id": d.id,
                    "product_id": d.product_id,
                    "qty": d.qty,
                    "total_price": float(d.total_price),
                    "pre_date": d.pre_date,
                    "product_status": d.product_status,
                    "created_at": d.created_at,
                    "updated_at": d.updated_at
                }
                for d in details
            ]

            results[o.id] = {
                "order_number": o.order_number,
                "customer_id": o.customer_id,
                "payment_id": o.payment_id,
                "shipping_id": o.shipping_id,
                "total_amount": float(o.total_amount),
                "order_status": o.order_status,
                "created_at": o.created_at,
                "updated_at": o.updated_at,
                "order_details": detail_list
            }

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/sale-management/order-number")
def sale_management_order_number():
    try:
        json_form = request.json
        if not json_form:
            return jsonify({"error": "No input data provided"}), 400

        order_number = json_form.get("order_number")
        if not order_number:
            return jsonify({"error": "Missing order_number"}), 400

        order = db.session.query(Order).filter_by(order_number=order_number).first()
        if not order:
            return jsonify({"message": "No Order found."}), 200

        details = db.session.query(OrderDetail).filter_by(order_id=order.id).all()
        detail_list = [
            {
                "id": d.id,
                "product_id": d.product_id,
                "qty": d.qty,
                "total_price": float(d.total_price),
                "pre_date": d.pre_date,
                "product_status": d.product_status,
                "created_at": d.created_at,
                "updated_at": d.updated_at
            }
            for d in details
        ]

        result = {}
        result[order.order_number] = {
            "id": order.id,
            "customer_id": order.customer_id,
            "payment_id": order.payment_id,
            "shipping_id": order.shipping_id,
            "total_amount": float(order.total_amount),
            "order_status": order.order_status,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "order_details": detail_list
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.post("/sale-management/create-json")
def sale_management_create_json():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        name = data.get("name")
        email = data.get("email")
        telephone = data.get("telephone")
        address = data.get("address")
        social = data.get("social")
        payment_id = data.get("payment_id")
        shipping_id = data.get("shipping_id")
        details = data.get("order_details")

        if not all([name, telephone, address, payment_id, shipping_id, details]):
            return jsonify({"error": "Missing required fields"}), 400

        customer = db.session.query(Customer).filter_by(telephone=telephone).first()
        if customer:
            updated = False
            if name and customer.name != name:
                customer.name = name
                updated = True
            if email and customer.email != email:
                customer.email = email
                updated = True
            if address and customer.address != address:
                customer.address = address
                updated = True
            if social and customer.social != social:
                customer.social = social
                updated = True
            if updated:
                customer.updated_at = PhnomPenhTime.now()
                db.session.flush()
        else:
            customer = Customer(
                name=name,
                email=email,
                telephone=telephone,
                address=address,
                social=social,
                created_at=PhnomPenhTime.now()
            )
            db.session.add(customer)
            db.session.flush()

        payment = db.session.query(PaymentMethod).get(payment_id)
        if not payment:
            return jsonify({"error": "Payment ID not found"}), 400

        payment_id = payment.id

        shipping = db.session.query(ShippingMethod).get(shipping_id)
        if not shipping:
            return jsonify({"error": "Shipping ID not found"}), 400
        shipping_cost = float(shipping.cost)

        order_number = f"ORD-{int(PhnomPenhTime.now().timestamp())}"
        total_products = 0
        has_preorder = False
        order_details_list = []

        for d in details:
            product_id = d.get("product_id")
            qty = int(d.get("qty", 0))
            if not product_id or qty <= 0:
                continue

            product = db.session.query(Product).get(product_id)
            if not product:
                return jsonify({"error": f"Product ID {product_id} not found"}), 400

            stock = product.stock.qty if product.stock else 0
            price = float(product.detail.price) if product.detail else 0
            discount = float(product.detail.discount or 0)
            final_price = price - discount
            total_price = final_price * qty
            total_products += total_price

            if stock <= 0:
                product_status = "Pre-ordered"
                has_preorder = True
                pre_date = PhnomPenhTime.now()
            else:
                product_status = "Place-ordered"
                pre_date = None
                product.stock.qty = max(stock - qty, 0)

            order_details_list.append({
                "product_id": product_id,
                "qty": qty,
                "total_price": total_price,
                "pre_date": pre_date,
                "product_status": product_status
            })

        total_amount = total_products + shipping_cost
        order_status = "Pending" if has_preorder else "Success"

        order = Order(
            order_number=order_number,
            customer_id=customer.id,
            payment_id=payment_id,
            shipping_id=shipping_id,
            total_amount=total_amount,
            order_status=order_status
        )
        db.session.add(order)
        db.session.flush()

        order_detail_objects = []
        for od in order_details_list:
            order_detail = OrderDetail(
                order_id=order.id,
                product_id=od["product_id"],
                qty=od["qty"],
                total_price=od["total_price"],
                pre_date=od["pre_date"],
                product_status=od["product_status"]
            )
            db.session.add(order_detail)
            order_detail_objects.append({
                "product_id": od["product_id"],
                "qty": od["qty"],
                "total_price": od["total_price"],
                "pre_date": od["pre_date"],
                "product_status": od["product_status"]
            })

        db.session.commit()

        result = {
            "order": {
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": customer.name,
                "payment_id": order.payment_id,
                "shipping_id": order.shipping_id,
                "shipping_cost": shipping_cost,
                "total_amount": float(order.total_amount),
                "order_status": order.order_status,
                "created_at": order.created_at
            },
            "order_details": order_detail_objects
        }

        return jsonify({
            "message": "Sale created successfully",
            "result": result
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/sale-management/update-json/<int:order_id>")
def sale_management_update_json(order_id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        order = db.session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": f"Order ID {order_id} not found"}), 404

        updated = False
        order_data = data.get("order", {})
        customer_data = data.get("customer", {})
        details_data = data.get("order_details", [])

        # === CUSTOMER UPDATE ===
        if customer_data:
            customer = order.customer
            for field, value in customer_data.items():
                if value not in [None, ""]:
                    current = getattr(customer, field, None)
                    if current != value:
                        if field == "telephone":
                            existing = db.session.query(Customer).filter(
                                Customer.telephone == value,
                                Customer.id != customer.id
                            ).first()
                            if existing:
                                return jsonify({"error": "Telephone already used by another customer"}), 400
                        setattr(customer, field, value)
                        updated = True

        # === ORDER INFO UPDATE ===
        if order_data:
            if "payment_id" in order_data and order_data["payment_id"]:
                payment = db.session.query(PaymentMethod).get(order_data["payment_id"])
                if not payment:
                    return jsonify({"error": "Invalid payment_id"}), 400
                if order.payment_id != order_data["payment_id"]:
                    order.payment_id = order_data["payment_id"]
                    updated = True

            if "shipping_id" in order_data and order_data["shipping_id"]:
                shipping = db.session.query(ShippingMethod).get(order_data["shipping_id"])
                if not shipping:
                    return jsonify({"error": "Invalid shipping_id"}), 400
                if order.shipping_id != order_data["shipping_id"]:
                    order.shipping_id = order_data["shipping_id"]
                    updated = True

            if "order_status" in order_data and order_data["order_status"]:
                new_status = order_data["order_status"]
                if new_status not in ["Pending", "Success"]:
                    return jsonify({"error": "Invalid order_status value"}), 400
                if order.order_status != new_status:
                    order.order_status = new_status
                    updated = True

        # === ORDER DETAILS UPDATE ===
        total_products = 0
        has_preorder = False

        if details_data:
            db.session.query(OrderDetail).filter_by(order_id=order.id).delete()
            for d in details_data:
                product_id = d.get("product_id")
                qty = d.get("qty", 0)
                if not product_id or qty <= 0:
                    continue

                product = db.session.query(Product).get(product_id)
                if not product:
                    return jsonify({"error": f"Product ID {product_id} not found"}), 400

                stock = product.stock.qty if product.stock else 0
                price = float(product.detail.price) if product.detail else 0
                discount = float(product.detail.discount or 0)
                final_price = price - discount
                total_price = final_price * qty
                total_products += total_price

                if stock <= 0:
                    product_status = "Pre-ordered"
                    has_preorder = True
                    pre_date = PhnomPenhTime.now()
                else:
                    product_status = "Place-ordered"
                    pre_date = None
                    product.stock.qty = max(stock - qty, 0)

                db.session.add(OrderDetail(
                    order_id=order.id,
                    product_id=product_id,
                    qty=qty,
                    total_price=total_price,
                    pre_date=pre_date,
                    product_status=product_status
                ))
            updated = True

        shipping = db.session.query(ShippingMethod).get(order.shipping_id)
        shipping_cost = float(shipping.cost) if shipping else 0
        total_amount = total_products + shipping_cost
        order.total_amount = total_amount

        if not order_data.get("order_status"):
            order.order_status = "Pending" if has_preorder else "Success"

        if updated:
            order.updated_at = PhnomPenhTime.now()
            db.session.commit()
            message = "Order updated successfully"
        else:
            message = "Nothing to update"

        updated_order = db.session.query(Order).get(order.id)
        details = db.session.query(OrderDetail).filter_by(order_id=order.id).all()

        order_detail_objects = [{
            "product_id": d.product_id,
            "qty": d.qty,
            "total_price": float(d.total_price),
            "pre_date": d.pre_date,
            "product_status": d.product_status
        } for d in details]

        result = {
            "order": {
                "id": updated_order.id,
                "order_number": updated_order.order_number,
                "payment_id": updated_order.payment_id,
                "shipping_id": updated_order.shipping_id,
                "shipping_cost": float(shipping_cost),
                "total_amount": float(updated_order.total_amount),
                "order_status": updated_order.order_status,
                "updated_at": updated_order.updated_at
            },
            "customer": {
                "id": updated_order.customer.id,
                "name": updated_order.customer.name,
                "email": updated_order.customer.email,
                "telephone": updated_order.customer.telephone,
                "address": updated_order.customer.address,
                "social": updated_order.customer.social
            },
            "order_details": order_detail_objects
        }

        return jsonify({"message": message, "result": result}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.post("/sale-management/delete-json/<int:order_id>")
def sale_management_delete_json(order_id):
    try:
        order = db.session.query(Order).get(order_id)
        if not order:
            return jsonify({"error": f"Order ID {order_id} not found"}), 404

        db.session.query(OrderDetail).filter_by(order_id=order.id).delete()
        db.session.delete(order)
        db.session.commit()

        return jsonify({
            "message": f"Order ID {order_id} deleted successfully"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================
@app.route("/sale-management")
def sale_management():
    return render_template("auth/admin/sale-mgt.html", title="LIM - Sale Management")
