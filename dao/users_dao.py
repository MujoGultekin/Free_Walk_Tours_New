# dao/users_dao.py
import sqlite3

def new_user(p_name, p_surname, p_email, p_password, p_role, p_languages=None):
    query = "INSERT INTO users (name, surname, email, password, role, languages) VALUES (?,?,?,?,?,?)"
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()
    try:
        cursor.execute(query, (p_name, p_surname, p_email, p_password, p_role, p_languages))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    finally:
        cursor.close()
        conn.close()
    return success

def get_user_by_email(p_email):
    query = "SELECT * FROM users WHERE email = ?"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_email,))
    db_user = cursor.fetchone()
    cursor.close()
    conn.close()
    return db_user

def get_user_by_id(p_id):
    query = "SELECT * FROM users WHERE id = ?"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (p_id,))
    db_user = cursor.fetchone()
    cursor.close()
    conn.close()
    return db_user

def get_all_guides_with_tours():
    query = "SELECT id, name, surname, email, languages FROM users WHERE role = 'guide'"
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query)
    guides = cursor.fetchall()
    
    guides_list = []
    for guide in guides:
        cursor.execute("SELECT id, title, language FROM tours WHERE guide_id = ?", (guide["id"],))
        tours = cursor.fetchall()
        guides_list.append({
            "info": guide,
            "tours": tours
        })
    cursor.close()
    conn.close()
    return guides_list

def get_platform_statistics():
    conn = sqlite3.connect("roma_tours.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    stats = {}
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'guide'")
    stats["total_guides"] = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'participant'")
    stats["total_participants"] = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM tours")
    stats["total_tours"] = cursor.fetchone()["count"]
    
    cursor.execute("SELECT COUNT(*) as count FROM reservations")
    stats["total_reservations"] = cursor.fetchone()["count"]
    
    query_lang = """
        SELECT t.language, COUNT(r.id) as res_count 
        FROM reservations r
        JOIN tours t ON r.tour_id = t.id
        GROUP BY t.language
    """
    cursor.execute(query_lang)
    stats["reservations_per_language"] = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return stats