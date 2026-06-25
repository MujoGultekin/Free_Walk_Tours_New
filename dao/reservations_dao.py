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