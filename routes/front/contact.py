from app import app
from flask import render_template, jsonify, request, redirect, url_for
from flask_mail import Message, Mail

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'chhayhout167@gmail.com'
app.config['MAIL_PASSWORD'] = 'yaby dwrd pvvx gdhh'
app.config['MAIL_DEFAULT_SENDER'] = 'chhayhout167@gmail.com'
mail = Mail(app)

@app.route("/contact")
def contact():
    success = request.args.get("contact_success")
    return render_template("pages/contact.html", success=success)

@app.post("/post-contact")
def post_contact():
    form = request.form
    name = form.get("name")
    email = form.get("email")
    message = form.get("message")

    if not name or not email or not message:
        return jsonify({"error": "Please fill in all fields"})

    msg = Message('Contact From LIM v2', recipients=['chhayhout167@gmail.com'])
    msg.body = f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
    msg.html = f"""
        <h3>New Contact Message</h3>
        <p><b>Name:</b> {name}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Message:</b><br>{message}</p>
    """
    mail.send(msg)
    contact_success = name
    return redirect(url_for("contact", contact_success=contact_success))