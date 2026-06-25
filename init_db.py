# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash

def initialize_database():
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()

    # 1. TABLOLARI OLUŞTURMA
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('guide', 'participant', 'administrator')) NOT NULL,
            languages TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guide_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            meeting_point TEXT NOT NULL,
            duration INTEGER NOT NULL,
            language TEXT NOT NULL,
            max_participants INTEGER NOT NULL,
            description TEXT NOT NULL,
            stops TEXT NOT NULL,
            photos TEXT NOT NULL,
            FOREIGN KEY (guide_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tour_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_id INTEGER NOT NULL,
            day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL,
            start_time TEXT NOT NULL,
            FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE,
            UNIQUE(tour_id, day_of_week)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL,
            tour_date TEXT NOT NULL,
            additional_count INTEGER DEFAULT 0,
            additional_names TEXT,
            FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE,
            FOREIGN KEY (participant_id) REFERENCES users(id) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tour_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_id INTEGER NOT NULL,
            tour_date TEXT NOT NULL,
            actual_participants INTEGER NOT NULL,
            evidence_photo TEXT NOT NULL,
            FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
        );
    ''')

    # Temizlik (Çift kayıtları önlemek için)
    cursor.execute("DELETE FROM tour_schedule;")
    cursor.execute("DELETE FROM tours;")
    cursor.execute("DELETE FROM users;")
    
    # 2. ÖRNEK TEST VERİLERİ (SEED DATA)
    # Tüm test hesaplarının şifresi: 'password123'
    hashed_pwd = generate_password_hash("password123")

    # Hazır Kullanıcılar (Rehber, Katılımcı ve Admin)
    cursor.execute("""
        INSERT INTO users (id, name, surname, email, password, role, languages)
        VALUES (1, 'Marco', 'Rossi', 'marco@guide.com', ?, 'guide', 'English,Italian,Spanish')
    """, (hashed_pwd,))

    cursor.execute("""
        INSERT INTO users (id, name, surname, email, password, role, languages)
        VALUES (2, 'John', 'Doe', 'john@part.com', ?, 'participant', NULL)
    """, (hashed_pwd,))

    cursor.execute("""
        INSERT INTO users (id, name, surname, email, password, role, languages)
        VALUES (3, 'Alessandro', 'Admin', 'admin@roma.com', ?, 'administrator', NULL)
    """, (hashed_pwd,))

    # Hazır Roma Turları
    cursor.execute("""
        INSERT INTO tours (id, guide_id, title, meeting_point, duration, language, max_participants, description, stops, photos)
        VALUES (1, 1, 'Imperial Rome & Colosseum Walk', 'Colosseum Metro Exit', 120, 'English', 15, 
                'Discover the history of the Roman Empire.', 'Colosseum,Roman Forum,Capitoline Hill', 'colosseum.jpg')
    """)

    cursor.execute("""
        INSERT INTO tours (id, guide_id, title, meeting_point, duration, language, max_participants, description, stops, photos)
        VALUES (2, 1, 'Vatican Secrets Tour', 'St. Peters Square Obelisk', 180, 'Italian', 10, 
                'Explore the magnificent St. Peters Basilica.', 'St. Peters Square,Via della Conciliazione', 'vatican.jpg')
    """)

    # Haftalık Takvim Günleri
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (1, 'Monday', '10:00')")
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (2, 'Wednesday', '14:00')")

    conn.commit()
    cursor.close()
    conn.close()
    print("roma_tours.db başarıyla oluşturuldu ve test verileri yüklendi!")

if __name__ == "__main__":
    initialize_database()