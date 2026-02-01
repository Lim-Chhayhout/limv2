from app import app,db
from flask import render_template, session, jsonify, request, redirect
from models import Product, ShippingMethod, Order, OrderDetail, Customer
from utils import PhnomPenhTime


@app.route("/checkout")
def checkout():
    ship = db.session.query(ShippingMethod).filter_by(status="Active").all()
    cart = session.get("cart", {})

    if not cart:
        return redirect("/cart")

    new_cart = {}
    removed_items = []
    total_qty = 0
    subtotal = 0

    for pid, item in list(cart.items()):
        product = Product.query.get(int(pid))
        if not product or product.status != "Active":
            removed_items.append({
                "name": item["name"],
                "image": item.get("image", "")
            })
            continue

        if product.detail.status == "In-stock" and product.stock.qty == 0:
            removed_items.append({
                "name": product.detail.name,
                "image": product.detail.image1
            })
            del cart[pid]
            continue

        if product.detail.status != "Pre-order" and item["qty"] > product.stock.qty:
            removed_items.append({
                "name": product.detail.name,
                "image": product.detail.image1
            })
            item["qty"] = product.stock.qty

        item["name"] = product.detail.name
        item["current_price"] = float(product.detail.price)
        item["discount"] = float(product.detail.discount)
        item["price"] = item["current_price"] * (1 - item["discount"] / 100)
        item["image"] = product.detail.image1
        item["condition"] = product.detail.condition
        item["status"] = product.detail.status
        item["stock_qty"] = product.stock.qty

        new_cart[pid] = item
        total_qty += item["qty"]
        subtotal += item["qty"] * item["price"]

    session["cart"] = new_cart
    session.modified = True

    return render_template(
        "pages/checkout.html",
        title="LIM - Kdmv",
        cart=new_cart,
        total_qty=total_qty,
        subtotal=subtotal,
        shipping=ship,
        removed_items=removed_items
    )


@app.get("/shipping/<int:shipping_id>")
def shipping(shipping_id):
    if request.headers.get("X-Requested-With") != "XMLHttpRequest":
        return redirect("/checkout")

    ship = db.session.query(ShippingMethod).filter_by(id=shipping_id).first()
    if not ship:
        return jsonify({"error": "Shipping not found"}), 404

    if not session.get("cart"):
        return jsonify({"error": "Unauthorized"}), 403

    cart = session.get("cart", {})

    subtotal = 0

    for pid, item in cart.items():
        subtotal += item["qty"] * item["price"]

    total = subtotal + float(ship.cost)

    session["ship"] = {
        "id": ship.id,
        "type": ship.type,
        "cost": float(ship.cost)
    }
    session.modified = True

    return jsonify({
        "shipping_type": ship.type,
        "shipping_cost": float(ship.cost),
        "total": float(total)
    })

@app.post("/checkout-post")
def checkout_post():
    if not session.get("cart") or not session.get("ship"):
        return redirect("/cart")

    form = request.form
    ship = session.get("ship", {})
    cart = session.get("cart", {})

    payment = form.get("payment")
    if not payment:
        return jsonify({"error": "Payment method is required"}), 400

    name = form.get("name")
    email = form.get("email")
    phone = form.get("phone")
    address = form.get("address")
    social = form.get("social")
    country = form.get("country")
    city = form.get("city")
    district = form.get("district")

    if not address:
        return jsonify({"error": "Address is required"}), 400

    customer_address = f"{address}, {district}, {city}, {country}."

    subtotal = 0.0
    ship_cost = float(ship.get("cost", 0))
    order_details = []
    stock_errors = []

    for pid, item in cart.items():
        product = Product.query.get(pid)
        if not product or product.status != "Active":
            stock_errors.append(f"Product not found: {item.get('name', 'Unknown')}")
            continue
        if not product:
            stock_errors.append(f"Product not found: {item.get('name', 'Unknown')}")
            continue

        product_stock = product.stock
        if item["status"] == "In-stock" and product_stock.qty < item["qty"]:
            stock_errors.append(f"Not enough stock for product {product.detail.name}")

    if stock_errors:
        return redirect("/checkout")

    existing_customer = Customer.query.filter(
        Customer.name == name,
        Customer.telephone == phone,
        Customer.email == email,
        Customer.address == customer_address
    ).first()

    if existing_customer:
        customer_id = existing_customer.id
    else:
        try:
            customer = Customer(
                name=name,
                email=email,
                telephone=phone,
                address=customer_address,
                social=social
            )
            db.session.add(customer)
            db.session.flush()
            customer_id = customer.id
        except Exception as e:
            return jsonify({"error": f"Failed to create customer: {str(e)}"}), 500

    for pid, item in cart.items():
        product = Product.query.get(pid)
        product_stock = product.stock

        price_at_purchase = item["price"]
        total_price = price_at_purchase * item["qty"]

        if item["status"] == "In-stock":
            product_status = "Place-ordered"
            product_stock.qty -= item["qty"]
            pre_date = None
        else:
            product_status = "Pre-ordered"
            pre_date = PhnomPenhTime.now()

        subtotal += total_price

        order_details.append(OrderDetail(
            product_id=pid,
            product_price=price_at_purchase,
            qty=item["qty"],
            subtotal=total_price,
            pre_date=pre_date,
            product_status=product_status
        ))

    date = PhnomPenhTime.now().strftime("%m%d%Y")
    latest_order = db.session.query(Order.order_number)\
        .filter(Order.order_number.like(f"ord-{date}%"))\
        .order_by(Order.order_number.desc())\
        .first()

    counter = int(latest_order.order_number[-3:]) + 1 if latest_order else 1
    formatted_counter = f"{counter:03}"

    total_amount = subtotal + ship_cost

    order_status = "Success"
    for item in order_details:
        if item.product_status == "Pre-ordered":
            order_status = "Pending"

    order = Order(
        order_number=f"ord-{date}{formatted_counter}",
        customer_id=customer_id,
        payment_id=payment,
        shipping_id=ship.get("id"),
        total_amount=total_amount,
        order_status=order_status
    )
    db.session.add(order)
    db.session.flush()

    for detail in order_details:
        detail.order_id = order.id
        db.session.add(detail)

    db.session.commit()
    session.pop("cart", None)

    session["order_success"] = order.id
    return redirect("/success")
