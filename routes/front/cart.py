from app import app
from flask import render_template
@app.route("/cart")
def cart():
    return render_template("pages/cart.html", title="LIM - Kdmv")