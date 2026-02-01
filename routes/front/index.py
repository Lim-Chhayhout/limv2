from app import app, db
from flask import render_template, request, jsonify, session, abort
from models import Product, Poster
from sqlalchemy.exc import OperationalError

@app.route("/")
def index():
    try:
        products = db.session.query(Product).filter_by(status="Active").all()
        posters = db.session.query(Poster).filter_by(status="Active").all()
    except OperationalError:
        return abort(503)

    cart_list = session.get("cart", {})
    total_qty = 0
    for item in cart_list.values():
        total_qty = item["qty"]


    return render_template("pages/index.html", title="LIM - Kdmv", products=products, total_qty=total_qty, posters=posters)

@app.route("/search-product")
def search_product():
    key = request.args.get("key", "").strip()
    if key == "":
        return jsonify([])

    results = Product.query.filter(Product.code.like(f"{key}%")).filter_by(status='Active').limit(5).all()

    data = []
    for p in results:
        data.append({
            "id": p.id,
            "code": p.code,
            "name": p.detail.name
        })

    return jsonify(data)

@app.route("/quick-search")
def quick_search():
    results = (
        Product.query
        .filter_by(status='Active')
        .order_by(Product.id.desc())
        .limit(3)
        .all()
    )

    data = []
    for p in results:
        data.append({
            "id": p.id,
            "code": p.code,
            "name": p.detail.name
        })

    return jsonify(data)

