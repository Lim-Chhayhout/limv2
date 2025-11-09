from app import app
from flask import render_template
@app.route("/product-detail")
def product_detail():
    return render_template("pages/detail.html", title="LIM - Kdmv")