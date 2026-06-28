# dao/tours_dao.py
import os
import sqlite3
from datetime import datetime

# Dynamic absolute path configuration for database access
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE_PATH = os.path.join(BASE_DIR, "roma_tours.db")

def new_tour(p_guide_id, p_title, p_meeting_point, p_duration, p_language, p_max_participants, p_description, p_stops, p_photos):
    """Inserts a new walking tour route record into the database."""
    query = """
        INSERT INTO tours (
            guide_id, title, meeting_point, duration, language, 
            max_participants, description, stops, photos
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (
        p_guide_id, p_title, p_meeting_point, p_duration, p_language, 
        p_max_participants, p_description, p_stops, p_photos
    ))
    tour_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return tour_id

def has_reservations(p_tour_id):
    """Checks whether a specific tour route has any consumer reservations linked."""
    query = "SELECT COUNT(*) as count FROM reservations WHERE tour_id = ?"
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res['count'] > 0

def search_tours(p_date_name=None, p_duration=None, p_lang=None):
    """Filters and dynamic searches available tours matching user constraints."""
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = """
        SELECT t.*, 
               GROUP_CONCAT(ts.day_of_week || ' (' || ts.start_time || ')', ', ') as schedule 
        FROM tours t 
        LEFT JOIN tour_schedule ts ON t.id = ts.tour_id 
        WHERE 1=1
    """
    params = []
    
    if p_lang:
        query += " AND t.language = ?"
        params.append(p_lang)
    if p_duration:
        query += " AND t.duration <= ?"
        params.append(int(p_duration))
    
    query += " GROUP BY t.id"
    
    if p_date_name:
        query += " HAVING schedule LIKE ?"
        params.append(f"%{p_date_name}%")
        
    cursor.execute(query, params)
    tours = cursor.fetchall()
    cursor.close()
    conn.close()
    return tours

def get_tour_by_id(p_tour_id):
    """Retrieves full profile details of a single tour including guide details and report status."""
    query = """
        SELECT t.*, u.name as guide_name, u.surname as guide_surname,
               GROUP_CONCAT(ts.day_of_week || ' (' || ts.start_time || ')', ', ') as schedule,
               CASE WHEN tr.id IS NOT NULL THEN 1 ELSE 0 END as is_reported
        FROM tours t 
        LEFT JOIN tour_schedule ts ON t.id = ts.tour_id 
        JOIN users u ON t.guide_id = u.id
        LEFT JOIN tour_reports tr ON t.id = tr.tour_id
        WHERE t.id = ?
        GROUP BY t.id
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    tour = cursor.fetchone()
    conn.close()
    return tour

def get_tours_by_guide_id(p_guide_id):
    """Retrieves all tours for a guide, flags whether they have been reported."""
    query = """
        SELECT t.*, CASE WHEN tr.id IS NOT NULL THEN 1 ELSE 0 END as is_reported
        FROM tours t
        LEFT JOIN tour_reports tr ON t.id = tr.tour_id
        WHERE t.guide_id = ?
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_guide_id,))
    tours = cursor.fetchall()
    cursor.close()
    conn.close()
    return tours

def update_tour(p_tour_id, p_title, p_meeting_point, p_duration, p_language, p_max_participants, p_description, p_stops, p_photos):
    """Updates target fields for an existing historical route entity."""
    query = """
        UPDATE tours 
        SET title=?, meeting_point=?, duration=?, language=?, 
            max_participants=?, description=?, stops=?, photos=? 
        WHERE id=?
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (
        p_title, p_meeting_point, p_duration, p_language, 
        p_max_participants, p_description, p_stops, p_photos, p_tour_id
    ))
    conn.commit()
    cursor.close()
    conn.close()

def delete_tour(p_tour_id):
    """Cascades deletion for a specific tour and its relative weekly schedule rows."""
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tours WHERE id = ?", (p_tour_id,))
    cursor.execute("DELETE FROM tour_schedule WHERE tour_id = ?", (p_tour_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_past_tours_with_reservations(p_guide_id):
    """Extracts historical tours assigned to the guide that have passed the schedule boundary."""
    today = datetime.now().strftime("%Y-%m-%d")
    query = """
        SELECT DISTINCT t.* 
        FROM tours t
        JOIN reservations r ON t.id = r.tour_id
        WHERE t.guide_id = ? 
        AND r.tour_date < ?
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_guide_id, today))
    tours = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tours

def add_tour_schedule(p_tour_id, p_day, p_time):
    """Appends a new structural day and time segment configuration for a tour."""
    query = "INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (?, ?, ?)"
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_day, p_time))
    conn.commit()
    conn.close()