from app import app, db
from flask import render_template, session, redirect
from models import ShippingMethod, Order, OrderDetail, Customer, PaymentMethod, Product, ProductDetail
from decimal import Decimal
from flask_mail import Message
from app import mail
from routes.telegram import *

@app.route("/success")
def success():
    order_id = session.get("order_success")

    if not order_id:
        return redirect("/")

    order = (
        db.session.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        return redirect("/")

    payment = (
        db.session.query(PaymentMethod)
        .filter(PaymentMethod.id == order.payment_id)
        .first()
    )

    shipping = (
        db.session.query(ShippingMethod)
        .filter(ShippingMethod.id == order.shipping_id)
        .first()
    )

    customer = (
        db.session.query(Customer)
        .filter(Customer.id == order.customer_id)
        .first()
    )

    details = (
        db.session.query(OrderDetail)
        .filter(OrderDetail.order_id == order.id)
        .all()
    )

    products_info = []
    for item in details:
        product = db.session.query(Product).filter(Product.id == item.product_id).first()
        product_detail = db.session.query(ProductDetail).filter(ProductDetail.product_id == product.id).first()
        products_info.append({
            "name": product_detail.name,
            "price": float(item.product_price),
            "qty": item.qty,
            "subtotal": float(item.subtotal),
            "status": product_detail.status
        })

    subtotal = order.total_amount - Decimal(shipping.cost)

    order.products_info = products_info
    order.customer = customer
    order.payment = payment
    order.shipping = shipping

    send_order_to_telegram(order)

    send_invoice_email(customer.email, order)

    session.pop("order_success", None)

    return render_template(
        "pages/success.html",
        order=order,
        shipping=shipping,
        customer=customer,
        payment=payment,
        products_info=products_info,
        subtotal=subtotal,
    )

def send_invoice_email(customer_email, order):
    html_content = render_template(
        "pages/invoice_mail.html",
        order=order
    )

    msg = Message(
        subject=f"Invoice for Order #{order.order_number}",
        recipients=[customer_email],
        html=html_content
    )

    try:
        mail.send(msg)
        print("Email sent successfully")
    except Exception as e:
        print("Error sending email:", e)


