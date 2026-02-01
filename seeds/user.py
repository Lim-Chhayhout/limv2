def seed_users():
    from app import app, db
    from models import User, UserRole
    from werkzeug.security import generate_password_hash

    with app.app_context():
        roles = ["Superadmin", "Admin"]
        for r in roles:
            if not UserRole.query.filter_by(name=r).first():
                db.session.add(UserRole(name=r, status="Enable"))
        db.session.commit()

        superadmin_email = "chhayhout167@gmail.com"
        if not User.query.filter_by(email=superadmin_email).first():
            role = UserRole.query.filter_by(name="Superadmin").first()  # match case exactly
            if not role:
                raise Exception("Role 'Superadmin' not found. Check seeding order.")
            user = User(
                name="Super Admin",
                email=superadmin_email,
                telephone="0972443249",
                password=generate_password_hash("lim11221122"),
                role_id=role.id,
                status="Enable"
            )
            db.session.add(user)
            db.session.commit()
            print("Superadmin created")
        else:
            print("Superadmin already exists.")