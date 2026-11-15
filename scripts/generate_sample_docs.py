"""
SchoolGPT - Demonstration Data Generator
Generates realistic sample school documents in PDF, DOCX, and TXT formats.
All documents are clearly marked as DEMO DATA for RSR Technologies.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors
import docx

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "demo_documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DOCS_CONTENT = {
    "student_handbook": {
        "title": "RSR International Academy - Student Handbook (DEMO DATA)",
        "category": "Student Handbook",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Teacher", "Student", "Parent"],
        "pages": [
            ("Section 1: General Code of Conduct", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
STUDENT HANDBOOK 2024-2025

1.1 School Working Hours:
Regular school hours for Grades 1 through 12 are from 8:30 AM to 3:30 PM, Monday through Friday. 
Kindergarten sessions operate from 9:00 AM to 12:45 PM.
Students must arrive at least 10 minutes prior to the morning assembly bell at 8:20 AM.

1.2 Attendance Requirements:
A minimum of 75% attendance across all academic subjects is mandatory for eligibility to sit for semester and annual examinations. 
Students failing to meet the 75% threshold without certified medical clearance will be placed on academic probation.

1.3 Uniform Policy:
Students must wear the complete formal school uniform on Mondays, Tuesdays, and Thursdays. 
Wednesday is physical education uniform day (white track pants and house sports t-shirt). 
Black formal shoes and navy blue socks are required on regular uniform days.
            """),
            ("Section 2: Campus Discipline and Facilities", """
2.1 Digital Devices and Mobile Phones:
Personal smartphones, tablets, smartwatches with cellular connectivity, and gaming devices are strictly prohibited on campus during instructional hours. 
If brought for emergency travel communication, devices must be deposited in the secure locker at the administrative desk upon entry and collected at dismissal.

2.2 Library and Laboratory Guidelines:
The Central Academic Library is open from 8:00 AM to 5:00 PM on all working days. 
Each student is eligible to borrow up to 3 books simultaneously for a duration of 14 calendar days. 
A late renewal fee of Rs. 10 per day applies to overdue books. 
Science and Computer laboratories require adherence to protective equipment guidelines; no food or beverages are permitted inside lab spaces.
            """),
            ("Section 3: Co-Curricular & Student Clubs", """
3.1 Student Houses & Clubs:
Every student is inducted into one of four school houses: Aryabhata (Blue), Ramanujan (Red), Kalam (Green), and Sarabhai (Yellow).
Active participation in at least one STEM club or Arts Society is compulsory for middle and high school students.
Club meetings take place every Friday from 2:15 PM to 3:30 PM.
            """)
        ]
    },
    "leave_policy": {
        "title": "RSR International Academy - Student Leave Policy (DEMO DATA)",
        "category": "School Policies",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Teacher", "Student", "Parent"],
        "pages": [
            ("Section 4.1: General Leave Rules", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
STUDENT LEAVE POLICY 2024-2025

4.1 Leave Entitlement and Application Procedure:
Students can avail leave for medical reasons, urgent personal circumstances, or official representation of the school in recognized competitions.
A formal written leave application or digital request through the SchoolGPT Parent Portal must be submitted by the parent or legal guardian.
Oral requests or notes written directly by students will not be entertained.

4.2 Leaves Exceeding Three Days:
Any planned leave exceeding 3 consecutive school days requires prior written sanction from the Principal at least 48 hours in advance.
Unnotified absence of more than 5 consecutive days may lead to disciplinary review and possible de-enrollment from the official attendance roster.
            """),
            ("Section 4.2: Medical Leave and Re-Admission", """
4.3 Medical Leave & Fitness Certificates:
For absences due to medical illness lasting 3 days or longer, a signed medical fitness certificate from a registered MBBS practitioner must be submitted upon resuming school.
In cases of contagious diseases (chickenpox, viral conjunctivitis, measles), students must observe the statutory isolation period before returning to class.

4.4 Examination Day Leave:
Absence during scheduled Mid-Term or Annual Examinations is strictly disallowed except under severe hospitalization. 
Re-examinations will only be sanctioned upon recommendation of the Academic Council chaired by the Principal.
            """)
        ]
    },
    "admission_policy": {
        "title": "RSR International Academy - Admission Policy & Guidelines (DEMO DATA)",
        "category": "Admission Guidelines",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Teacher", "Parent"],
        "pages": [
            ("Section 1: Admission Procedure", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
ADMISSION POLICY & PROCEDURE 2024-2025

1. Eligibility and Age Criteria:
For Nursery: Child must complete 3 years of age as of June 1st of the academic year.
For Grade 1: Child must complete 6 years of age as of June 1st of the academic year.
Admissions for Grades 1 through 9 are granted based on seat availability and evaluation through the School Readiness Assessment.

2. Online and Offline Application Process:
Prospective parents must submit the official application form either online at www.rsrtechnologies.co.in or physically at the Admissions Office.
Application registration fee is Rs. 1,000 (non-refundable).
            """),
            ("Section 2: Mandatory Documents for Admission", """
3. Mandatory Documents Required at Verification:
a) Original Birth Certificate issued by Municipal Corporation along with 2 attested copies.
b) Official Transfer Certificate (TC) from the previous recognized school, countersigned by the Education Inspector/Board for out-of-state students.
c) Previous academic year's report card showing promotion to the requested grade.
d) Six passport-sized colored photographs of the student.
e) Two passport-sized photographs of father and mother / guardian.
f) Copy of student's Aadhar Card and Parent's Address Proof (Utility bill / Passport / Driving license).
g) Blood Group report issued by a recognized diagnostic clinic.
            """)
        ]
    },
    "fee_structure": {
        "title": "RSR International Academy - Annual Fee Structure & Deadlines (DEMO DATA)",
        "category": "Fee Structure",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Parent"],
        "pages": [
            ("Section 1: Tuition and Facility Fees", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
SCHEDULE OF FEES & PAYMENT POLICIES 2024-2025

1. Grade-wise Annual Tuition Fees:
- Pre-Primary (Nursery, LKG, UKG): Rs. 65,000 per annum
- Primary (Grades 1 to 5): Rs. 85,000 per annum
- Middle School (Grades 6 to 8): Rs. 98,000 per annum
- Secondary (Grades 9 & 10): Rs. 1,15,000 per annum
- Senior Secondary (Grades 11 & 12 Science / Commerce): Rs. 1,35,000 per annum

2. One-Time Charges (Applicable for new admissions only):
- Registration Fee: Rs. 1,000
- Admission Fee: Rs. 25,000
- Refundable Caution Deposit: Rs. 10,000 (Refundable upon withdrawal after clearing dues)
            """),
            ("Section 2: Payment Deadlines and Late Surcharges", """
3. Installment Deadlines:
Fees can be paid in 3 equal term installments:
- Term 1 Installment: Payable on or before June 10, 2024
- Term 2 Installment: Payable on or before October 10, 2024
- Term 3 Installment: Payable on or before January 10, 2025

4. Late Payment Surcharge Policy:
Payments made after the 10th of the installment month will incur a late fine of Rs. 100 per day up to the 25th of the month.
If fees remain unpaid after the 25th, an administrative notice will be issued and student portal access may be restricted.

5. Payment Methods:
Online net banking, UPI, Credit/Debit cards via the School Payment Portal, or Demand Draft drawn in favor of 'RSR International Academy'.
Cash transactions exceeding Rs. 5,000 are not accepted at the accounts counter.
            """)
        ]
    },
    "examination_schedule": {
        "title": "RSR International Academy - Academic Examination Calendar (DEMO DATA)",
        "category": "Examination Timetable",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Teacher", "Student", "Parent"],
        "pages": [
            ("Section 1: Examination Calendar", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
EXAMINATION SCHEDULE & ASSESSMENT CALENDAR 2024-2025

1. Formative and Summative Assessment Schedule:
- Periodic Assessment 1 (PA-1): July 22 to July 29, 2024
- Mid-Term Examinations (Term 1): September 18 to September 30, 2024
- Periodic Assessment 2 (PA-2): November 18 to November 25, 2024
- Pre-Board Examinations (Grades 10 & 12): January 6 to January 18, 2025
- Annual Final Examinations: March 3 to March 17, 2025

2. Timings During Exam Days:
Reporting time: 8:30 AM
Reading time: 9:00 AM to 9:15 AM
Writing duration: 9:15 AM to 12:15 PM
Dispersal for all students on exam days is at 12:45 PM.
            """),
            ("Section 2: Examination Rules & Grading System", """
3. Examination Hall Rules:
Students must be seated in their assigned exam hall 15 minutes before reading time.
Only transparent stationery pouches and clear water bottles are permitted.
Possession of unauthorized notes, electronic calculators, or mobile devices constitutes malpractice resulting in immediate paper cancellation.

4. Grading Scale (CBSE Aligned):
91% - 100%: Grade A1
81% - 90%: Grade A2
71% - 80%: Grade B1
61% - 70%: Grade B2
51% - 60%: Grade C1
41% - 50%: Grade C2
33% - 40%: Grade D (Passing benchmark)
Below 33%: Grade E (Needs remedial improvement / re-test required)
            """)
        ]
    },
    "transport_policy": {
        "title": "RSR International Academy - Transportation & Bus Safety Rules (DEMO DATA)",
        "category": "Transport Policies",
        "academic_year": "2024-2025",
        "allowed_roles": ["Super Admin", "School Administrator", "Principal", "Teacher", "Student", "Parent"],
        "pages": [
            ("Section 1: Bus Routes & Safety Regulations", """
=== DEMO DATA - RSR INTERNATIONAL ACADEMY ===
SCHOOL TRANSPORTATION POLICY 2024-2025

1. Bus Service Overview:
RSR International Academy operates a fleet of 24 GPS-enabled air-conditioned school buses covering major routes across the metropolitan region.
Each bus is equipped with dual CCTV surveillance cameras, first-aid kits, fire extinguishers, and a certified female attendant.

2. Student Conduct & Safety Rules:
Students must board and alight only at designated bus stops. 
Students must remain seated with seatbelts fastened while the bus is in motion. 
Extending heads or arms out of windows, shouting, or unruly behavior is strictly prohibited.
Eating or drinking (except water) is disallowed on school buses to maintain hygiene.
            """),
            ("Section 2: Bus Tracking & Parent Guidelines", """
3. Real-Time Tracking & Delay Protocols:
Parents can track their child's bus location in real-time using the SchoolGPT mobile application.
Buses will wait for a maximum of 2 minutes at any stop before proceeding. Parents must ensure children arrive at the stop 5 minutes prior to scheduled pickup.
In case of breakdown or adverse traffic delays exceeding 15 minutes, parents will receive automatic SMS updates from the Transport Coordinator.

4. Route Changes and Cancellation:
Temporary change of bus stop requires written notice to the Transport Desk 24 hours prior. 
Transport fee is charged on a quarterly basis and is non-refundable once the term commences.
            """)
        ]
    }
}

def generate_pdf(doc_key: str, data: dict, output_path: Path):
    """Generates PDF using ReportLab with clean pages."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=14
    )
    section_style = ParagraphStyle(
        'SecTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1D4ED8'),
        spaceAfter=8,
        spaceBefore=12
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )

    story = []
    story.append(Paragraph(data["title"], title_style))
    story.append(Paragraph(f"Category: {data['category']} | Academic Year: {data['academic_year']} | Official RSR Technologies Demo", body_style))
    story.append(Spacer(1, 15))

    for idx, (section_title, section_text) in enumerate(data["pages"]):
        if idx > 0:
            story.append(PageBreak())
        story.append(Paragraph(section_title, section_style))
        for line in section_text.strip().split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, body_style))
        story.append(Spacer(1, 10))

    doc.build(story)

def generate_docx(doc_key: str, data: dict, output_path: Path):
    """Generates DOCX with headings and paragraphs."""
    doc = docx.Document()
    doc.add_heading(data["title"], level=0)
    doc.add_paragraph(f"Category: {data['category']} | Academic Year: {data['academic_year']}")

    for section_title, section_text in data["pages"]:
        doc.add_heading(section_title, level=1)
        for line in section_text.strip().split("\n"):
            line = line.strip()
            if line:
                doc.add_paragraph(line)

    doc.save(str(output_path))

def generate_txt(doc_key: str, data: dict, output_path: Path):
    """Generates plain TXT with explicit page indicators."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"{data['title']}\n")
        f.write(f"Category: {data['category']} | Year: {data['academic_year']}\n\n")
        for idx, (section_title, section_text) in enumerate(data["pages"], 1):
            f.write(f"=== Page {idx}: {section_title} ===\n\n")
            f.write(section_text.strip() + "\n\n")

def main():
    print("Generating official demonstration school documents...")
    # Generate mix of PDF, DOCX, TXT formats
    # 1. Student Handbook (PDF)
    generate_pdf("student_handbook", DOCS_CONTENT["student_handbook"], OUTPUT_DIR / "Student_Handbook.pdf")
    # 2. Leave Policy (PDF)
    generate_pdf("leave_policy", DOCS_CONTENT["leave_policy"], OUTPUT_DIR / "Student_Leave_Policy.pdf")
    # 3. Admission Policy (DOCX)
    generate_docx("admission_policy", DOCS_CONTENT["admission_policy"], OUTPUT_DIR / "Admission_Policy.docx")
    # 4. Fee Structure (PDF)
    generate_pdf("fee_structure", DOCS_CONTENT["fee_structure"], OUTPUT_DIR / "School_Fee_Structure.pdf")
    # 5. Examination Schedule (TXT)
    generate_txt("examination_schedule", DOCS_CONTENT["examination_schedule"], OUTPUT_DIR / "Examination_Schedule.txt")
    # 6. Transport Policy (PDF)
    generate_pdf("transport_policy", DOCS_CONTENT["transport_policy"], OUTPUT_DIR / "School_Transport_Policy.pdf")

    print(f"Generated 6 high-quality demonstration documents in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
