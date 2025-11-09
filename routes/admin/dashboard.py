from app import app
from flask import render_template
from flask import jsonify
from app import db
from models import Order, OrderDetail, Product, ProductCategory
from utils.timezone import PhnomPenhTime
from datetime import timedelta

# ===============================================================================================================
# api with backend (postman)
# ===============================================================================================================
@app.get("/dashboard/sale-report/daily-json")
def sale_report_daily_json():
    try:
        now = PhnomPenhTime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        orders = (
            db.session.query(Order)
            .filter(Order.created_at >= today_start, Order.created_at <= today_end)
            .all()
        )

        if not orders:
            return jsonify({"message": "No sales today"}), 200

        total_sale_count = len(orders)
        total_revenue = 0
        status_count = {"Pending": 0, "Success": 0}

        order_list = {}

        for o in orders:
            total_revenue += float(o.total_amount)
            status_count[o.order_status] = status_count.get(o.order_status, 0) + 1

            details = db.session.query(OrderDetail).filter_by(order_id=o.id).all()

            detail_list = [
                {
                    "id": d.id,
                    "product_id": d.product_id,
                    "qty": d.qty,
                    "total_price": float(d.total_price),
                    "product_status": d.product_status
                }
                for d in details
            ]

            order_list[o.id] = {
                "order_number": o.order_number,
                "customer_id": o.customer_id,
                "payment_id": o.payment_id,
                "shipping_id": o.shipping_id,
                "total_amount": float(o.total_amount),
                "order_status": o.order_status,
                "created_at": o.created_at,
                "order_details": detail_list
            }

        result = {
            "date": today_start.strftime("%Y-%m-%d"),
            "total_sale_count": total_sale_count,
            "total_revenue": total_revenue,
            "status_count": status_count
        }

        return jsonify({
            "result": result,
            "sale_list": order_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/dashboard/sale-report/weekly-json")
def sale_report_weekly_json():
    try:
        now = PhnomPenhTime.now()

        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        week_end = week_start + timedelta(days=6)
        week_end = week_end.replace(hour=23, minute=59, second=59, microsecond=999999)

        orders = (
            db.session.query(Order)
            .filter(Order.created_at >= week_start, Order.created_at <= week_end)
            .all()
        )

        total_sale_count = len(orders)
        total_revenue = 0
        status_count = {"Pending": 0, "Success": 0}

        order_list = {}

        for o in orders:
            total_revenue += float(o.total_amount)
            status_count[o.order_status] = status_count.get(o.order_status, 0) + 1

            details = db.session.query(OrderDetail).filter_by(order_id=o.id).all()

            detail_list = [
                {
                    "id": d.id,
                    "product_id": d.product_id,
                    "qty": d.qty,
                    "total_price": float(d.total_price),
                    "product_status": d.product_status,
                }
                for d in details
            ]

            order_list[o.id] = {
                "order_number": o.order_number,
                "customer_id": o.customer_id,
                "payment_id": o.payment_id,
                "shipping_id": o.shipping_id,
                "total_amount": float(o.total_amount),
                "order_status": o.order_status,
                "created_at": o.created_at,
                "order_details": detail_list,
            }

        result = {
            "week_start": week_start.strftime("%Y-%m-%d"),
            "week_end": week_end.strftime("%Y-%m-%d"),
            "total_sale_count": total_sale_count,
            "total_revenue": total_revenue,
            "status_count": status_count,
        }

        return jsonify({
            "result": result,
            "sale_list": order_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/dashboard/sale-report/monthly-json")
def sale_report_monthly_json():
    try:
        now = PhnomPenhTime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Get last day of current month
        if now.month == 12:
            next_month_start = month_start.replace(year=now.year + 1, month=1)
        else:
            next_month_start = month_start.replace(month=now.month + 1)
        month_end = next_month_start - timedelta(microseconds=1)

        orders = (
            db.session.query(Order)
            .filter(Order.created_at >= month_start, Order.created_at <= month_end)
            .all()
        )

        if not orders:
            return jsonify({"message": "No sales this month"}), 200

        total_sale_count = len(orders)
        total_revenue = 0
        status_count = {"Pending": 0, "Success": 0}

        order_list = {}

        for o in orders:
            total_revenue += float(o.total_amount)
            status_count[o.order_status] = status_count.get(o.order_status, 0) + 1

            details = db.session.query(OrderDetail).filter_by(order_id=o.id).all()
            detail_list = [
                {
                    "id": d.id,
                    "product_id": d.product_id,
                    "qty": d.qty,
                    "total_price": float(d.total_price),
                    "product_status": d.product_status
                }
                for d in details
            ]

            order_list[o.id] = {
                "order_number": o.order_number,
                "customer_id": o.customer_id,
                "payment_id": o.payment_id,
                "shipping_id": o.shipping_id,
                "total_amount": float(o.total_amount),
                "order_status": o.order_status,
                "created_at": o.created_at,
                "order_details": detail_list
            }

        result = {
            "month": month_start.strftime("%Y-%m"),
            "total_sale_count": total_sale_count,
            "total_revenue": total_revenue,
            "status_count": status_count
        }

        return jsonify({
            "result": result,
            "sale_list": order_list
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/dashboard/criteria-report/product-json")
def criteria_report_product_json():
    try:
        products = db.session.query(Product).all()
        if not products:
            return jsonify({"message": "No products found"}), 200

        total_products = len(products)
        total_active = sum(1 for p in products if p.status == "Active")
        total_in_stock = sum(p.stock.qty if p.stock else 0 for p in products)
        total_out_of_stock = sum(1 for p in products if not p.stock or p.stock.qty <= 0)
        total_sold = sum(db.session.query(db.func.sum(OrderDetail.qty))
                         .filter(OrderDetail.product_id == p.id).scalar() or 0 for p in products)

        result = {
            "total_products": total_products,
            "total_active": total_active,
            "total_in_stock": total_in_stock,
            "total_out_of_stock": total_out_of_stock,
            "total_sold": int(total_sold)
        }

        return jsonify({
            "result": result
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.get("/dashboard/criteria-report/category-json")
def criteria_report_category_json():
    try:
        categories = db.session.query(ProductCategory).all()
        if not categories:
            return jsonify({"message": "No categories found"}), 200

        return jsonify({
            "result": {
                "total_categories": len(categories)
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================================================================================================
# api with front (page)
# ===============================================================================================================
@app.route("/dashboard")
def dashboard():
    return render_template("auth/admin/dashboard.html", title="LIM - Sale Report")

