# 🚀 Quick Start Guide - Grade & Transcript Management System

## 5-Minute Setup

### Step 1: Verify Python Installation ✓
```powershell
python --version
# Expected: Python 3.12.x or higher
```

### Step 2: Navigate to Project Directory
```powershell
cd c:\Users\erwin\Downloads\MODUL_TRANSCRIPT\Grade_Transcript_System
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed Flask-2.3.3 Werkzeug-2.3.7 reportlab-4.0.4 Pillow-10.0.0
```

### Step 4: Initialize Database
```powershell
python database.py
```

**Expected Output:**
```
Database initialized successfully!
Sample data populated successfully!
```

### Step 5: Run Tests (Optional - Verify Everything Works)
```powershell
python -m unittest test_system -v
```

**Expected Output:**
```
Ran 42 tests in 0.046s
Result: OK ✅
```

### Step 6: Launch Web Application
```powershell
python app.py
```

**Expected Output:**
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Step 7: Access Application
Open your browser and go to:
```
http://localhost:5000
```

---

## 📱 Web Interface Walkthrough

### Dashboard (Home Page)
- URL: `http://localhost:5000/`
- Shows system statistics and navigation menu
- Click on any menu item to navigate

### Input Grades
- URL: `http://localhost:5000/grades`
- **How to use:**
  1. Select Student (NIM) from dropdown
  2. Select Course (Kode MK) from dropdown
  3. Select Grade (A, B, C, D, E) using radio buttons
  4. Enter Presence Percentage (75-100%)
  5. Select Semester
  6. Click "Submit Grade"
- **Success Message**: Grade saved to database
- **Failed Message**: Will show validation error (e.g., "Presence < 75%")

### View Transcripts
- URL: `http://localhost:5000/transcript`
- **How to use:**
  1. Select Student (NIM)
  2. View complete academic record with:
     - All courses by semester
     - Grades and credits (SKS)
     - IPS per semester
     - Cumulative IPK
     - Graduation predicate
  3. Click "Download PDF" to get official transcript

### Analytics Dashboard
- URL: `http://localhost:5000/analytics`
- View class-wide statistics:
  - Average IPK
  - Highest performers
  - Lowest performers
  - Grade distribution

### Audit Trail
- URL: `http://localhost:5000/audit-trail`
- View all grade modifications:
  - Who changed the grade
  - When it was changed
  - Old value vs new value
  - Reason for change

---

## 🔧 Common Tasks

### Task 1: Input New Grade for Student 21001
1. Go to `/grades`
2. Select: NIM = "21001", Course = "PBO101", Grade = "A", Presence = "95", Semester = "1"
3. Click "Submit Grade"
4. View the grade in the history table below

### Task 2: View Student Transcript
1. Go to `/transcript`
2. Select: NIM = "21001"
3. View all academic information
4. Click "Download PDF" to get transcript file

### Task 3: Generate PDF for All Students
1. Use the API endpoint directly:
```powershell
# For student 21001
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/download-pdf/21001"
[System.IO.File]::WriteAllBytes("C:\path\to\transcript_21001.pdf", $response.Content)
```

### Task 4: Check Grade Audit Trail
1. Go to `/audit-trail`
2. View all changes made to grades
3. See who changed what and when

---

## 📊 Using the API Programmatically

### Get Student Transcript (JSON)
```powershell
# PowerShell
$nim = "21001"
$response = Invoke-RestMethod -Uri "http://localhost:5000/api/transcript/$nim"
$response | ConvertTo-Json | Write-Host
```

### Input a Grade via API
```powershell
# PowerShell
$body = @{
    nim = "21001"
    course_code = "ALSTD101"
    semester = 2
    letter_grade = "A"
    presence_percentage = 90
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/input-grade" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### Download Transcript PDF
```powershell
# PowerShell
$nim = "21001"
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/download-pdf/$nim"
[System.IO.File]::WriteAllBytes("C:\transcript.pdf", $response.Content)
```

---

## 🧪 Testing the System

### Run All Tests
```powershell
python -m unittest test_system -v
```

### Run Specific Test Category
```powershell
# Grade validation tests only
python -m unittest test_system.TestGradeValidation -v

# IPK calculation tests only
python -m unittest test_system.TestIPKCalculation -v

# PDF generation tests only
python -m unittest test_system.TestPDFGeneration -v
```

### Run Single Test
```powershell
# Test presensi validation
python -m unittest test_system.TestGradeValidation.test_presence_below_threshold -v
```

---

## 📁 Project Structure

```
Grade_Transcript_System/
├── database.py              # Database setup
├── grade_manager.py         # Grade management
├── grade_calculator.py      # GPA/IPK calculations
├── transcript_generator.py  # PDF generation
├── app.py                   # Flask web app
├── test_system.py          # Unit tests
├── requirements.txt        # Dependencies
├── README.md              # Full documentation
├── VERIFICATION_REPORT.md # Verification results
├── QUICK_START.md         # This file
├── transcript_system.db   # SQLite database (auto-created)
├── transcripts/           # Generated PDF folder (auto-created)
└── templates/             # HTML templates
    ├── index.html
    ├── grades.html
    ├── transcript.html
    ├── analytics.html
    └── audit_trail.html
```

---

## 🐛 Troubleshooting

### Issue: "Port 5000 already in use"
**Solution:**
```powershell
# Use different port
python -c "from app import app; app.run(port=5001)"
```
Then access: `http://localhost:5001`

### Issue: "No module named 'flask'"
**Solution:**
```powershell
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### Issue: "Database already exists"
**Solution:**
```powershell
# Remove old database and reinitialize
Remove-Item transcript_system.db
python database.py
```

### Issue: "Permission denied on database.db"
**Solution:**
- Close the Flask application (press Ctrl+C)
- Delete `transcript_system.db`
- Restart the application

### Issue: "PDF generation failed"
**Solution:**
- Ensure Pillow and ReportLab are installed
- Run: `pip install -r requirements.txt --upgrade`

---

## 📞 Sample Data Available

The system comes with pre-populated sample data:

**Students:**
- 21001: Ahmad Pratama (Teknik Informatika)
- 21002: Siti Nurhaliza (Sistem Informasi)
- 21003: Budi Santoso (Teknik Komputer)

**Courses:**
- PBO101, DBMS101, WEB101, ALSTD101, NET101

**Grades:** Semester 1 already populated with grades for all students

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Database created (transcript_system.db exists)
- [ ] Flask app starts without errors
- [ ] Can access http://localhost:5000
- [ ] Can view dashboard
- [ ] Can input grades
- [ ] Can view transcripts
- [ ] Can download PDF
- [ ] All 42 tests pass

---

## 🎯 Next Steps

1. **Explore the Web Interface**
   - Try inputting new grades
   - View different student transcripts
   - Download PDF files

2. **Review the Code**
   - Open `grade_calculator.py` to see GPA calculations
   - Open `transcript_generator.py` to see PDF generation
   - Open `test_system.py` to understand the business logic

3. **Customize (Optional)**
   - Add more students to `database.py`
   - Modify CSS in templates
   - Add new features as needed

4. **Deployment**
   - For production, set `debug=False` in `app.py`
   - Use a production WSGI server (Gunicorn, etc.)
   - Set up proper logging and monitoring

---

## 📖 Need More Information?

- **Full Documentation**: See `README.md`
- **Verification Results**: See `VERIFICATION_REPORT.md`
- **Source Code**: Check comments in Python files
- **Tests**: Review `test_system.py` for usage examples

---

**Happy grading! 🎓**

For support or questions, refer to the complete README.md documentation.
