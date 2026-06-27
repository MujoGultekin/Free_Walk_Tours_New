# routes/guide_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from routes.auth_routes import guide_required
from dao import tours_dao

guide_bp = Blueprint('guide', __name__)

@guide_bp.route("/guide/tour/new", methods=["GET", "POST"])
@login_required
@guide_required
def new_tour():
    if request.method == "POST":
        # Formdan gelen verileri alıyoruz
        title = request.form.get("title")
        meeting_point = request.form.get("meeting_point")
        duration = request.form.get("duration")
        language = request.form.get("language")
        max_participants = request.form.get("max_participants")
        description = request.form.get("description")
        stops = request.form.get("stops")
        photos = request.form.get("photos") # Basit olması için dosya yolu/adı

        # Veritabanına kayıt işlemini gerçekleştiriyoruz
        tours_dao.new_tour(
            current_user.id, title, meeting_point, duration, 
            language, max_participants, description, stops, photos
        )
        
        flash("New tour created successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
        
    return render_template("new_tour.html")

@guide_bp.route("/guide/tour/edit/<int:tour_id>", methods=["GET", "POST"])
@login_required
@guide_required
def edit_tour(tour_id):
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be modified!", "danger")
        return redirect(url_for("auth.profile_guide"))
    return render_template("edit_tour.html", tour_id=tour_id)

@guide_bp.route("/guide/tour/report/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def submit_report(tour_id):
    actual_participants = request.form.get("actual_participants")
    photo = request.files.get("photo") # Dosya yükleme kısmı
    
    # Burada tours_dao.py içine yeni bir add_report fonksiyonu ekleyip çağırabilirsin
    tours_dao.add_report(tour_id, actual_participants, photo.filename)
    
    flash("Report submitted successfully!", "success")
    return redirect(url_for("auth.profile_guide"))