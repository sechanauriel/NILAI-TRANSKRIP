import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "transcript_system.db"

def init_database():
    """Initialize database with all required tables"""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            nim TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            program_study TEXT NOT NULL,
            batch_year INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            course_code TEXT PRIMARY KEY,
            course_name TEXT NOT NULL,
            sks INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nim TEXT NOT NULL,
            course_code TEXT NOT NULL,
            semester INTEGER NOT NULL,
            letter_grade TEXT NOT NULL,
            numeric_grade REAL NOT NULL,
            presence_percentage REAL NOT NULL DEFAULT 75.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (nim) REFERENCES students(nim),
            FOREIGN KEY (course_code) REFERENCES courses(course_code),
            UNIQUE(nim, course_code, semester)
        )
    ''')
    
    # Grade history table (for audit trail)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grade_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade_id INTEGER NOT NULL,
            old_letter_grade TEXT,
            old_numeric_grade REAL,
            new_letter_grade TEXT,
            new_numeric_grade REAL,
            changed_by TEXT NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            FOREIGN KEY (grade_id) REFERENCES grades(grade_id)
        )
    ''')
    
    # Views for audit trail
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS grade_changes_summary AS
        SELECT 
            gh.history_id,
            s.nim,
            s.name,
            c.course_name,
            gh.old_numeric_grade,
            gh.new_numeric_grade,
            gh.changed_by,
            gh.changed_at,
            gh.reason
        FROM grade_history gh
        JOIN grades g ON gh.grade_id = g.grade_id
        JOIN students s ON g.nim = s.nim
        JOIN courses c ON g.course_code = c.course_code
        ORDER BY gh.changed_at DESC
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def get_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def populate_sample_data():
    """Populate sample data for testing"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] > 0:
        return  # Data already exists
    
    # Sample students
    students = [
        ("21001", "MUHAMMAD SECHAN AURIEL", "Teknik Informatika", 2021),
        ("21002", "PUTRI NURHALIZA", "Teknik Informatika", 2021),
    ]
    
    # Sample courses
    courses = [
        ("PBO101", "Pemrograman Berorientasi Objek", 3),
        ("DBMS101", "Sistem Basis Data", 3),
        ("WEB101", "Pengembangan Web", 4),
        ("ALSTD101", "Algoritma dan Struktur Data", 3),
        ("NET101", "Jaringan Komputer", 3),
    ]
    
    cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)", students)
    cursor.executemany("INSERT INTO courses VALUES (?, ?, ?, CURRENT_TIMESTAMP)", courses)
    
    # Sample grades for semester 1
    sample_grades = [
        ("21001", "PBO101", 1, "A", 4.0, 95),
        ("21001", "DBMS101", 1, "A", 4.0, 92),
        ("21001", "WEB101", 1, "B", 3.0, 88),
        ("21001", "ALSTD101", 1, "A", 4.0, 90),
        ("21002", "PBO101", 1, "B", 3.0, 85),
        ("21002", "DBMS101", 1, "B", 3.0, 87),
        ("21002", "WEB101", 1, "C", 2.0, 75),
        ("21002", "ALSTD101", 1, "A", 4.0, 91),
        ("21003", "PBO101", 1, "C", 2.0, 78),
        ("21003", "DBMS101", 1, "D", 1.0, 74),
        ("21003", "WEB101", 1, "C", 2.0, 76),
        ("21003", "NET101", 1, "C", 2.0, 77),
    ]
    
    cursor.executemany("""
        INSERT INTO grades (nim, course_code, semester, letter_grade, numeric_grade, presence_percentage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_grades)
    
    conn.commit()
    conn.close()
    print("Sample data populated successfully!")

if __name__ == "__main__":
    init_database()
    populate_sample_data()
