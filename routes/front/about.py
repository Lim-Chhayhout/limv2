from app import app
from flask import render_template, session

@app.route("/about")
def about():
    cart_list = session.get("cart", {})
    total_qty = 0
    for item in cart_list.values():
        total_qty += item["qty"]

    return render_template("pages/about.html", title="LIM - Kdmv", total_qty=total_qty)
