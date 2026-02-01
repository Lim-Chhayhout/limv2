from app import app
from flask import render_template, session
from models import Product, ProductDetail

@app.route("/filter/<string:filter_by>")
def filter_list(filter_by):
    q = Product.query.join(ProductDetail).filter(Product.status == "Active")

    if filter_by in ["New", "LikeNew", "2ndHand"]:
        q = q.filter(ProductDetail.condition == filter_by)

    elif filter_by in ["In-stock", "Pre-order"]:
        q = q.filter(ProductDetail.status == filter_by)

    else:
        q = q.filter(False)

    cart_list = session.get("cart", {})
    total_qty = sum(item["qty"] for item in cart_list.values())

    products = q.all()
    return render_template(
        "pages/filter.html",
        products=products,
        filter_by=filter_by,
        title=f"Filter: {filter_by}",
        total_qty=total_qty
    )