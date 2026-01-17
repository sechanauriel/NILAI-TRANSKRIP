"""
PDF Transcript Generator - Generate professional academic transcripts
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from grade_calculator import GradeCalculator
from grade_manager import GradeManager
import os

class TranscriptGenerator:
    """Generate professional PDF transcripts"""
    
    def __init__(self, output_dir="transcripts"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def generate_transcript(self, nim: str, filename: str = None) -> str:
        """
        Generate a complete transcript PDF for a student
        
        Args:
            nim: Student ID
            filename: Output filename (optional)
            
        Returns:
            str: Path to generated PDF
        """
        
        # Get transcript data
        transcript = GradeCalculator.get_transcript(nim)
        
        if not transcript:
            raise ValueError(f"No data found for student {nim}")
        
        student = transcript['student']
        if filename is None:
            filename = f"Transcript_{student['nim']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)
        
        story = []
        styles = self._get_styles()
        
        # Header
        story.extend(self._create_header())
        story.append(Spacer(1, 0.3*inch))
        
        # Title
        title = Paragraph("TRANSKRIP AKADEMIK", styles['title'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Student Info
        story.extend(self._create_student_info(student, styles))
        story.append(Spacer(1, 0.2*inch))
        
        # Grades by Semester
        for semester_data in transcript['semesters']:
            story.extend(self._create_semester_table(semester_data, styles))
            story.append(Spacer(1, 0.15*inch))
        
        # Summary
        story.extend(self._create_summary(transcript, styles))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer with signature
        story.extend(self._create_footer(student, styles))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def _get_styles(self) -> dict:
        """Get custom paragraph styles"""
        
        styles = getSampleStyleSheet()
        
        custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=12,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ),
            'heading2': ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.HexColor('#333333'),
                spaceAfter=10,
                fontName='Helvetica-Bold',
                borderBottomColor=colors.HexColor('#cccccc'),
                borderBottomWidth=1
            ),
            'normal': ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=8
            ),
            'small': ParagraphStyle(
                'CustomSmall',
                parent=styles['Normal'],
                fontSize=9,
                spaceAfter=6
            )
        }
        
        return custom_styles
    
    def _create_header(self) -> list:
        """Create document header with university name"""
        
        elements = []
        styles = self._get_styles()
        
        # University header
        header = Paragraph(
            "<b>UNIVERSITAS XYZ</b><br/><b>LAPORAN NILAI AKADEMIK</b>",
            styles['heading2']
        )
        elements.append(header)
        
        return elements
    
    def _create_student_info(self, student: dict, styles: dict) -> list:
        """Create student information section"""
        
        elements = []
        
        # Create info table
        info_data = [
            ['NIM', ':', f"<b>{student['nim']}</b>"],
            ['Nama Lengkap', ':', f"<b>{student['name']}</b>"],
            ['Program Studi', ':', student['program_study']],
            ['Tahun Angkatan', ':', str(student['batch_year'])]
        ]
        
        info_table = Table(info_data, colWidths=[1.5*inch, 0.2*inch, 3.5*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        elements.append(info_table)
        
        return elements
    
    def _create_semester_table(self, semester_data: dict, styles: dict) -> list:
        """Create grade table for a semester"""
        
        elements = []
        
        # Semester header
        sem_header = Paragraph(
            f"<b>SEMESTER {semester_data['semester']} - IPS: {semester_data['ips']}</b>",
            styles['heading2']
        )
        elements.append(sem_header)
        elements.append(Spacer(1, 0.1*inch))
        
        # Create grade table
        table_data = [
            ['Kode MK', 'Nama Mata Kuliah', 'SKS', 'Nilai', 'Mutu', 'Keterangan']
        ]
        
        for course in semester_data['courses']:
            keterangan = 'LULUS' if course['numeric_grade'] >= 1.0 else 'TIDAK LULUS'
            table_data.append([
                course['course_code'],
                course['course_name'],
                str(course['sks']),
                course['letter_grade'],
                f"{course['numeric_grade']:.2f}",
                keterangan
            ])
        
        # Add total row
        total_sks = semester_data['total_sks']
        table_data.append([
            '', '<b>JUMLAH</b>', f'<b>{total_sks}</b>', '', '', ''
        ])
        
        grade_table = Table(table_data, colWidths=[0.9*inch, 2.8*inch, 0.6*inch, 0.7*inch, 0.6*inch, 1.0*inch])
        
        grade_table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            
            # Data rows
            ('ALIGN', (0, 1), (-1, -2), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -2), 'CENTER'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.beige, colors.white]),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E7E6E6')),
            ('ALIGN', (0, -1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, -1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 6),
        ]))
        
        elements.append(grade_table)
        
        return elements
    
    def _create_summary(self, transcript: dict, styles: dict) -> list:
        """Create academic summary section"""
        
        elements = []
        
        summary_header = Paragraph("<b>RINGKASAN AKADEMIK</b>", styles['heading2'])
        elements.append(summary_header)
        elements.append(Spacer(1, 0.1*inch))
        
        # Summary data
        summary_data = [
            ['Total SKS', ':', f"<b>{transcript['total_sks']}</b> SKS"],
            ['IPK (Indeks Prestasi Kumulatif)', ':', f"<b>{transcript['ipk']:.2f}</b>"],
            ['Predikat Kelulusan', ':', f"<b>{transcript['graduation_predicate']}</b>"],
            ['Jumlah Semester', ':', str(transcript['number_of_semesters'])]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 0.2*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_footer(self, student: dict, styles: dict) -> list:
        """Create footer with signature line"""
        
        elements = []
        
        # Generated date
        date_text = Paragraph(
            f"<i>Dicetak pada: {datetime.now().strftime('%d %B %Y - %H:%M:%S')}</i>",
            styles['small']
        )
        elements.append(date_text)
        elements.append(Spacer(1, 0.15*inch))
        
        # Signature section
        sig_data = [
            ['Mengetahui,', '', 'Mahasiswa,'],
            ['Dekan Fakultas', '', f"{student['name']}"],
            ['', '', f"({student['nim']})"],
            ['', '', ''],
            ['_____________________', '', '_____________________'],
            ['Tanggal: ___________', '', 'Tanggal: ___________']
        ]
        
        sig_table = Table(sig_data, colWidths=[2*inch, 1*inch, 2*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(sig_table)
        
        return elements


if __name__ == "__main__":
    # Test PDF generation
    print("Testing Transcript Generator...")
    
    generator = TranscriptGenerator()
    
    try:
        pdf_path = generator.generate_transcript("21001", "test_transcript.pdf")
        print(f"Transcript generated successfully: {pdf_path}")
    except Exception as e:
        print(f"Error generating transcript: {e}")
