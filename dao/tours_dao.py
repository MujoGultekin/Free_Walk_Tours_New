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
    
    # GROUP_CONCAT ile günleri ve saatleri birleştiriyoruz
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
    
    # Gruplama ekliyoruz ki aynı tur bir kez gelsin ama tüm günleri schedule içinde birleşsin
    query += " GROUP BY t.id"
    
    # Eğer tarih filtresi varsa HAVING kullanarak filtreleme yapıyoruz
    if p_date_name:
        query += " HAVING schedule LIKE ?"
        params.append(f"%{p_date_name}%")
        
    cursor.execute(query, params)
    tours = cursor.fetchall()
    cursor.close()
    conn.close()
    return tours

def get_tour_by_id(p_tour_id):
    query = """
        SELECT t.*, GROUP_CONCAT(ts.day_of_week || ' (' || ts.start_time || ')', ', ') as schedule 
        FROM tours t 
        LEFT JOIN tour_schedule ts ON t.id = ts.tour_id 
        WHERE t.id = ?
        GROUP BY t.id
    """
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_tour_id,))
    tour = cursor.fetchone()
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

def get_past_tours_with_reservations(p_guide_id):
    """Rehberin, tarihi geçmiş ve rezervasyonu olan turlarını getirir."""
    import sqlite3
    from datetime import datetime
    
    # Bugünün tarihini al (YYYY-MM-DD)
    today = datetime.now().strftime("%Y-%m-%d")
    
    query = """
        SELECT DISTINCT t.* 
        FROM tours t
        JOIN reservations r ON t.id = r.tour_id
        WHERE t.guide_id = ? 
        AND r.tour_date < ?
    """
    
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # today değişkenini parametre olarak gönderiyoruz
    cursor.execute(query, (p_guide_id, today))
    tours = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tours