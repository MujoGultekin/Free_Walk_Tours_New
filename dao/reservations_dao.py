# dao/reservations_dao.py
import sqlite3

def get_reservation_by_id(p_res_id):
    query = "SELECT * FROM reservations WHERE id = ?"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_res_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res

def cancel_reservation(p_res_id):
    query = "DELETE FROM reservations WHERE id = ?"
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_res_id,))
    conn.commit()
    cursor.close()
    conn.close()

# dao/reservations_dao.py dosyasına eklenecek fonksiyon:

def get_participant_reservations(p_part_id):
    """Katılımcının yaptığı tüm rezervasyonları tur bilgileriyle birlikte getirir."""
    query = """
        SELECT r.id as res_id, r.tour_date, r.additional_count, t.title, t.meeting_point 
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        WHERE r.participant_id = ?
    """
    import sqlite3
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_part_id,))
    res = cursor.fetchall()
    cursor.close()
    conn.close()
    return res

def new_reservation(p_tour_id, p_part_id, p_date, p_add_count, p_add_names):
    query = "INSERT INTO reservations (tour_id, participant_id, tour_date, additional_count, additional_names) VALUES (?,?,?,?,?)"
    import sqlite3
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_part_id, p_date, p_add_count, p_add_names))
    conn.commit()
    cursor.close()
    conn.close()

def get_total_booked_count(p_tour_id):
    query = "SELECT SUM(1 + additional_count) as total FROM reservations WHERE tour_id = ?"
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    res = cursor.fetchone()
    total = res[0] if res[0] else 0
    conn.close()
    return total

def save_tour_report(p_tour_id, p_actual_count, p_photo_path):
    query = "INSERT INTO tour_reports (tour_id, actual_participants, photo_path) VALUES (?,?,?)"
    import sqlite3
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id, p_actual_count, p_photo_path))
    conn.commit()
    cursor.close()
    conn.close()