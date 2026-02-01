from app import app, db
from flask import render_template, session
from models import Product

@app.route("/<product_name>/<int:product_id>")
def product_detail(product_name, product_id):
    product = db.session.query(Product).filter_by(id=product_id).first()
    if not product:
        return "Product not found", 404

    cart = session.get("cart", {})

    total_qty = sum(item["qty"] for item in cart.values())

    related_products = (
        Product.query
        .filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
            Product.status == "Active"
        )
        .all()
    )

    return render_template(
        "pages/detail.html",
        title=f"LIM - {product_name}",
        product=product,
        products=related_products,
        total_qty=total_qty
    )
