from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import models

app = Flask(__name__)
app.secret_key = "clave_secreta"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return models.get_user_by_id(user_id)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # aquí creas el usuario en la base
        ...
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # aquí verificas el usuario
        ...
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return f"Bienvenido {current_user.name}"

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
