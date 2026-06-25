# routes/participant_routes.py
from flask import Blueprint, redirect, url_for, flash
from flask_login import login_required
from routes.auth_routes import participant_required
from dao import reservations_dao

participant_bp = Blueprint('participant', __name__)

@participant_bp.route("/reservation/cancel/<int:res_id>", methods=["POST"])
@login_required
@participant_required
def cancel_booking(res_id):
    res = reservations_dao.get_reservation_by_id(res_id)
    if res:
        reservations_dao.cancel_reservation(res_id)
        flash("Reservation cancelled.", "info")
    return redirect(url_for("auth.profile_participant"))