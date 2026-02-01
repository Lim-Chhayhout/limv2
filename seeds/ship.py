def seed_ships():
    from app import db
    from models import ShippingMethod

    if not ShippingMethod.query.first():
        shipping_methods = [
            ShippingMethod(type='Local Shipping', cost=1.50),
            ShippingMethod(type='Express Shipping', cost=2.00)
        ]

        db.session.bulk_save_objects(shipping_methods)
        db.session.commit()

        print("Shipping methods have been seeded.")
    else:
        print("Shipping methods already exist.")
