"""
Grade Management System - Input, validation, and conversion of academic grades
"""
from database import get_connection
from datetime import datetime
from typing import Tuple, Optional

# Grade conversion table
GRADE_CONVERSION = {
    'A': 4.0,
    'B': 3.0,
    'C': 2.0,
    'D': 1.0,
    'E': 0.0
}

# Reverse conversion
NUMERIC_TO_GRADE = {
    4.0: 'A',
    3.0: 'B',
    2.0: 'C',
    1.0: 'D',
    0.0: 'E'
}

class GradeManager:
    """Manages grade input, validation, and conversion"""
    
    def __init__(self):
        pass
    
    @staticmethod
    def validate_input(nim: str, course_code: str, letter_grade: str, 
                      presence_percentage: float, semester: int) -> Tuple[bool, str]:
        """
        Validate grade input with business rules
        
        Business Rules:
        - Nilai tidak bisa diinput jika presensi < 75%
        - Huruf grade harus A-E
        - Presence harus 0-100
        - Semester harus positif
        """
        
        # Check presence percentage
        if presence_percentage < 75.0:
            return False, f"Presence {presence_percentage}% kurang dari 75%. Nilai tidak bisa diinput."
        
        # Check grade validity
        if letter_grade not in GRADE_CONVERSION:
            return False, f"Huruf grade '{letter_grade}' tidak valid. Harus A, B, C, D, atau E."
        
        # Check presence range
        if not (0 <= presence_percentage <= 100):
            return False, f"Persentase kehadiran harus antara 0-100."
        
        # Check semester
        if semester < 1:
            return False, f"Semester harus positif."
        
        return True, "Validation passed"
    
    @staticmethod
    def convert_letter_to_numeric(letter_grade: str) -> float:
        """Convert letter grade to numeric value"""
        return GRADE_CONVERSION.get(letter_grade, 0.0)
    
    @staticmethod
    def convert_numeric_to_letter(numeric_grade: float) -> str:
        """Convert numeric grade back to letter"""
        return NUMERIC_TO_GRADE.get(numeric_grade, 'E')
    
    @staticmethod
    def input_grade(nim: str, course_code: str, semester: int, 
                    letter_grade: str, presence_percentage: float = 75.0) -> Tuple[bool, str]:
        """
        Input a grade with validation
        
        Returns:
            Tuple[bool, str]: (success, message)
        """
        
        # Validate input
        is_valid, validation_msg = GradeManager.validate_input(
            nim, course_code, letter_grade, presence_percentage, semester
        )
        
        if not is_valid:
            return False, validation_msg
        
        # Convert letter to numeric
        numeric_grade = GradeManager.convert_letter_to_numeric(letter_grade)
        
        # Insert or update grade
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if grade already exists
            cursor.execute("""
                SELECT grade_id FROM grades 
                WHERE nim = ? AND course_code = ? AND semester = ?
            """, (nim, course_code, semester))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing grade
                grade_id = existing['grade_id']
                
                # Get old values for audit trail
                cursor.execute("""
                    SELECT letter_grade, numeric_grade FROM grades 
                    WHERE grade_id = ?
                """, (grade_id,))
                old_values = cursor.fetchone()
                
                # Update grade
                cursor.execute("""
                    UPDATE grades 
                    SET letter_grade = ?, numeric_grade = ?, 
                        presence_percentage = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE grade_id = ?
                """, (letter_grade, numeric_grade, presence_percentage, grade_id))
                
                # Record in audit trail
                cursor.execute("""
                    INSERT INTO grade_history 
                    (grade_id, old_letter_grade, old_numeric_grade, 
                     new_letter_grade, new_numeric_grade, changed_by, changed_at, reason)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """, (grade_id, old_values['letter_grade'], old_values['numeric_grade'],
                      letter_grade, numeric_grade, 'system', 'Grade updated'))
                
                conn.commit()
                return True, f"Grade updated: {letter_grade} ({numeric_grade})"
            
            else:
                # Insert new grade
                cursor.execute("""
                    INSERT INTO grades 
                    (nim, course_code, semester, letter_grade, numeric_grade, presence_percentage)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (nim, course_code, semester, letter_grade, numeric_grade, presence_percentage))
                
                conn.commit()
                return True, f"Grade inserted: {letter_grade} ({numeric_grade})"
        
        except Exception as e:
            conn.rollback()
            return False, f"Error: {str(e)}"
        
        finally:
            conn.close()
    
    @staticmethod
    def get_grade(nim: str, course_code: str, semester: int) -> Optional[dict]:
        """Get a specific grade"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT g.*, c.sks, c.course_name
            FROM grades g
            JOIN courses c ON g.course_code = c.course_code
            WHERE g.nim = ? AND g.course_code = ? AND g.semester = ?
        """, (nim, course_code, semester))
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    @staticmethod
    def get_all_grades_for_student(nim: str, semester: Optional[int] = None) -> list:
        """Get all grades for a student, optionally filtered by semester"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if semester:
            cursor.execute("""
                SELECT g.*, c.sks, c.course_name
                FROM grades g
                JOIN courses c ON g.course_code = c.course_code
                WHERE g.nim = ? AND g.semester = ?
                ORDER BY g.semester, g.course_code
            """, (nim, semester))
        else:
            cursor.execute("""
                SELECT g.*, c.sks, c.course_name
                FROM grades g
                JOIN courses c ON g.course_code = c.course_code
                WHERE g.nim = ?
                ORDER BY g.semester, g.course_code
            """, (nim,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    @staticmethod
    def get_student_info(nim: str) -> Optional[dict]:
        """Get student information"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students WHERE nim = ?", (nim,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    @staticmethod
    def is_passed(numeric_grade: float) -> bool:
        """
        Check if student passed the course
        Business Rule: Lulus MK jika nilai >= D (2.0)
        """
        return numeric_grade >= 1.0  # D grade is 1.0
    
    @staticmethod
    def get_grade_history(nim: str) -> list:
        """Get audit trail for a student"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM grade_changes_summary
            WHERE nim = ?
            ORDER BY changed_at DESC
        """, (nim,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]


if __name__ == "__main__":
    # Test the grade manager
    print("Testing Grade Manager...")
    
    # Test validation
    is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 95, 1)
    print(f"Validation test 1: {is_valid} - {msg}")
    
    # Test with low presence
    is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 70, 1)
    print(f"Validation test 2 (low presence): {is_valid} - {msg}")
    
    # Test conversion
    numeric = GradeManager.convert_letter_to_numeric("A")
    print(f"Grade A converts to: {numeric}")
    
    letter = GradeManager.convert_numeric_to_letter(4.0)
    print(f"Grade 4.0 converts to: {letter}")
    
    # Test input
    success, msg = GradeManager.input_grade("21001", "PBO101", 1, "A", 95)
    print(f"Grade input test: {success} - {msg}")
    
    # Get grade
    grade = GradeManager.get_grade("21001", "PBO101", 1)
    print(f"Grade retrieved: {grade}")
