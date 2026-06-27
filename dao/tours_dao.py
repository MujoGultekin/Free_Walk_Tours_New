# dao/tours_dao.py
import sqlite3

def new_tour(p_guide_id, p_title, p_meeting_point, p_duration, p_language, p_max_participants, p_description, p_stops, p_photos):
    query = "INSERT INTO tours (guide_id, title, meeting_point, duration, language, max_participants, description, stops, photos) VALUES (?,?,?,?,?,?,?,?,?)"
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_guide_id, p_title, p_meeting_point, p_duration, p_language, p_max_participants, p_description, p_stops, p_photos))
    tour_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return tour_id

def has_reservations(p_tour_id):
    query = "SELECT COUNT(*) as count FROM reservations WHERE tour_id = ?"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res['count'] > 0

def search_tours(p_date_name=None, p_duration=None, p_lang=None):
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # JOIN yerine LEFT JOIN kullanıldı
    query = "SELECT DISTINCT t.* FROM tours t LEFT JOIN tour_schedule ts ON t.id = ts.tour_id WHERE 1=1"
    params = []
    
    if p_lang:
        query += " AND t.language = ?"
        params.append(p_lang)
    if p_duration:
        query += " AND t.duration <= ?"
        params.append(int(p_duration))
    if p_date_name:
        # Eğer tarih filtresi varsa, LEFT JOIN üzerinden günü kontrol ediyoruz
        query += " AND ts.day_of_week = ?"
        params.append(p_date_name)
        
    cursor.execute(query, params)
    tours = cursor.fetchall()
    cursor.close()
    conn.close()
    return tours

def get_tour_by_id(p_tour_id):
    query = "SELECT * FROM tours WHERE id = ?"
    import sqlite3
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    tour = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return tour

def get_tours_by_guide_id(p_guide_id):
    query = "SELECT * FROM tours WHERE guide_id = ?"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_guide_id,))
    tours = cursor.fetchall()
    cursor.close()
    conn.close()
    return tours

def update_tour(p_tour_id, p_title, p_meeting_point, p_duration, p_language, p_max_participants, p_description, p_stops, p_photos):
    query = """UPDATE tours SET title=?, meeting_point=?, duration=?, language=?, 
               max_participants=?, description=?, stops=?, photos=? WHERE id=?"""
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    cursor.execute(query, (p_title, p_meeting_point, p_duration, p_language, 
                           p_max_participants, p_description, p_stops, p_photos, p_tour_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_tour(p_tour_id):
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    # Önce turu siliyoruz
    cursor.execute("DELETE FROM tours WHERE id = ?", (p_tour_id,))
    # İsterseniz ilgili schedule kayıtlarını da temizleyebilirsiniz:
    cursor.execute("DELETE FROM tour_schedule WHERE tour_id = ?", (p_tour_id,))
    conn.commit()
    cursor.close()
    conn.close()