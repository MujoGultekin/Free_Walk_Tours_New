# routes/participant_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes.auth_routes import participant_required
from dao import tours_dao, reservations_dao

participant_bp = Blueprint('participant', __name__)

@participant_bp.route("/tour/detail/<int:tour_id>")
def tour_detail(tour_id):
    tour = tours_dao.get_tour_by_id(tour_id)
    if not tour:
        flash("Tour not found.", "danger")
        return redirect(url_for("home"))
    return render_template("tour_detail.html", tour=tour)

@participant_bp.route("/tour/book/<int:tour_id>", methods=["POST"])
@login_required
@participant_required
def book_tour(tour_id):
    tour_date = request.form.get("txt_date")
    add_count = int(request.form.get("txt_count", 0))
    add_names = request.form.get("txt_names", "").strip()
    
    # Sınav kuralı: Ekstra kişi sayısı 0 ile 3 arasında olmalıdır.
    if add_count < 0 or add_count > 3:
        flash("You can add a maximum of 3 extra guests.", "danger")
        return redirect(url_for("participant.tour_detail", tour_id=tour_id))

    reservations_dao.new_reservation(tour_id, current_user.id, tour_date, add_count, add_names)
    flash("Your booking has been successfully saved!", "success")
    return redirect(url_for("auth.profile_participant"))

@participant_bp.route("/reservation/cancel/<int:res_id>", methods=["POST"])
@login_required
@participant_required
def cancel_booking(res_id):
    res = reservations_dao.get_reservation_by_id(res_id)
    if res and res["participant_id"] == current_user.id:
        reservations_dao.cancel_reservation(res_id)
        flash("Reservation has been successfully cancelled.", "info")
    else:
        flash("Unauthorized action.", "danger")
    return redirect(url_for("auth.profile_participant"))