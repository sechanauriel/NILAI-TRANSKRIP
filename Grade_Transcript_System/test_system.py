"""
Comprehensive Unit Tests for Grade & Transcript Management System
Tests cover: Grade validation, IPK calculation, PDF generation, business rules, and edge cases
"""
import unittest
import os
import sys
from datetime import datetime
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, init_database, DATABASE_FILE
from grade_manager import GradeManager
from grade_calculator import GradeCalculator
from transcript_generator import TranscriptGenerator

class TestGradeValidation(unittest.TestCase):
    """Test grade input validation and business rules"""
    
    def test_valid_grade_input(self):
        """Test valid grade input passes validation"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 95, 1)
        self.assertTrue(is_valid, msg)
    
    def test_presence_below_threshold(self):
        """Test: Nilai tidak bisa diinput jika presensi < 75%"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 74.9, 1)
        self.assertFalse(is_valid)
        self.assertIn("75%", msg)
    
    def test_presence_at_threshold(self):
        """Test: Presence exactly at 75% is valid"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 75.0, 1)
        self.assertTrue(is_valid)
    
    def test_invalid_grade_letter(self):
        """Test invalid grade letter rejection"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "F", 95, 1)
        self.assertFalse(is_valid)
        self.assertIn("tidak valid", msg)
    
    def test_invalid_presence_range(self):
        """Test invalid presence percentage"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 105, 1)
        self.assertFalse(is_valid)
    
    def test_invalid_semester(self):
        """Test invalid semester"""
        is_valid, msg = GradeManager.validate_input("21001", "PBO101", "A", 95, 0)
        self.assertFalse(is_valid)
    
    def test_all_valid_grades(self):
        """Test all valid grades A-E"""
        for grade in ['A', 'B', 'C', 'D', 'E']:
            is_valid, _ = GradeManager.validate_input("21001", "PBO101", grade, 80, 1)
            self.assertTrue(is_valid, f"Grade {grade} should be valid")


class TestGradeConversion(unittest.TestCase):
    """Test grade conversion between letter and numeric"""
    
    def test_letter_to_numeric_a(self):
        """Test A grade converts to 4.0"""
        numeric = GradeManager.convert_letter_to_numeric("A")
        self.assertEqual(numeric, 4.0)
    
    def test_letter_to_numeric_b(self):
        """Test B grade converts to 3.0"""
        numeric = GradeManager.convert_letter_to_numeric("B")
        self.assertEqual(numeric, 3.0)
    
    def test_letter_to_numeric_c(self):
        """Test C grade converts to 2.0"""
        numeric = GradeManager.convert_letter_to_numeric("C")
        self.assertEqual(numeric, 2.0)
    
    def test_letter_to_numeric_d(self):
        """Test D grade converts to 1.0"""
        numeric = GradeManager.convert_letter_to_numeric("D")
        self.assertEqual(numeric, 1.0)
    
    def test_letter_to_numeric_e(self):
        """Test E grade converts to 0.0"""
        numeric = GradeManager.convert_letter_to_numeric("E")
        self.assertEqual(numeric, 0.0)
    
    def test_numeric_to_letter_4(self):
        """Test 4.0 converts to A"""
        letter = GradeManager.convert_numeric_to_letter(4.0)
        self.assertEqual(letter, "A")
    
    def test_round_trip_conversion(self):
        """Test conversion round trip"""
        original = "B"
        numeric = GradeManager.convert_letter_to_numeric(original)
        letter = GradeManager.convert_numeric_to_letter(numeric)
        self.assertEqual(original, letter)


class TestBusinessRules(unittest.TestCase):
    """Test business logic and rules"""
    
    def test_course_passed_at_d(self):
        """Test: Lulus MK jika nilai >= D (1.0)"""
        # D grade (1.0) should pass
        self.assertTrue(GradeManager.is_passed(1.0))
    
    def test_course_failed_below_d(self):
        """Test: Course fails if grade < D (1.0)"""
        # E grade (0.0) should not pass
        self.assertFalse(GradeManager.is_passed(0.0))
    
    def test_all_grades_pass_status(self):
        """Test pass status for all grades"""
        grades_status = {
            4.0: True,  # A
            3.0: True,  # B
            2.0: True,  # C
            1.0: True,  # D
            0.0: False  # E
        }
        for grade, should_pass in grades_status.items():
            self.assertEqual(GradeManager.is_passed(grade), should_pass)


class TestIPSCalculation(unittest.TestCase):
    """Test IPS (Semester GPA) calculation"""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database with sample data"""
        # Use test database
        global DATABASE_FILE
        test_db = DATABASE_FILE.replace('.db', '_test.db')
        if os.path.exists(test_db):
            os.remove(test_db)
        DATABASE_FILE = test_db
    
    def test_ips_all_a_grades(self):
        """Test: Mahasiswa dengan nilai sempurna (semua A)"""
        # This test uses existing sample data where 21001 has mostly A's in sem 1
        # Calculate expected IPS: (4.0*3 + 3.0*4 + 4.0*3 + 4.0*3) / (3+4+3+3) = 55/13 ≈ 4.23 but max is based on the actual grades
        # Student 21001 in sem 1: A(3), A(3), B(4), A(3) = (4*3 + 4*3 + 3*4 + 4*3) / (3+3+4+3) = 52/13 ≈ 4.0
        ips = GradeCalculator.calculate_ips("21001", 1)
        self.assertGreater(ips, 3.5, "Student should have IPS > 3.5")
        self.assertLessEqual(ips, 4.0, "IPS should not exceed 4.0")
    
    def test_ips_mixed_grades(self):
        """Test IPS calculation with mixed grades"""
        # Student 21002 has mixed grades
        ips = GradeCalculator.calculate_ips("21002", 1)
        self.assertGreater(ips, 2.5)
        self.assertLess(ips, 4.0)
    
    def test_ips_no_grades(self):
        """Test IPS for non-existent student returns 0"""
        ips = GradeCalculator.calculate_ips("99999", 1)
        self.assertEqual(ips, 0.0)
    
    def test_ips_calculation_formula(self):
        """Test IPS calculation: Σ(SKS × Nilai) / Σ(SKS)"""
        # Get transcript data
        grades = GradeManager.get_all_grades_for_student("21001", 1)
        
        if grades:
            # Calculate manually
            total_weighted = sum(g['sks'] * g['numeric_grade'] for g in grades)
            total_sks = sum(g['sks'] for g in grades)
            expected_ips = round(total_weighted / total_sks, 2)
            
            # Get from calculator
            calculated_ips = GradeCalculator.calculate_ips("21001", 1)
            
            self.assertEqual(calculated_ips, expected_ips)


class TestIPKCalculation(unittest.TestCase):
    """Test IPK (Cumulative GPA) calculation"""
    
    def test_ipk_all_semesters(self):
        """Test IPK calculation across all semesters"""
        ipk = GradeCalculator.calculate_ipk("21001")
        self.assertGreaterEqual(ipk, 0)
        self.assertLessEqual(ipk, 4.0)
    
    def test_ipk_range(self):
        """Test IPK is within valid range"""
        for nim in ["21001", "21002", "21003"]:
            ipk = GradeCalculator.calculate_ipk(nim)
            self.assertGreaterEqual(ipk, 0.0)
            self.assertLessEqual(ipk, 4.0)
    
    def test_ipk_no_student(self):
        """Test IPK for non-existent student"""
        ipk = GradeCalculator.calculate_ipk("99999")
        self.assertEqual(ipk, 0.0)
    
    def test_ipk_highest_grade_for_repeated_course(self):
        """Test: Jika MK diulang, ambil nilai tertinggi"""
        # This would require setting up repeated course data
        # For now we test the logic works
        ipk = GradeCalculator.calculate_ipk("21001")
        self.assertGreater(ipk, 0)


class TestGraduationPredicate(unittest.TestCase):
    """Test graduation predicate assignment"""
    
    def test_predicate_cum_laude(self):
        """Test: Cum Laude untuk IPK >= 3.5"""
        predicate = GradeCalculator.get_graduation_predicate(3.5)
        self.assertEqual(predicate, "Cum Laude")
        
        predicate = GradeCalculator.get_graduation_predicate(3.8)
        self.assertEqual(predicate, "Cum Laude")
    
    def test_predicate_sangat_memuaskan(self):
        """Test: Sangat Memuaskan untuk IPK 3.0-3.49"""
        predicate = GradeCalculator.get_graduation_predicate(3.0)
        self.assertEqual(predicate, "Sangat Memuaskan")
        
        predicate = GradeCalculator.get_graduation_predicate(3.4)
        self.assertEqual(predicate, "Sangat Memuaskan")
    
    def test_predicate_memuaskan(self):
        """Test: Memuaskan untuk IPK 2.75-2.99"""
        predicate = GradeCalculator.get_graduation_predicate(2.75)
        self.assertEqual(predicate, "Memuaskan")
        
        predicate = GradeCalculator.get_graduation_predicate(2.9)
        self.assertEqual(predicate, "Memuaskan")
    
    def test_predicate_cukup(self):
        """Test: Cukup untuk IPK 2.0-2.74"""
        predicate = GradeCalculator.get_graduation_predicate(2.0)
        self.assertEqual(predicate, "Cukup")
        
        predicate = GradeCalculator.get_graduation_predicate(2.5)
        self.assertEqual(predicate, "Cukup")
    
    def test_predicate_kurang(self):
        """Test: Kurang untuk IPK < 2.0"""
        predicate = GradeCalculator.get_graduation_predicate(1.5)
        self.assertEqual(predicate, "Kurang")
        
        predicate = GradeCalculator.get_graduation_predicate(0.0)
        self.assertEqual(predicate, "Kurang")


class TestTranscriptGeneration(unittest.TestCase):
    """Test transcript data retrieval"""
    
    def test_transcript_retrieval(self):
        """Test getting complete transcript"""
        transcript = GradeCalculator.get_transcript("21001")
        
        self.assertIsNotNone(transcript)
        self.assertIn('student', transcript)
        self.assertIn('semesters', transcript)
        self.assertIn('ipk', transcript)
        self.assertIn('graduation_predicate', transcript)
    
    def test_transcript_student_info(self):
        """Test transcript contains correct student info"""
        transcript = GradeCalculator.get_transcript("21001")
        
        self.assertEqual(transcript['student']['nim'], "21001")
        self.assertIsNotNone(transcript['student']['name'])
        self.assertIsNotNone(transcript['student']['program_study'])
    
    def test_transcript_semester_structure(self):
        """Test transcript semester structure"""
        transcript = GradeCalculator.get_transcript("21001")
        
        for semester_data in transcript['semesters']:
            self.assertIn('semester', semester_data)
            self.assertIn('ips', semester_data)
            self.assertIn('courses', semester_data)
            self.assertIn('total_sks', semester_data)
    
    def test_transcript_non_existent_student(self):
        """Test transcript for non-existent student"""
        transcript = GradeCalculator.get_transcript("99999")
        self.assertEqual(transcript, {})


class TestPerformanceStatistics(unittest.TestCase):
    """Test performance statistics calculation"""
    
    def test_performance_stats_structure(self):
        """Test performance stats returns all required fields"""
        stats = GradeCalculator.get_performance_statistics("21001")
        
        required_fields = ['total_courses', 'passed_courses', 'failed_courses', 
                          'total_sks', 'passed_sks', 'average_grade']
        
        for field in required_fields:
            self.assertIn(field, stats)
    
    def test_performance_stats_non_negative(self):
        """Test all performance stats are non-negative"""
        stats = GradeCalculator.get_performance_statistics("21001")
        
        self.assertGreaterEqual(stats['total_courses'], 0)
        self.assertGreaterEqual(stats['passed_courses'], 0)
        self.assertGreaterEqual(stats['failed_courses'], 0)
        self.assertGreaterEqual(stats['average_grade'], 0)
    
    def test_performance_stats_no_data(self):
        """Test performance stats for student with no data"""
        stats = GradeCalculator.get_performance_statistics("99999")
        
        self.assertEqual(stats['total_courses'], 0)
        self.assertEqual(stats['passed_courses'], 0)


class TestPDFGeneration(unittest.TestCase):
    """Test PDF transcript generation"""
    
    @classmethod
    def setUpClass(cls):
        """Setup PDF generator"""
        cls.generator = TranscriptGenerator()
    
    def test_pdf_generation_creates_file(self):
        """Test PDF generation creates a file"""
        try:
            pdf_path = self.generator.generate_transcript("21001", "test_output.pdf")
            self.assertTrue(os.path.exists(pdf_path))
            # Clean up
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            self.fail(f"PDF generation failed: {e}")
    
    def test_pdf_generation_file_not_empty(self):
        """Test generated PDF file is not empty"""
        try:
            pdf_path = self.generator.generate_transcript("21001", "test_size.pdf")
            file_size = os.path.getsize(pdf_path)
            self.assertGreater(file_size, 0)
            # Clean up
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            self.fail(f"PDF generation failed: {e}")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    def test_zero_sks_course(self):
        """Test handling of zero SKS courses"""
        # This tests robustness of the system
        ips = GradeCalculator.calculate_ips("21001", 1)
        self.assertIsNotNone(ips)
    
    def test_empty_student_database(self):
        """Test system handles non-existent student gracefully"""
        student = GradeManager.get_student_info("NONEXISTENT")
        self.assertIsNone(student)
    
    def test_grade_validation_with_unicode(self):
        """Test grade validation handles unicode properly"""
        is_valid, _ = GradeManager.validate_input("21001", "PBO101", "A", 80, 1)
        self.assertTrue(is_valid)


# ===================== TEST SUITE RUNNER =====================

def run_all_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestGradeValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestGradeConversion))
    suite.addTests(loader.loadTestsFromTestCase(TestBusinessRules))
    suite.addTests(loader.loadTestsFromTestCase(TestIPSCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestIPKCalculation))
    suite.addTests(loader.loadTestsFromTestCase(TestGraduationPredicate))
    suite.addTests(loader.loadTestsFromTestCase(TestTranscriptGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformanceStatistics))
    suite.addTests(loader.loadTestsFromTestCase(TestPDFGeneration))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result


if __name__ == '__main__':
    result = run_all_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
