from app import app, db
from flask import render_template, session, redirect, url_for, request, jsonify
from models import Product, ProductStock


@app.route("/post-to-cart/<int:product_id>", methods=["GET", "POST"])
def post_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        return "Product not found", 404

    cart_list = session.get("cart", {})
    pid = str(product_id)

    if pid not in cart_list:
        cart_list[pid] = {
            "id": product.id,
            "name": product.detail.name,
            "price": float(product.detail.price),
            "image": product.detail.image1,
            "condition": product.detail.condition,
            "status": product.detail.status,
            "stock_qty": product.stock.qty,
            "qty": 1
        }
    else:
        cart_list[pid].setdefault("qty", 1)

    session["cart"] = cart_list
    session.modified = True

    return redirect(url_for("cart"))


@app.route("/remove-from-cart/<int:product_id>")
def remove_cart(product_id):
    cart_list = session.get("cart", {})
    pid = str(product_id)

    if pid in cart_list:
        del cart_list[pid]

    session["cart"] = cart_list
    return redirect(request.referrer or url_for("cart"))

@app.get("/api/cart/dec/<int:product_id>")
def api_dec_qty(product_id):
    cart = session.get("cart", {})
    pid = str(product_id)

    if pid in cart:
        cart[pid].setdefault("qty", 1)
        if cart[pid]["qty"] > 1:
            cart[pid]["qty"] -= 1

    session["cart"] = cart
    return jsonify({"qty": cart[pid]["qty"]})


@app.get("/api/cart/inc/<int:product_id>")
def api_inc_qty(product_id):
    check_only = request.args.get("check") == "1"

    cart = session.get("cart", {})
    pid = str(product_id)

    product = db.session.query(Product).filter_by(id=product_id).first()
    stock = db.session.query(ProductStock.qty).filter_by(product_id=product_id).scalar()

    if check_only:
        return jsonify({
            "qty": cart.get(pid, {}).get("qty", 1),
            "stock": stock,
            "status": product.detail.status
        })

    if pid in cart:
        cart[pid].setdefault("qty", 1)

        if product.detail.status == "Pre-order":
            if cart[pid]["qty"] < 10:
                cart[pid]["qty"] += 1
        else:
            if stock and cart[pid]["qty"] < stock:
                cart[pid]["qty"] += 1

    session["cart"] = cart

    return jsonify({
        "qty": cart[pid]["qty"],
        "stock": stock,
        "status": product.detail.status
    })


@app.get("/api/cart/fix-stock")
def api_fix_stock():
    cart = session.get("cart", {})
    changed = False

    for pid, item in cart.items():
        product_id = int(pid)
        product = db.session.query(Product).filter_by(id=product_id).first()
        stock = db.session.query(ProductStock.qty).filter_by(product_id=product_id).scalar()

        if product.detail.status != "Pre-order":
            if stock and item["qty"] > stock:
                item["qty"] = stock
                changed = True

    if changed:
        session["cart"] = cart

    return jsonify(cart)


@app.route("/cart")
def cart():
    session.pop("removed_items", None)
    cart_list = session.get("cart", {})
    new_cart = {}
    total_qty = 0
    subtotal = 0

    for pid, item in cart_list.items():
        product = Product.query.get(int(pid))
        if not product or product.status != "Active":
            continue

        if product.detail.status == "In-stock" and product.stock.qty == 0:
            continue

        item.setdefault("qty", 1)

        if product.detail.status != "Pre-order" and item["qty"] > product.stock.qty:
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
        "pages/cart.html",
        cart_list=new_cart,
        total_qty=total_qty,
        subtotal=subtotal
    )