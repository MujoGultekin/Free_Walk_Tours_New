import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def initialize_database():
    conn = sqlite3.connect("roma_tours.db")
    cursor = conn.cursor()

    # Eski tabloları temizle
    cursor.execute('DROP TABLE IF EXISTS tour_reports;')
    cursor.execute('DROP TABLE IF EXISTS reservations;')
    cursor.execute('DROP TABLE IF EXISTS tour_schedule;')
    cursor.execute('DROP TABLE IF EXISTS tours;')
    cursor.execute('DROP TABLE IF EXISTS users;')

    # 1. TABLOLARI OLUŞTURMA
    cursor.execute('''
        CREATE TABLE users (
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
    CREATE TABLE IF NOT EXISTS tour_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tour_id INTEGER,
        actual_participants INTEGER,
        photo_path TEXT,
        report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(tour_id) REFERENCES tours(id)
        );
    ''')

    cursor.execute('''
        CREATE TABLE tours (
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
        CREATE TABLE tour_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_id INTEGER NOT NULL,
            day_of_week TEXT CHECK(day_of_week IN ('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')) NOT NULL,
            start_time TEXT NOT NULL,
            FOREIGN KEY (tour_id) REFERENCES tours(id) ON DELETE CASCADE
        );
    ''')

    cursor.execute('''
        CREATE TABLE reservations (
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

    # Ortak Şifre: 'password123'
    hashed_pwd = generate_password_hash("password123")

    # 2. KULLANICILAR
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (1, 'Marco', 'Rossi', 'marco@guide.com', ?, 'guide', 'English,Italian')", (hashed_pwd,))
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (4, 'Giulia', 'Verdi', 'giulia@guide.com', ?, 'guide', 'Spanish,German')", (hashed_pwd,))
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (2, 'John', 'Doe', 'john@part.com', ?, 'participant', NULL)", (hashed_pwd,))
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (5, 'Maria', 'Bianchi', 'maria@part.com', ?, 'participant', NULL)", (hashed_pwd,))
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (6, 'Luca', 'Neri', 'luca@part.com', ?, 'participant', NULL)", (hashed_pwd,))
    cursor.execute("INSERT INTO users (id, name, surname, email, password, role, languages) VALUES (3, 'Alessandro', 'Admin', 'admin@roma.com', ?, 'administrator', NULL)", (hashed_pwd,))

    # 3. TURLAR
    cursor.execute("INSERT INTO tours VALUES (1, 1, 'Colosseum & Ancient Rome Walk', 'Colosseum Metro Exit', 120, 'English', 15, 'Discover the history of the Roman Empire.', 'Colosseum,Roman Forum', 'colosseum1.jpg,colosseum2.jpg,colosseum3.jpg,colosseum4.jpg,colosseum5.jpg')")
    cursor.execute("INSERT INTO tours VALUES (2, 1, 'Vatican Secrets Tour', 'St. Peters Square Obelisk', 180, 'Italian', 10, 'Explore the magnificent St. Peters Basilica.', 'St. Peters Square,Basilica', 'vatican1.jpg,vatican2.jpg,vatican3.jpg,vatican4.jpg,vatican5.jpg')")
    cursor.execute("INSERT INTO tours VALUES (3, 4, 'Trastevere Evening Food Tour', 'Piazza Trilussa', 150, 'Spanish', 12, 'Taste authentic Roman street food and local legends.', 'Trastevere,Bakery,Gelateria', 'trastevere1.jpg,trastevere2.jpg,trastevere3.jpg,trastevere4.jpg,trastevere5.jpg')")
    cursor.execute("INSERT INTO tours VALUES (4, 1, 'Pantheon & Hidden Gems', 'Piazza della Rotonda', 90, 'English', 20, 'Uncover the secrets of ancient temples and squares.', 'Pantheon,Trevi Fountain,Navona', 'pantheon.jpg,pantheon2.jpg,pantheon3.jpg,pantheon4.jpg,pantheon5.jpg')")
    cursor.execute("INSERT INTO tours VALUES (5, 4, 'Roman Catacombs Underground', 'Piazza Venezia Bus Stop', 240, 'German', 8, 'Descend into the underground early Christian burial chambers.', 'Appian Way,Catacombs of San Callisto', 'catacombs1.jpg,catacombs2.jpg,catacombs3.jpg,catacombs4.jpg,catacombs5.jpg')")

    # 4. HAFTALIK TAKVİM
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (1, 'Monday', '10:00')")
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (2, 'Wednesday', '14:00')")
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (3, 'Friday', '18:30')")
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (4, 'Tuesday', '11:00')")
    cursor.execute("INSERT INTO tour_schedule (tour_id, day_of_week, start_time) VALUES (5, 'Saturday', '09:00')")

    # 5. GEÇMİŞ TARİHLİ REZERVASYON (5 Kişi: 1 ana katılımcı + 4 ek kişi)

    past_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO reservations (tour_id, participant_id, tour_date, additional_count, additional_names) VALUES (1, 2, ?, 4, 'Jane Doe, Alice Smith, Bob Brown, Charlie Green')", (past_date,))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with test data.")

if __name__ == "__main__":
    initialize_database()