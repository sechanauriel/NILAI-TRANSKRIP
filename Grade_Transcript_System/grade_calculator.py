"""
GPA/IPK Calculator - Calculate semester GPA (IPS) and cumulative GPA (IPK)
"""
from database import get_connection
from grade_manager import GradeManager
from typing import Tuple, Optional, List, Dict

class GradeCalculator:
    """Calculate academic performance metrics"""
    
    PREDICATE_GRADES = {
        'Cum Laude': 3.5,
        'Sangat Memuaskan': 3.0,
        'Memuaskan': 2.75,
        'Cukup': 2.0,
        'Kurang': 0.0
    }
    
    @staticmethod
    def calculate_ips(nim: str, semester: int) -> float:
        """
        Calculate Indeks Prestasi Semester (IPS) - GPA for a specific semester
        
        Formula: IPK = Σ(SKS × Nilai Angka) / Σ(SKS)
        
        Rules:
        - Only count courses with nilai >= D (1.0) [PASSED]
        - If course is repeated, take the highest grade
        
        Args:
            nim: Student ID
            semester: Semester number
            
        Returns:
            float: IPS value (0.0 - 4.0)
        """
        
        grades_data = GradeManager.get_all_grades_for_student(nim, semester)
        
        if not grades_data:
            return 0.0  # No grades in this semester
        
        total_weighted_grade = 0.0
        total_sks = 0
        
        for grade in grades_data:
            # Only count passed courses (nilai >= D = 1.0)
            if GradeManager.is_passed(grade['numeric_grade']):
                sks = grade['sks']
                numeric_grade = grade['numeric_grade']
                
                total_weighted_grade += (sks * numeric_grade)
                total_sks += sks
        
        if total_sks == 0:
            return 0.0
        
        ips = total_weighted_grade / total_sks
        return round(ips, 2)
    
    @staticmethod
    def calculate_ipk(nim: str) -> float:
        """
        Calculate Indeks Prestasi Kumulatif (IPK) - Cumulative GPA
        
        Formula: IPK = Σ(SKS × Nilai Angka) / Σ(SKS) for all semesters
        
        Rules:
        - Only count courses with nilai >= D (1.0) [PASSED]
        - If course is repeated, take the highest grade only
        
        Args:
            nim: Student ID
            
        Returns:
            float: IPK value (0.0 - 4.0)
        """
        
        grades_data = GradeManager.get_all_grades_for_student(nim)
        
        if not grades_data:
            return 0.0  # Semester 1 belum ada nilai
        
        # Handle repeated courses - keep only the highest grade per course
        course_grades = {}
        for grade in grades_data:
            course_code = grade['course_code']
            
            if course_code not in course_grades:
                course_grades[course_code] = grade
            else:
                # If course exists, keep the one with higher grade
                if grade['numeric_grade'] > course_grades[course_code]['numeric_grade']:
                    course_grades[course_code] = grade
        
        total_weighted_grade = 0.0
        total_sks = 0
        
        # Calculate IPK using only the highest grade per course
        for course_code, grade in course_grades.items():
            # Only count passed courses (nilai >= D = 1.0)
            if GradeManager.is_passed(grade['numeric_grade']):
                sks = grade['sks']
                numeric_grade = grade['numeric_grade']
                
                total_weighted_grade += (sks * numeric_grade)
                total_sks += sks
        
        if total_sks == 0:
            return 0.0
        
        ipk = total_weighted_grade / total_sks
        return round(ipk, 2)
    
    @staticmethod
    def get_transcript(nim: str) -> Dict:
        """
        Get complete academic record for a student
        
        Returns:
            Dict: Complete transcript with all semesters, courses, grades, and metrics
        """
        
        # Get student info
        student = GradeManager.get_student_info(nim)
        if not student:
            return {}
        
        # Get all grades
        all_grades = GradeManager.get_all_grades_for_student(nim)
        
        # Organize by semester
        transcript_by_semester = {}
        for grade in all_grades:
            semester = grade['semester']
            if semester not in transcript_by_semester:
                transcript_by_semester[semester] = []
            transcript_by_semester[semester].append(grade)
        
        # Calculate metrics for each semester
        semesters_data = []
        total_sks_all = 0
        
        for semester in sorted(transcript_by_semester.keys()):
            grades = transcript_by_semester[semester]
            
            # Calculate semester total SKS (passed courses only)
            semester_sks = sum(g['sks'] for g in grades 
                              if GradeManager.is_passed(g['numeric_grade']))
            total_sks_all += semester_sks
            
            # Calculate IPS for this semester
            ips = GradeCalculator.calculate_ips(nim, semester)
            
            semesters_data.append({
                'semester': semester,
                'ips': ips,
                'total_sks': semester_sks,
                'courses': grades
            })
        
        # Calculate IPK
        ipk = GradeCalculator.calculate_ipk(nim)
        
        # Determine graduation predicate
        predicate = GradeCalculator.get_graduation_predicate(ipk)
        
        # Build transcript
        transcript = {
            'student': dict(student),
            'semesters': semesters_data,
            'total_sks': total_sks_all,
            'ipk': ipk,
            'graduation_predicate': predicate,
            'number_of_semesters': len(semesters_data)
        }
        
        return transcript
    
    @staticmethod
    def get_graduation_predicate(ipk: float) -> str:
        """
        Determine graduation predicate based on IPK
        
        Predicates:
        - IPK >= 3.5: Cum Laude
        - IPK >= 3.0 & < 3.5: Sangat Memuaskan
        - IPK >= 2.75 & < 3.0: Memuaskan
        - IPK >= 2.0 & < 2.75: Cukup
        - IPK < 2.0: Kurang
        """
        
        if ipk >= 3.5:
            return 'Cum Laude'
        elif ipk >= 3.0:
            return 'Sangat Memuaskan'
        elif ipk >= 2.75:
            return 'Memuaskan'
        elif ipk >= 2.0:
            return 'Cukup'
        else:
            return 'Kurang'
    
    @staticmethod
    def get_semester_summary(nim: str, semester: int) -> Dict:
        """Get summary for a specific semester"""
        
        grades = GradeManager.get_all_grades_for_student(nim, semester)
        ips = GradeCalculator.calculate_ips(nim, semester)
        
        total_sks = sum(g['sks'] for g in grades)
        passed_sks = sum(g['sks'] for g in grades if GradeManager.is_passed(g['numeric_grade']))
        failed_count = sum(1 for g in grades if not GradeManager.is_passed(g['numeric_grade']))
        
        return {
            'semester': semester,
            'courses': grades,
            'ips': ips,
            'total_sks': total_sks,
            'passed_sks': passed_sks,
            'failed_courses': failed_count,
            'average_grade': round(sum(g['numeric_grade'] for g in grades) / len(grades), 2) if grades else 0.0
        }
    
    @staticmethod
    def get_performance_statistics(nim: str) -> Dict:
        """Get detailed performance statistics for a student"""
        
        all_grades = GradeManager.get_all_grades_for_student(nim)
        
        if not all_grades:
            return {
                'total_courses': 0,
                'passed_courses': 0,
                'failed_courses': 0,
                'total_sks': 0,
                'passed_sks': 0,
                'average_grade': 0.0
            }
        
        passed_count = sum(1 for g in all_grades if GradeManager.is_passed(g['numeric_grade']))
        passed_sks = sum(g['sks'] for g in all_grades if GradeManager.is_passed(g['numeric_grade']))
        total_sks = sum(g['sks'] for g in all_grades)
        average_grade = round(sum(g['numeric_grade'] for g in all_grades) / len(all_grades), 2)
        
        return {
            'total_courses': len(all_grades),
            'passed_courses': passed_count,
            'failed_courses': len(all_grades) - passed_count,
            'total_sks': total_sks,
            'passed_sks': passed_sks,
            'average_grade': average_grade
        }


if __name__ == "__main__":
    # Test the calculator
    print("Testing Grade Calculator...")
    
    # Test IPS calculation
    ips = GradeCalculator.calculate_ips("21001", 1)
    print(f"IPS Semester 1 for student 21001: {ips}")
    
    # Test IPK calculation
    ipk = GradeCalculator.calculate_ipk("21001")
    print(f"IPK for student 21001: {ipk}")
    
    # Test predicate
    predicate = GradeCalculator.get_graduation_predicate(ipk)
    print(f"Graduation predicate: {predicate}")
    
    # Test transcript
    transcript = GradeCalculator.get_transcript("21001")
    print(f"\nTranscript for {transcript['student']['name']}:")
    print(f"Total SKS: {transcript['total_sks']}")
    print(f"IPK: {transcript['ipk']}")
    print(f"Predicate: {transcript['graduation_predicate']}")
    print(f"Number of semesters: {transcript['number_of_semesters']}")
    
    # Test performance stats
    stats = GradeCalculator.get_performance_statistics("21001")
    print(f"\nPerformance Statistics:")
    print(f"Total Courses: {stats['total_courses']}")
    print(f"Passed: {stats['passed_courses']}, Failed: {stats['failed_courses']}")
    print(f"Average Grade: {stats['average_grade']}")
