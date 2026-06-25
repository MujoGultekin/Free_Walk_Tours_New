# routes/guide_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from routes.auth_routes import guide_required
from dao import tours_dao

guide_bp = Blueprint('guide', __name__)

@guide_bp.route("/guide/tour/new", methods=["GET", "POST"])
@login_required
@guide_required
def new_tour():
    if request.method == "POST":
        pass
    return render_template("new_tour.html")

@guide_bp.route("/guide/tour/edit/<int:tour_id>", methods=["GET", "POST"])
@login_required
@guide_required
def edit_tour(tour_id):
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be modified!", "danger")
        return redirect(url_for("auth.profile_guide"))
    return render_template("edit_tour.html", tour_id=tour_id)