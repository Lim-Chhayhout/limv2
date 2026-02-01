from flask import render_template
from sqlalchemy import func
from app import app, db
from middleware.jwt import jwt_required
from models import Order, Product
from utils.timezone import PhnomPenhTime
from datetime import timedelta


@app.route("/dashboard")
@jwt_required(roles=["Superadmin"])
def dashboard(role):
    now = PhnomPenhTime.now()

    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    today_sales = (
        db.session.query(func.count(Order.id))
        .filter(
            Order.created_at >= today_start,
            Order.created_at < today_end,
            Order.order_status == "Success"
        )
        .scalar()
    )

    total_sales = (
        db.session.query(func.count(Order.id))
        .filter(Order.order_status == "Success")
        .scalar()
    )

    first_sale_date = (
        db.session.query(func.min(Order.created_at))
        .filter(Order.order_status == "Success")
        .scalar()
    )

    selling_days = 0
    if first_sale_date:
        selling_days = (now.date() - first_sale_date.date()).days

    active_products = (
        db.session.query(func.count(Product.id))
        .filter(Product.status == "Active")
        .scalar()
    )

    total_products = (
        db.session.query(func.count(Product.id))
        .scalar()
    )

    return render_template(
        "auth/admin/dashboard.html",
        title="LIM - Dashboard",
        user_role=role,
        today_sales=today_sales,
        total_sales=total_sales,
        selling_days=selling_days,
        active_products=active_products,
        total_products=total_products,
        today_date=today_start.strftime("%d/%m/%Y")
    )
