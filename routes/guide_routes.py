import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from routes.auth_routes import guide_required
from dao import reservations_dao, tours_dao

# Defining the guide Blueprint for managing tour routes and reports
guide_bp = Blueprint('guide', __name__)

# Directory path for storing uploaded tour images
UPLOAD_FOLDER = 'static/images'

@guide_bp.route("/guide/tour/new", methods=["GET", "POST"])
@login_required
@guide_required
def new_tour():
    """
    Handles the creation of a new tour, including file uploads and schedule configuration.
    """
    if request.method == "POST":
        # Retrieve form data
        title = request.form.get("title")
        meeting_point = request.form.get("meeting_point")
        duration = request.form.get("duration")
        language = request.form.get("language")
        max_participants = request.form.get("max_participants")
        description = request.form.get("description")
        stops = request.form.get("stops")

        # Process and save uploaded tour photos
        files = request.files.getlist("photos")
        file_names = []
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
                file_names.append(filename)
        photos_str = ",".join(file_names)

        # 1. Create the tour and retrieve the new ID
        new_id = tours_dao.new_tour(
            current_user.id, title, meeting_point, duration, 
            language, max_participants, description, stops, photos_str
        )
        
        # 2. Save selected days and times to the tour_schedule table
        selected_days = request.form.getlist("days")
        for day in selected_days:
            start_time = request.form.get(f"times_{day}")
            # Ensure both the day is selected and the time is provided
            if start_time: 
                tours_dao.add_tour_schedule(new_id, day, start_time)
        
        flash("New tour with schedule created successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
        
    return render_template("new_tour.html")

@guide_bp.route("/guide/tour/edit/<int:tour_id>", methods=["GET", "POST"])
@login_required
@guide_required
def edit_tour(tour_id):
    """
    Allows guides to update existing tour details if no reservations are present.
    """
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be modified!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    if request.method == "POST":
        # Update tour information in the database
        tours_dao.update_tour(
            tour_id,
            request.form.get("title"),
            request.form.get("meeting_point"),
            request.form.get("duration"),
            request.form.get("language"),
            request.form.get("max_participants"),
            request.form.get("description"),
            request.form.get("stops"),
            request.form.get("photos")
        )
        flash("Tour updated successfully!", "success")
        return redirect(url_for("auth.profile_guide"))
    
    tour = tours_dao.get_tour_by_id(tour_id)
    return render_template("edit_tour.html", tour=tour)

@guide_bp.route("/guide/tour/report/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def submit_report(tour_id):
    """
    Handles post-tour reporting, including participant counts and photo evidence.
    """
    count = request.form.get("actual_participants")
    file = request.files.get("report_photo")
    
    if file and file.filename:
        filename = secure_filename(file.filename)
        # Save report photo to the designated upload folder
        file.save(os.path.join(current_app.root_path, UPLOAD_FOLDER, filename))
        
        # Store report data in the database
        reservations_dao.save_tour_report(tour_id, count, filename)
        flash("Report submitted successfully!", "success")
    else:
        flash("Please upload a valid photo.", "danger")
        
    return redirect(url_for("auth.profile_guide"))

@guide_bp.route("/guide/tour/delete/<int:tour_id>", methods=["POST"])
@login_required
@guide_required
def delete_tour(tour_id):
    """
    Handles deletion of a tour route if no reservations are linked to it.
    """
    if tours_dao.has_reservations(tour_id):
        flash("This tour has active reservations and cannot be deleted!", "danger")
        return redirect(url_for("auth.profile_guide"))
    
    tours_dao.delete_tour(tour_id)
    flash("Tour deleted successfully!", "success")
    return redirect(url_for("auth.profile_guide"))