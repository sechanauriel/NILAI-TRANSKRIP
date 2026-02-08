# 🎓 Grade & Transcript Management System

## 📋 Project Overview

Sistem Manajemen Nilai dan Transkrip Akademik (Grade & Transcript Management System) adalah aplikasi web lengkap untuk mengelola nilai akademik mahasiswa, menghitung GPA/IPK, menghasilkan transkrip resmi dalam format PDF, dan melacak audit trail semua perubahan nilai.

Sistem ini dibangun sesuai dengan spesifikasi modul MINGGU 9-10 dengan implementasi 100% dari semua requirement.

## ✨ Fitur Utama

### 1. Grade Management (30%)
- ✅ Input nilai per mahasiswa per MK (A/B/C/D/E)
- ✅ Konversi huruf → angka otomatis (A=4.0, B=3.0, C=2.0, D=1.0, E=0.0)
- ✅ Edit nilai dengan audit trail (siapa ubah, kapan)
- ✅ Validasi kehadiran minimum 75%
- ✅ Interface user-friendly untuk input data

### 2. GPA Calculator (30%)
- ✅ `calculate_ips(nim, semester)` → IP semester
- ✅ `calculate_ipk(nim)` → IP kumulatif
- ✅ `get_transcript(nim)` → full academic record
- ✅ Penanganan MK yang diulang (ambil nilai tertinggi)
- ✅ Penanganan edge case (mahasiswa semester 1 belum ada nilai)

### 3. PDF Generator (25%)
- ✅ Template transkrip resmi dengan logo, header, footer
- ✅ Tabel semester: MK, SKS, Nilai, Mutu
- ✅ Summary: Total SKS, IPK, Predikat kelulusan
- ✅ Download instan dari sistem
- ✅ Layout profesional seperti ijazah resmi

### 4. Business Rules (10%)
- ✅ Nilai tidak bisa diinput jika presensi < 75%
- ✅ Lulus MK jika nilai ≥ D (2.0)
- ✅ Predikat: Cum Laude (IPK≥3.5), Sangat Memuaskan (3.0-3.49), Memuaskan (2.75-2.99), Cukup (2.0-2.74), Kurang (<2.0)

### 5. Audit Trail System
- ✅ Tabel `grade_history` untuk track perubahan nilai
- ✅ Kolom: old_value, new_value, changed_by, changed_at, reason
- ✅ View `grade_changes_summary` untuk lihat riwayat
- ✅ Automatis trigger saat ada perubahan nilai

### 6. Tests (5%)
- ✅ 30+ unit test cases
- ✅ Test perhitungan IPK dengan multiple cases
- ✅ Test validasi business rules
- ✅ Test PDF generation
- ✅ Test edge cases

## 🏗️ Struktur Proyek

```
Grade_Transcript_System/
├── database.py              # Database initialization & schema
├── grade_manager.py         # Grade input, validation, conversion
├── grade_calculator.py      # GPA/IPK calculation logic
├── transcript_generator.py  # PDF generation
├── app.py                   # Flask web application
├── test_system.py          # Comprehensive test suite (30+ tests)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── templates/             # HTML templates
│   ├── index.html
│   ├── grades.html
│   ├── transcript.html
│   ├── analytics.html
│   └── audit_trail.html
└── transcripts/           # Generated PDF output directory
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Navigate to project directory
cd Grade_Transcript_System

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/Scripts/activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python database.py
```

This will:
- Create SQLite database with all tables
- Populate sample data (3 students, 5 courses, sample grades)
- Setup audit trail system

### 3. Run Tests

```bash
python test_system.py
```

Runs 30+ test cases covering:
- Grade validation (7 tests)
- Grade conversion (6 tests)
- Business rules (5 tests)
- IPS calculation (5 tests)
- IPK calculation (5 tests)
- Graduation predicate (6 tests)
- Transcript generation (4 tests)
- Performance statistics (3 tests)
- PDF generation (3 tests)
- Edge cases (5 tests)

### 4. Run Web Application

```bash
python app.py
```

Application akan berjalan di `http://localhost:5000`

## 📖 Module Documentation

### Grade Manager (grade_manager.py)

**Main Classes:**
- `GradeManager` - Manages grade operations

**Key Methods:**
```python
# Validation
validate_input(nim, course_code, letter_grade, presence_pct, semester)
→ (bool, str)  # Returns (is_valid, message)

# Grade input
input_grade(nim, course_code, semester, letter_grade, presence_percentage)
→ (bool, str)  # Returns (success, message)

# Conversion
convert_letter_to_numeric(letter_grade)  # A → 4.0
convert_numeric_to_letter(numeric_grade) # 4.0 → A

# Retrieval
get_grade(nim, course_code, semester)
get_all_grades_for_student(nim, semester=None)
get_student_info(nim)
is_passed(numeric_grade)  # >= 1.0 = passed
get_grade_history(nim)    # Audit trail
```

**Validation Rules:**
- Presence must be ≥ 75%
- Grade must be A-E
- Presence range: 0-100%
- Semester must be positive

### Grade Calculator (grade_calculator.py)

**Main Class:**
- `GradeCalculator` - Calculates academic metrics

**Key Methods:**
```python
# Calculate IPS for semester
calculate_ips(nim, semester) → float
# Formula: Σ(SKS × Nilai Angka) / Σ(SKS)

# Calculate IPK (cumulative)
calculate_ipk(nim) → float
# Only counts highest grade if course repeated

# Get full transcript
get_transcript(nim) → dict
# Returns: student info, semesters data, IPK, predicate

# Determine graduation predicate
get_graduation_predicate(ipk) → str
# Cum Laude (≥3.5), Sangat Memuaskan (3.0-3.49), etc.

# Get performance statistics
get_performance_statistics(nim) → dict
# Total/passed/failed courses, SKS, average grade

# Get semester summary
get_semester_summary(nim, semester) → dict
```

### Transcript Generator (transcript_generator.py)

**Main Class:**
- `TranscriptGenerator` - Generates PDF transcripts

**Key Methods:**
```python
generate_transcript(nim, filename=None) → str
# Returns: filepath to generated PDF
# Includes:
# - Header with university name
# - Student biodata
# - Grades table per semester
# - Academic summary
# - Signature section
```

**Features:**
- Professional A4 layout
- Color-coded tables
- Logo and header/footer
- Semester-by-semester breakdown
- Total SKS and IPK summary
- Signature lines for officials

### Flask Application (app.py)

**API Endpoints:**

**Students & Courses:**
- `GET /api/students` - List all students
- `GET /api/courses` - List all courses
- `GET /api/student/<nim>` - Get student details

**Grades:**
- `GET /api/grades/<nim>` - Get student grades
- `POST /api/grade` - Input new grade

**Calculations:**
- `GET /api/calculator/ips/<nim>/<semester>` - Get IPS
- `GET /api/calculator/ipk/<nim>` - Get IPK
- `GET /api/transcript/<nim>` - Get full transcript

**Reports:**
- `GET /api/performance-stats/<nim>` - Performance statistics
- `GET /api/audit-trail/<nim>` - Grade change history

**PDF & Downloads:**
- `GET /download-transcript/<nim>` - Download transcript PDF

**Web Pages:**
- `GET /` - Home page
- `GET /grades` - Grade management page
- `GET /transcript` - Transcript viewer
- `GET /analytics` - Analytics dashboard
- `GET /audit-trail` - Audit trail viewer

## 🗄️ Database Schema

### Tables

**students**
- nim (TEXT, PRIMARY KEY)
- name (TEXT)
- program_study (TEXT)
- batch_year (INTEGER)
- created_at (TIMESTAMP)

**courses**
- course_code (TEXT, PRIMARY KEY)
- course_name (TEXT)
- sks (INTEGER)
- created_at (TIMESTAMP)

**grades**
- grade_id (INTEGER, PRIMARY KEY)
- nim (TEXT, FOREIGN KEY)
- course_code (TEXT, FOREIGN KEY)
- semester (INTEGER)
- letter_grade (TEXT)
- numeric_grade (REAL)
- presence_percentage (REAL)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**grade_history** (Audit Trail)
- history_id (INTEGER, PRIMARY KEY)
- grade_id (INTEGER, FOREIGN KEY)
- old_letter_grade (TEXT)
- old_numeric_grade (REAL)
- new_letter_grade (TEXT)
- new_numeric_grade (REAL)
- changed_by (TEXT)
- changed_at (TIMESTAMP)
- reason (TEXT)

**Views:**
- `grade_changes_summary` - Easy access to audit trail

## 🧪 Test Coverage

### Test Categories

1. **Grade Validation Tests (7)**
   - Valid input acceptance
   - Presence < 75% rejection
   - Invalid grade letter rejection
   - Invalid presence range
   - Invalid semester
   - All valid grades A-E

2. **Conversion Tests (6)**
   - Letter to numeric conversion
   - Numeric to letter conversion
   - Round-trip conversion

3. **Business Rules Tests (5)**
   - Pass condition (grade ≥ D = 1.0)
   - Fail condition (grade < D = 0.0)
   - All grades pass status

4. **GPA Calculation Tests (10)**
   - IPS calculation accuracy
   - IPK calculation accuracy
   - Handling of all A grades
   - Handling of mixed grades
   - Handling of repeated courses
   - Edge cases (no grades, zero SKS)

5. **Graduation Predicate Tests (6)**
   - Cum Laude (IPK ≥ 3.5)
   - Sangat Memuaskan (3.0-3.49)
   - Memuaskan (2.75-2.99)
   - Cukup (2.0-2.74)
   - Kurang (< 2.0)

6. **Transcript Tests (4)**
   - Transcript retrieval
   - Student info accuracy
   - Semester structure
   - Non-existent student handling

7. **Performance Statistics Tests (3)**
   - Statistics structure
   - Non-negative values
   - Empty data handling

8. **PDF Generation Tests (3)**
   - File creation
   - File size verification
   - Content accuracy

9. **Edge Cases Tests (5)**
   - Zero SKS handling
   - Empty database
   - Unicode handling
   - Large datasets
   - Concurrent access

## 💡 Usage Examples

### 1. Input Grade via API

```python
import requests

data = {
    'nim': '21001',
    'course_code': 'PBO101',
    'semester': 1,
    'letter_grade': 'A',
    'presence_percentage': 95
}

response = requests.post('http://localhost:5000/api/grade', json=data)
print(response.json())  # {'success': True, 'message': '...'}
```

### 2. Get Transcript

```python
response = requests.get('http://localhost:5000/api/transcript/21001')
transcript = response.json()

print(f"Student: {transcript['student']['name']}")
print(f"IPK: {transcript['ipk']}")
print(f"Predicate: {transcript['graduation_predicate']}")
```

### 3. Generate PDF

```python
import requests

response = requests.get('http://localhost:5000/download-transcript/21001')
with open('transcript.pdf', 'wb') as f:
    f.write(response.content)
```

### 4. Get Performance Stats

```python
response = requests.get('http://localhost:5000/api/performance-stats/21001')
stats = response.json()

print(f"Total Courses: {stats['total_courses']}")
print(f"Passed: {stats['passed_courses']}")
print(f"Failed: {stats['failed_courses']}")
print(f"Average Grade: {stats['average_grade']}")
```

## 📊 Sample Data

System dilengkapi dengan sample data:

**Students:**
- 21001 - Ahmad Pratama (Teknik Informatika)
- 21002 - Siti Nurhaliza (Sistem Informasi)
- 21003 - Budi Santoso (Teknik Komputer)

**Courses:**
- PBO101 - Pemrograman Berorientasi Objek (3 SKS)
- DBMS101 - Sistem Basis Data (3 SKS)
- WEB101 - Pengembangan Web (4 SKS)
- ALSTD101 - Algoritma dan Struktur Data (3 SKS)
- NET101 - Jaringan Komputer (3 SKS)

**Grades:**
- Pre-populated for Semester 1
- Student 21001: All A's (IPK = 4.0)
- Student 21002: Mixed grades B, B, C, A (IPK ≈ 3.0)
- Student 21003: Mixed grades C, D, C, C

## 🔧 Configuration

### Database
- Type: SQLite
- File: `transcript_system.db`
- Location: Project root directory

### Flask
- Host: localhost
- Port: 5000
- Debug: True (development)

### PDF Output
- Directory: `transcripts/`
- Format: `Transcript_{NIM}_{TIMESTAMP}.pdf`

## 📝 Business Rules Implementation

### Rule 1: Presence Validation
```python
if presence_percentage < 75.0:
    return False  # Cannot input grade
```

### Rule 2: Pass/Fail Status
```python
if numeric_grade >= 1.0:  # D grade or higher
    passed = True
else:
    passed = False
```

### Rule 3: Grade Repetition
```python
# If course repeated, take highest grade
if course_code in grades_dict:
    if new_grade > existing_grade:
        grades_dict[course_code] = new_grade
```

### Rule 4: Graduation Predicate
```python
if ipk >= 3.5:
    predicate = "Cum Laude"
elif ipk >= 3.0:
    predicate = "Sangat Memuaskan"
# ... etc
```

## 🐛 Troubleshooting

### Database Already Exists
```python
# Delete old database
import os
os.remove('transcript_system.db')

# Re-initialize
python database.py
```

### Port Already in Use
```bash
# Use different port
python -c "from app import app; app.run(port=5001)"
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📦 Dependencies

- **Flask** 2.3.3 - Web framework
- **ReportLab** 4.0.4 - PDF generation
- **SQLite3** - Database (built-in Python)
- **Pillow** 10.0.0 - Image processing (for PDF)

## 🎯 Deliverables Checklist

- ✅ **Grade Management (30%)**: Full implementation with validation
- ✅ **GPA Calculator (30%)**: IPS, IPK, transcript functions
- ✅ **PDF Generator (25%)**: Professional template with all sections
- ✅ **Business Rules (10%)**: All rules implemented and validated
- ✅ **Tests (5%)**: 30+ comprehensive test cases
- ✅ **Audit Trail**: Grade change tracking system
- ✅ **Web Interface**: Complete UI for all operations
- ✅ **Documentation**: Full API and usage documentation

## 📄 License

Educational Project - MINGGU 9-10 Module

## 👨‍💼 Developer Notes

### Key Implementation Decisions

1. **SQLite Database**: Lightweight, no external database needed
2. **Flask Framework**: Simple, perfect for this scope
3. **ReportLab**: Pure Python PDF generation, no external tools
4. **MVC Pattern**: Separation of concerns (models, views, controllers)
5. **RESTful API**: Easy to test and extend

### Code Quality

- Clean, documented code with docstrings
- Comprehensive error handling
- Validation at every input point
- Transaction management for data integrity
- Audit logging for compliance

### Performance

- Database indexes on primary keys
- Efficient queries with proper joins
- Minimal PDF file sizes
- Response caching where appropriate

## 🔒 Security Notes

- Input validation on all grade inputs
- SQL injection prevention via parameterized queries
- Type checking for all parameters
- Presence validation (business rule enforcement)
- Audit trail for compliance

## 🚀 Future Enhancements

Possible improvements for future versions:
1. User authentication and roles
2. Email notifications for grade updates
3. GPA prediction based on current performance
4. Export to Excel
5. Batch grade import
6. Mobile app
7. Real-time notifications
8. Advanced analytics dashboard
9. Integration with other systems
10. Multi-language support

---

**Created**: January 2024
**Status**: Complete (100% Module Fulfillment)
**Test Coverage**: 30+ Test Cases
**Documentation**: Comprehensive
