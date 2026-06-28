import os
from flask import (
    Blueprint, render_template, request, redirect, 
    url_for, flash, current_app
)
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from routes.auth_routes import guide_required
from dao import reservations_dao, tours_dao

guide_bp = Blueprint('guide', __name__)
UPLOAD_FOLDER = 'static/images'

@guide_bp.route("/guide/tour/new", methods=["GET", "POST"])
@login_required
@guide_required
def new_tour():
    """Handle the creation of a new tour route."""
    if request.method == "POST":
        title = request.form.get("title")
        meeting_point = request.form.get("meeting_point")
        duration = request.form.get("duration")
        language = request.form.get("language")
        max_participants = request.form.get("max_participants")
        description = request.form.get("description")
        stops = request.form.get("stops")

        files = request.files.getlist("photos")
        file_names = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
                file_names.append(filename)
        photos_str = ",".join(file_names)

        new_id = tours_dao.new_tour(
            current_user.id, title, meeting_point, duration, 
            language, max_participants, description, stops, photos_str
        )
        
        selected_days = request.form.getlist("days")
        for day in selected_days:
            start_time = request.form.get(f"times_{day}")
            if start_time: 
                tours_dao.add_tour_schedule(new_id, day, start_time)
        
        flash("New tour created successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
    return render_template("new_tour.html")

@guide_bp.route("/guide/tour/edit/<int:tour_id>", methods=["GET", "POST"])
@login_required
@guide_required
def edit_tour(tour_id):
    """Handle editing an existing tour route with report validation."""
    tour = tours_dao.get_tour_by_id(tour_id)
    
    reportable_tours = tours_dao.get_past_tours_with_reservations(current_user.id)
    is_reportable = any(t['id'] == tour_id for t in reportable_tours)

    if is_reportable and not tour['is_reported']:
        flash("You must submit the post-tour report before editing this completed tour!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    if request.method == "POST":
        files = request.files.getlist("photos")
        photo_names = tour['photos']
        
        if files and files[0].filename != '':
            file_list = []
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
                file_list.append(filename)
            photo_names = ",".join(file_list)
        
        tours_dao.update_tour(
            tour_id,
            request.form.get("title"),
            request.form.get("meeting_point"),
            request.form.get("duration"),
            request.form.get("language"),
            request.form.get("max_participants"),
            request.form.get("description"),
            request.form.get("stops"),
            photo_names
        )
        flash("Tour updated successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
    
    return render_template("edit_tour.html", tour=tour)

@guide_bp.route("/guide/tour/report/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def submit_report(tour_id):
    """Submit a post-tour report."""
    count = request.form.get("actual_participants")
    file = request.files.get("report_photo")
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
        reservations_dao.save_tour_report(tour_id, count, filename)
        flash("Report submitted successfully!", "success")
    else:
        flash("Please upload a valid photo.", "danger")
    return redirect(url_for("auth.profile_guide"))

@guide_bp.route("/guide/tour/delete/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def delete_tour(tour_id):
    """Handle deletion of a tour route with report validation."""
    tour = tours_dao.get_tour_by_id(tour_id)
    reportable_tours = tours_dao.get_past_tours_with_reservations(current_user.id)
    is_reportable = any(t['id'] == tour_id for t in reportable_tours)

    if is_reportable and not tour['is_reported']:
        flash("You must submit the post-tour report before deleting this completed tour!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    tours_dao.delete_tour(tour_id)
    flash("Tour deleted successfully!", "success")
    return redirect(url_for("auth.profile_guide"))