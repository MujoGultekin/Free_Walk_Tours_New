# routes/auth_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from dao import users_dao

auth_bp = Blueprint('auth', __name__)

def guide_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'guide':
            flash("Only guides can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def participant_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'participant':
            flash("Only participants can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'administrator':
            flash("Only administrators can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        
        db_user = users_dao.get_user_by_email(email)
        if db_user and check_password_hash(db_user["password"], password):
            user_obj = User(
                id=db_user["id"], name=db_user["name"], surname=db_user["surname"],
                email=db_user["email"], role=db_user["role"], languages=db_user["languages"]
            )
            login_user(user_obj)
            flash(f"Welcome back, {user_obj.name}!", "success")
            
            if user_obj.role == 'administrator':
                return redirect(url_for("auth.profile_admin"))
            elif user_obj.role == 'guide':
                return redirect(url_for("auth.profile_guide"))
            return redirect(url_for("auth.profile_participant"))
        flash("Wrong email or password.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out.", "info")
    return redirect(url_for("home"))

@auth_bp.route("/register/participant", methods=["GET", "POST"])
def register_participant():
    if request.method == "POST":
        name = request.form.get("txt_name").strip()
        surname = request.form.get("txt_surname").strip()
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        
        hashed_password = generate_password_hash(password)
        if users_dao.new_user(name, surname, email, hashed_password, 'participant'):
            flash("Registration successful!", "success")
            return redirect(url_for("auth.login"))
        flash("Email already exists.", "danger")
    return render_template("register_participant.html")

@auth_bp.route("/register/guide", methods=["GET", "POST"])
def register_guide():
    if request.method == "POST":
        name = request.form.get("txt_name").strip()
        surname = request.form.get("txt_surname").strip()
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        langs = ",".join(request.form.getlist("chk_languages"))
        
        hashed_password = generate_password_hash(password)
        if users_dao.new_user(name, surname, email, hashed_password, 'guide', langs):
            flash("Guide registration successful!", "success")
            return redirect(url_for("auth.login"))
        flash("Email already exists.", "danger")
    return render_template("register_guide.html")

@auth_bp.route("/guide/profile")
@login_required
@guide_required
def profile_guide():
    return render_template("profile_guide.html")

@auth_bp.route("/participant/profile")
@login_required
@participant_required
def profile_participant():
    from dao import reservations_dao
    my_bookings = reservations_dao.get_participant_reservations(current_user.id)
    return render_template("profile_participant.html", bookings=my_bookings)

@auth_bp.route("/admin/profile")
@login_required
@admin_required
def profile_admin():
    guides_data = users_dao.get_all_guides_with_tours()
    stats_data = users_dao.get_platform_statistics()
    return render_template("profile_admin.html", guides=guides_data, stats=stats_data)