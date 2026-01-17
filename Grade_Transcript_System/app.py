"""
Flask Web Application for Grade & Transcript Management System
"""
from flask import Flask, render_template, request, jsonify, send_file, session
from grade_manager import GradeManager
from grade_calculator import GradeCalculator
from transcript_generator import TranscriptGenerator
from database import get_connection, init_database, populate_sample_data
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Initialize database
init_database()
populate_sample_data()

# Initialize transcript generator
transcript_gen = TranscriptGenerator()

# ===================== ROUTES =====================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY nim")
    students = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(students)

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM courses ORDER BY course_code")
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(courses)

@app.route('/api/student/<nim>', methods=['GET'])
def get_student_details(nim):
    """Get student details"""
    student = GradeManager.get_student_info(nim)
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify(student)

@app.route('/api/grades/<nim>', methods=['GET'])
def get_student_grades(nim):
    """Get all grades for a student"""
    semester = request.args.get('semester', type=int)
    grades = GradeManager.get_all_grades_for_student(nim, semester)
    return jsonify(grades)

@app.route('/api/grade', methods=['POST'])
def input_grade_api():
    """API endpoint to input a grade"""
    data = request.json
    
    try:
        success, message = GradeManager.input_grade(
            nim=data['nim'],
            course_code=data['course_code'],
            semester=int(data['semester']),
            letter_grade=data['letter_grade'],
            presence_percentage=float(data.get('presence_percentage', 75))
        )
        
        return jsonify({
            'success': success,
            'message': message
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

@app.route('/api/calculator/ips/<nim>/<int:semester>', methods=['GET'])
def get_ips(nim, semester):
    """Calculate IPS for a semester"""
    ips = GradeCalculator.calculate_ips(nim, semester)
    return jsonify({
        'nim': nim,
        'semester': semester,
        'ips': ips
    })

@app.route('/api/calculator/ipk/<nim>', methods=['GET'])
def get_ipk(nim):
    """Calculate IPK"""
    ipk = GradeCalculator.calculate_ipk(nim)
    predicate = GradeCalculator.get_graduation_predicate(ipk)
    return jsonify({
        'nim': nim,
        'ipk': ipk,
        'predicate': predicate
    })

@app.route('/api/transcript/<nim>', methods=['GET'])
def get_transcript_api(nim):
    """Get full transcript"""
    transcript = GradeCalculator.get_transcript(nim)
    if not transcript:
        return jsonify({'error': 'No transcript data found'}), 404
    return jsonify(transcript)

@app.route('/api/performance-stats/<nim>', methods=['GET'])
def get_performance_stats(nim):
    """Get performance statistics"""
    stats = GradeCalculator.get_performance_statistics(nim)
    return jsonify(stats)

@app.route('/api/audit-trail/<nim>', methods=['GET'])
def get_audit_trail(nim):
    """Get grade change audit trail"""
    history = GradeManager.get_grade_history(nim)
    return jsonify(history)

# ===================== PDF GENERATION ROUTES =====================

@app.route('/download-transcript/<nim>', methods=['GET'])
def download_transcript(nim):
    """Download transcript as PDF"""
    try:
        student = GradeManager.get_student_info(nim)
        if not student:
            return "Student not found", 404
        
        filename = f"Transcript_{nim}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = transcript_gen.generate_transcript(nim, filename)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return f"Error generating transcript: {str(e)}", 500

# ===================== WEB INTERFACE ROUTES =====================

@app.route('/grades')
def grades_page():
    """Grade management page"""
    return render_template('grades.html')

@app.route('/transcript')
def transcript_page():
    """Transcript view page"""
    return render_template('transcript.html')

@app.route('/analytics')
def analytics_page():
    """Analytics and reports page"""
    return render_template('analytics.html')

@app.route('/audit-trail')
def audit_page():
    """Audit trail page"""
    return render_template('audit_trail.html')

# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    # Create transcripts directory if it doesn't exist
    if not os.path.exists('transcripts'):
        os.makedirs('transcripts')
    
    print("=" * 50)
    print("Grade & Transcript Management System")
    print("=" * 50)
    print("Database initialized and sample data loaded")
    print("Visit http://localhost:5000 to access the system")
    print("=" * 50)
    
    app.run(debug=True, port=5000)
