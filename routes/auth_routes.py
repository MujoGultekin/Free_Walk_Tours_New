# routes/auth_routes.py
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from dao import tours_dao
from models import User

# Direct function imports to prevent naming conflicts
from dao.users_dao import get_user_by_email, get_user_by_id, get_all_guides_with_tours, get_platform_statistics
from dao.users_dao import new_user

import dao.users_dao as users_dao

auth_bp = Blueprint('auth', __name__)

# --- Access Control Decorators ---

def guide_required(f):
    """Decorator to restrict access to authenticated guides only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'guide':
            flash("Only guides can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def participant_required(f):
    """Decorator to restrict access to authenticated participants only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'participant':
            flash("Only participants can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to restrict access to authenticated administrators only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'administrator':
            flash("Only administrators can access this page.", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated_function

# --- Authentication Routes ---

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handles user authentication and role-based redirection."""
    if request.method == "POST":
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        
        db_user = get_user_by_email(email)
        if db_user and check_password_hash(db_user["password"], password):
            user_obj = User(
                id=db_user["id"], name=db_user["name"], surname=db_user["surname"],
                email=db_user["email"], role=db_user["role"], languages=db_user["languages"]
            )
            login_user(user_obj)
            flash(f"Welcome back, {user_obj.name}!", "success")
            
            # Redirect to appropriate profile based on user role
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
    """Logs out the current user and clears the session."""
    logout_user()
    flash("Successfully logged out.", "info")
    return redirect(url_for("home"))

@auth_bp.route("/register/participant", methods=["GET", "POST"])
def register_participant():
    """Registers a new participant account."""
    if request.method == "POST":
        name = request.form.get("txt_name").strip()
        surname = request.form.get("txt_surname").strip()
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        
        hashed_password = generate_password_hash(password)
        if new_user(name, surname, email, hashed_password, 'participant'):
            flash("Registration successful!", "success")
            return redirect(url_for("auth.login"))
        flash("Email already exists.", "danger")
    return render_template("register_participant.html")

@auth_bp.route("/register/guide", methods=["GET", "POST"])
def register_guide():
    """Registers a new guide account with language proficiency data."""
    if request.method == "POST":
        name = request.form.get("txt_name").strip()
        surname = request.form.get("txt_surname").strip()
        email = request.form.get("txt_email").strip()
        password = request.form.get("txt_password")
        langs = ",".join(request.form.getlist("chk_languages"))
        
        hashed_password = generate_password_hash(password)
        if new_user(name, surname, email, hashed_password, 'guide', langs):
            flash("Guide registration successful!", "success")
            return redirect(url_for("auth.login"))
        flash("Email already exists.", "danger")
    return render_template("register_guide.html")

# --- Profile Routes ---

@auth_bp.route("/guide/profile")
@login_required
@guide_required
def profile_guide():
    """Displays the guide's dashboard with created tours and reportable history."""
    from dao.tours_dao import get_tours_by_guide_id
    my_tours = get_tours_by_guide_id(current_user.id)
    reportable_tours = tours_dao.get_past_tours_with_reservations(current_user.id)
    return render_template("profile_guide.html", tours=my_tours, reportable_tours=reportable_tours)

@auth_bp.route("/participant/profile")
@login_required
@participant_required
def profile_participant():
    """Displays the participant's dashboard with active bookings."""
    from dao.reservations_dao import get_participant_reservations
    my_bookings = get_participant_reservations(current_user.id)
    today_str = datetime.now().strftime("%Y-%m-%d")
    return render_template("profile_participant.html", bookings=my_bookings,today_str=today_str)

@auth_bp.route("/admin/profile")
@login_required
@admin_required
def profile_admin():
    """Displays the admin dashboard with platform-wide statistics."""
    from dao.users_dao import get_platform_statistics, get_all_guides_with_tours
    stats = get_platform_statistics()
    guides = get_all_guides_with_tours()
    return render_template("profile_admin.html", stats=stats, guides=guides)