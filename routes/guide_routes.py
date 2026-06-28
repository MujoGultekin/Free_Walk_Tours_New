import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from routes.auth_routes import guide_required
from dao import reservations_dao, tours_dao

guide_bp = Blueprint('guide', __name__)

# Görsellerin kaydedileceği klasör
UPLOAD_FOLDER = 'static/images'

@guide_bp.route("/guide/tour/new", methods=["GET", "POST"])
@login_required
@guide_required
def new_tour():
    if request.method == "POST":
        # Form verilerini alıyoruz
        title = request.form.get("title")
        meeting_point = request.form.get("meeting_point")
        duration = request.form.get("duration")
        language = request.form.get("language")
        max_participants = request.form.get("max_participants")
        description = request.form.get("description")
        stops = request.form.get("stops")

        # Fotoğrafları işliyoruz
        files = request.files.getlist("photos")
        file_names = []
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Dosyayı static/images klasörüne kaydediyoruz
                file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
                file_names.append(filename)
        
        # İsimleri virgülle birleştirip string olarak veritabanına gönderiyoruz
        photos_str = ",".join(file_names)

        tours_dao.new_tour(
            current_user.id, title, meeting_point, duration, 
            language, max_participants, description, stops, photos_str
        )
        
        flash("New tour with photos created successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
        
    return render_template("new_tour.html")

@guide_bp.route("/guide/tour/edit/<int:tour_id>", methods=["GET", "POST"])
@login_required
@guide_required
def edit_tour(tour_id):
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be modified!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    if request.method == "POST":
        # Edit kısmında dosya yükleme opsiyonel olabilir, burada sadece metin güncelliyoruz
        tours_dao.update_tour(
            tour_id,
            request.form.get("title"),
            request.form.get("meeting_point"),
            request.form.get("duration"),
            request.form.get("language"),
            request.form.get("max_participants"),
            request.form.get("description"),
            request.form.get("stops"),
            request.form.get("photos") # Eski yöntem devam ediyor
        )
        flash("Tour updated successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
    
    tour = tours_dao.get_tour_by_id(tour_id)
    return render_template("edit_tour.html", tour=tour)

@guide_bp.route("/guide/tour/report/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def submit_report(tour_id):
    count = request.form.get("actual_participants")
    file = request.files.get("report_photo")
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Mevcut dosya yükleme mantığınla uyumlu:
        file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
        
        # DAO üzerinden veritabanına kaydet
        reservations_dao.save_tour_report(tour_id, count, filename)
        flash("Report submitted successfully!", "success")
    else:
        flash("Please upload a valid photo.", "danger")
        
    # Senin sisteminde çalışan doğru rota:
    return redirect(url_for("auth.profile_guide"))

@guide_bp.route("/guide/tour/delete/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def delete_tour(tour_id):
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be deleted!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    tours_dao.delete_tour(tour_id)
    flash("Tour deleted successfully!", "success")
    return redirect(url_for("auth.profile_guide"))