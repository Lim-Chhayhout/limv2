from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask.cli import with_appcontext
from seeds import *


mail = Mail()
app = Flask(__name__)
app.secret_key = "lim2026"

# db config ---------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/db_limv2'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# db config ---------------------------

# seeds -------------------------------
@app.cli.command("seeds")
@with_appcontext
def seed_command():
    seed_users()
    seed_ships()
    seed_payments()
# seeds -------------------------------

# routes ------------------------------
from routes import *
# routes ------------------------------

# mail --------------------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "chhayhout167@gmail.com"
app.config["MAIL_PASSWORD"] = "pyzk rcwq npyr znyr"
app.config["MAIL_DEFAULT_SENDER"] = ("Lim - Kdmv", "chhayhout167@gmail.com")

mail.init_app(app)

# mail --------------------------------

# error -------------------------------
@app.errorhandler(403)
def error_403(e):
    return render_template("handlers/403.html"), 403

@app.errorhandler(404)
def error_404(e):
    return render_template("handlers/404.html"), 404

@app.errorhandler(500)
def error_500(e):
    return render_template("handlers/500.html"), 500

@app.errorhandler(503)
def error_503(e):
    return render_template("handlers/503.html"), 503
# error -------------------------------



if __name__ == "__main__":
    app.run(debug=True)
