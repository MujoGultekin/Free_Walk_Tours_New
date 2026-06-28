# dao/reservations_dao.py
import os
import sqlite3

# Dinamik mutlak yol tanımı (Dizin/Klasör hatalarını önlemek için)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE_PATH = os.path.join(BASE_DIR, "roma_tours.db")

def get_reservation_by_id(p_res_id):
    """Retrieves a specific reservation record by its ID."""
    query = "SELECT * FROM reservations WHERE id = ?"
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_res_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res

def cancel_reservation(p_res_id):
    """Deletes a reservation from the database."""
    query = "DELETE FROM reservations WHERE id = ?"
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_res_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_participant_reservations(p_part_id):
    """Fetches all reservations for a specific participant, including related tour details."""
    query = """
        SELECT r.id as res_id, r.tour_date, r.additional_count, t.title, t.meeting_point 
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        WHERE r.participant_id = ?
    """
    conn = sqlite3.connect(DB_FILE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_part_id,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def new_reservation(p_tour_id, p_part_id, p_date, p_add_count, p_add_names):
    """Creates a new reservation entry in the database."""
    query = "INSERT INTO reservations (tour_id, participant_id, tour_date, additional_count, additional_names) VALUES (?,?,?,?,?)"
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_part_id, p_date, p_add_count, p_add_names))
    conn.commit()
    cursor.close()
    conn.close()

# ------------------------------------------------------------------
# DÜZELTME: Fonksiyona p_date eklendi ve SQL sorgusu tarihe göre filtrelendi
# ------------------------------------------------------------------
def get_total_booked_count(p_tour_id, p_date):
    """Calculates the total number of participants booked for a specific tour on a specific date."""
    query = "SELECT SUM(1 + additional_count) as total FROM reservations WHERE tour_id = ? AND tour_date = ?"
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_date))
    res = cursor.fetchone()
    total = res[0] if res[0] else 0
    conn.close()
    return total

# ------------------------------------------------------------------
# DÜZELTME: SQL parametrelerinin sırası (p_tour_id, p_actual_count, p_photo_path) olarak eşitlendi
# ------------------------------------------------------------------
def save_tour_report(p_tour_id, p_actual_count, p_photo_path):
    """Saves a post-tour report containing participant count and photo evidence."""
    query = "INSERT INTO tour_reports (tour_id, actual_participants, photo_path) VALUES (?,?,?)"
    conn = sqlite3.connect(DB_FILE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_actual_count, p_photo_path))
    conn.commit()
    cursor.close()
    conn.close()