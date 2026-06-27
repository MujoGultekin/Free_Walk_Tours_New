# routes/participant_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from routes.auth_routes import participant_required
from dao import tours_dao, reservations_dao
from datetime import datetime, timedelta

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
    tour = tours_dao.get_tour_by_id(tour_id)
    add_count = int(request.form.get("txt_count", 0))
    
    # 1. Kural: Toplam kişi kontrolü
    current_booked = reservations_dao.get_total_booked_count(tour_id)
    if (current_booked + 1 + add_count) > tour['max_participants']:
        flash(f"This tour is full! (Max {tour['max_participants']} people).", "danger")
        return redirect(url_for("participant.tour_detail", tour_id=tour_id))

    # 2. Kural: Ekstra kişi sayısı (3 ile sınırlandırmıştık)
    if add_count < 0 or add_count > 3:
        flash("You can add a maximum of 3 extra guests.", "danger")
        return redirect(url_for("participant.tour_detail", tour_id=tour_id))

    # Kaydetme işlemi...
    reservations_dao.new_reservation(tour_id, current_user.id, request.form.get("txt_date"), add_count, request.form.get("txt_names", ""))
    flash("Booking successful!", "success")
    return redirect(url_for("auth.profile_participant"))

@participant_bp.route("/reservation/cancel/<int:res_id>", methods=["POST"])
@login_required
@participant_required
def cancel_booking(res_id):
    # 1. Rezervasyonu getir[cite: 19]
    res = reservations_dao.get_reservation_by_id(res_id)
    
    # 2. Yetkilendirme kontrolü (Senin orijinal kodun)
    if res and res["participant_id"] == current_user.id:
        
        # 3. 24 Saat kuralı kontrolü
        # 'tour_date' formatını YYYY-MM-DD olarak varsayıyorum
        tour_date = datetime.strptime(res['tour_date'], "%Y-%m-%d")
        
        if datetime.now() < (tour_date - timedelta(hours=24)):
            reservations_dao.cancel_reservation(res_id)
            flash("Reservation has been successfully cancelled.", "info")
        else:
            flash("Cannot cancel: less than 24 hours to the tour.", "danger")
            
    else:
        # Yetkisiz erişim veya rezervasyon bulunamadı
        flash("Unauthorized action or reservation not found.", "danger")
        
    return redirect(url_for("auth.profile_participant"))