def seed_payments():
    from app import db
    from models import PaymentMethod

    if not PaymentMethod.query.first():
        payment_methods = [
            PaymentMethod(type='ABA PAY'),
            PaymentMethod(type='KHQR')
        ]

        db.session.bulk_save_objects(payment_methods)

        print("Payment methods have been seeded.")
    else:
        print("Payment methods already exist.")
