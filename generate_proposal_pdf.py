import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#555555"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "BUBT Dept. of CSE | Project Proposal: SDERMS")
            self.setStrokeColor(colors.HexColor("#CCCCCC"))
            self.setLineWidth(0.5)
            self.line(54, 748, 558, 748)
            
        # Footer
        page_text = f"Page | {self._pageNumber} of {page_count}"
        self.drawRightString(558, 35, page_text)
        self.drawString(54, 35, "Confidential - SDP-200 Project Proposal")
        self.setStrokeColor(colors.HexColor("#CCCCCC"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()


def create_proposal_pdf(output_filename="BUBT_Project_Proposal_SDERMS.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    primary_color = colors.HexColor("#1A365D")   # Deep navy
    secondary_color = colors.HexColor("#2B6CB0") # Slate blue
    dark_neutral = colors.HexColor("#2D3748")
    
    univ_style = ParagraphStyle(
        'UnivHeader',
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f2942"),
        alignment=0
    )
    
    univ_sub = ParagraphStyle(
        'UnivSubHeader',
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4A5568")
    )
    
    doc_title_style = ParagraphStyle(
        'DocTitle',
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1A202C"),
        alignment=0,
        spaceAfter=10
    )
    
    section_heading = ParagraphStyle(
        'SecHeading',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    sub_heading = ParagraphStyle(
        'SubHeading',
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=dark_neutral,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=dark_neutral,
        leftIndent=12,
        spaceAfter=3
    )

    tbl_header_style = ParagraphStyle(
        'TblHdr',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    tbl_cell_style = ParagraphStyle(
        'TblCell',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral
    )

    tbl_cell_center = ParagraphStyle(
        'TblCellCenter',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral,
        alignment=1
    )

    tbl_cell_bold = ParagraphStyle(
        'TblCellBold',
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral
    )

    story = []

    # ================= TOP HEADER BANNER =================
    header_data = [
        [
            Paragraph("<b>Bangladesh University of Business and Technology (BUBT)</b><br/><font color='#4A5568' size='9'>Department of Computer Science and Engineering (CSE)<br/>Course: SDP-200 (Software Development Project)</font>", univ_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[504])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('LEFTPADDING', (0,0), (-1,-1), 14),
        ('RIGHTPADDING', (0,0), (-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINELEFT', (0,0), (0,-1), 4, primary_color),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # ================= TITLE =================
    story.append(Paragraph("PROJECT PROPOSAL", doc_title_style))
    story.append(Paragraph("<b>On</b><br/><b>[Project Name: Smart Disaster & Emergency Resource Management System (SDERMS)]</b><br/><b>[Submission Date: October 7, 2026]</b>", body_style))
    story.append(Spacer(1, 8))

    # ================= SUBMITTED BY TABLE =================
    story.append(Paragraph("<b>Submitted By:</b>", sub_heading))
    members = [
        ("20255203047", "Md Maruf Hossain", "48 / 2", "Team Leader"),
        ("20255203050", "Masud Rana", "48 / 2", "Co-Leader"),
        ("20255203052", "MD. MAHABUR RAHMAN MUHIN", "48 / 2", "Member"),
        ("20255203055", "Sumaiya Afroz", "48 / 2", "Member"),
        ("20255203057", "Urmi Akther", "48 / 2", "Member"),
        ("20255203125", "Nazmus sakib junayed", "48 / 2", "Member")
    ]
    
    sub_by_data = [[
        Paragraph("<b>ID</b>", tbl_header_style),
        Paragraph("<b>Name</b>", tbl_header_style),
        Paragraph("<b>Intake / Section</b>", tbl_header_style),
        Paragraph("<b>Role</b>", tbl_header_style)
    ]]
    for s_id, name, intake_sec, role in members:
        sub_by_data.append([
            Paragraph(s_id, tbl_cell_center),
            Paragraph(f"<b>{name}</b>", tbl_cell_style),
            Paragraph(intake_sec, tbl_cell_center),
            Paragraph(role, tbl_cell_center)
        ])
    
    sub_table = Table(sub_by_data, colWidths=[90, 184, 110, 120])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sub_table)
    story.append(Spacer(1, 8))

    # ================= SUBMITTED TO =================
    sub_to_data = [
        [
            Paragraph("<b>Submitted To:</b><br/><b>Ashfia Jannat Keya</b><br/><i>Lecturer, Dept. of CSE, BUBT</i>", body_style)
        ]
    ]
    sub_to_table = Table(sub_to_data, colWidths=[504])
    sub_to_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F7FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(sub_to_table)
    story.append(Spacer(1, 10))

    # ================= 1. NEEDS / PROBLEMS =================
    story.append(Paragraph("1. Needs / Problems", section_heading))
    story.append(Paragraph("In Bangladesh, sudden environmental and urban emergencies (flash floods, cyclones, building fires, earthquakes) create chaotic post-disaster scenarios. Rescue coordinators and humanitarian volunteers face critical systemic bottlenecks:", body_style))
    story.append(Paragraph("• <b>Manual & Uncoordinated Incident Logging:</b> Emergency calls are gathered via fragmented logs and paperwork, leading to lost incidents and delayed rescue response times.", bullet_style))
    story.append(Paragraph("• <b>Absence of Algorithmic Risk Triage:</b> Responders lack an objective metric to rank incoming crises by mathematical risk severity, casualty count, and vulnerable population.", bullet_style))
    story.append(Paragraph("• <b>Imbalanced Shelter Utilization:</b> Displaced victims rush to familiar nearby centers without capacity intelligence, resulting in severe overcrowding at certain shelters while others remain vacant.", bullet_style))
    story.append(Paragraph("• <b>Disproportionate Relief Allocation:</b> Essential supplies (food, water purification, medicines) are distributed without population-proportional mathematical models.", bullet_style))
    story.append(Paragraph("• <b>Hazard-Blind Evacuation Routing:</b> Flooded or blocked roadways render conventional maps inaccurate without real-time road obstruction bypass routing.", bullet_style))

    # ================= 2. GOALS / OBJECTIVES =================
    story.append(Paragraph("2. Goals / Objectives", section_heading))
    story.append(Paragraph("The primary goal of <b>SDERMS</b> is to build a robust, responsive desktop decision-support system to coordinate incident reporting, triage prioritization, shelter recommendation, relief quota calculation, and shortest safe routing.", body_style))
    story.append(Paragraph("<b>Specific Objectives:</b>", sub_heading))
    story.append(Paragraph("• <b>Centralized Disaster Tracking:</b> Fast CRUD operations for incident status, category, severity rating, and resolution toggling.", bullet_style))
    story.append(Paragraph("• <b>Automated Risk Scoring Engine:</b> Compute dynamic risk scores (0–100) using multi-factor weights to maintain a live priority queue.", bullet_style))
    story.append(Paragraph("• <b>Optimal Shelter Recommendation:</b> Algorithmic Best-Fit capacity matching to redirect displaced victims efficiently.", bullet_style))
    story.append(Paragraph("• <b>Fair Relief Distribution:</b> Compute mathematical population-proportional quotas across relief camps from central inventory.", bullet_style))
    story.append(Paragraph("• <b>Dijkstra Safe Route Pathfinder:</b> Visual shortest path calculation with live interactive road obstacle/blockade simulation.", bullet_style))
    story.append(Paragraph("• <b>Squad & Volunteer Coordination:</b> Real-time rescue squad status tracking and volunteer skill registry.", bullet_style))
    story.append(Paragraph("• <b>Audit Reporting:</b> Instant CSV export for post-disaster evaluations and administrative logs.", bullet_style))

    # ================= 3. EXISTING SYSTEM ANALYSIS =================
    story.append(Paragraph("3. Existing System Analysis", section_heading))
    story.append(Paragraph("An evaluation of existing software solutions was conducted to identify limitations and define the project's unique contributions:", body_style))

    exist_data = [
        [
            Paragraph("<b>Existing System</b>", tbl_header_style),
            Paragraph("<b>Key Strengths</b>", tbl_header_style),
            Paragraph("<b>Identified Shortcomings & Gaps</b>", tbl_header_style)
        ],
        [
            Paragraph("<b>1. Sahana Eden</b><br/>(Open Source DM)", tbl_cell_bold),
            Paragraph("Comprehensive web framework, GIS support, multi-agency deployment.", tbl_cell_style),
            Paragraph("Heavy enterprise stack, complex hosting, lacks instant local offline triage scoring for decentralized field hubs.", tbl_cell_style)
        ],
        [
            Paragraph("<b>2. FEMA App / Portal</b><br/>(USA Federal)", tbl_cell_bold),
            Paragraph("Official alerts, reliable meteorological integration, citizen awareness.", tbl_cell_style),
            Paragraph("Strictly US-centric; functions as a public broadcast channel rather than a tactical operational tool for shelter & road graph triage.", tbl_cell_style)
        ],
        [
            Paragraph("<b>3. DesInventar</b><br/>(UNDRR Disaster DB)", tbl_cell_bold),
            Paragraph("Excellent historical disaster loss records and global damage statistics.", tbl_cell_style),
            Paragraph("Exclusively retrospective; contains zero real-time operational modules (no live shelter matching, no Dijkstra routing).", tbl_cell_style)
        ]
    ]
    exist_table = Table(exist_data, colWidths=[120, 184, 200])
    exist_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(exist_table)

    # ================= 4. FEATURES / SCOPES =================
    story.append(Paragraph("4. Features / Scopes", section_heading))
    story.append(Paragraph("To ensure full execution within academic deadlines, the project scope strictly covers feasible and functional modules:", body_style))
    story.append(Paragraph("• <b>Executive Dashboard:</b> Real-time metric cards (Active Disasters, Casualties, Critical Queue, Shelter Capacity, Squad Readiness).", bullet_style))
    story.append(Paragraph("• <b>Disaster Management:</b> Incident registration, severity rating (1–5), location, and Active/Resolved status toggles.", bullet_style))
    story.append(Paragraph("• <b>Dynamic Risk Scoring Engine:</b> Automated risk score calculation: <i>Score = (0.40 × Severity × 20) + (0.35 × min(100, Casualties × 2)) + (0.25 × Urgency Weight)</i>.", bullet_style))
    story.append(Paragraph("• <b>Shelter Best-Fit Recommender:</b> Capacity tracking, visual occupancy progress bars, and optimal shelter matching.", bullet_style))
    story.append(Paragraph("• <b>Relief Inventory & Distribution:</b> Stock tracking, critical low-stock threshold alerts, and population-proportional quota calculation.", bullet_style))
    story.append(Paragraph("• <b>Rescue Squads & Volunteer Registry:</b> Squad dispatch tracking (Standby, Dispatched, Active) and volunteer skill categorizer.", bullet_style))
    story.append(Paragraph("• <b>Dijkstra Safe Route Navigator:</b> Graph-based shortest path routefinder with toggleable road blockades.", bullet_style))
    story.append(Paragraph("• <b>Audit Reports & Modern UI:</b> One-click CSV export and responsive Dark/Light mode theme powered by CustomTkinter.", bullet_style))

    # ================= 5. DEVELOPMENT MODEL =================
    story.append(Paragraph("5. Development Model", section_heading))
    story.append(Paragraph("The <b>Agile Iterative Development Model</b> is chosen for this project.", body_style))
    story.append(Paragraph("<b>Why Agile Iterative Model?</b>", sub_heading))
    story.append(Paragraph("1. <b>Modular Sprints:</b> Allows iterative construction of database models, core algorithms (Dijkstra, Risk Scoring), and UI views in structured sprints.", bullet_style))
    story.append(Paragraph("2. <b>Early Algorithm Verification:</b> Mathematical allocation models and graph routing can be isolated and verified before GUI integration.", bullet_style))
    story.append(Paragraph("3. <b>Continuous Feedback & Adaptability:</b> Enables rapid integration of supervisor feedback without architectural disruption.", bullet_style))
    story.append(Paragraph("4. <b>Risk Mitigation:</b> Guarantees functional software at every milestone rather than a high-risk end-of-semester integration.", bullet_style))

    # ================= 6. FEASIBILITY ANALYSIS & POSSIBLE RISKS =================
    story.append(Paragraph("6. Feasibility Analysis & Possible Risks", section_heading))
    story.append(Paragraph("<b>3-Factor Feasibility Analysis:</b>", sub_heading))
    story.append(Paragraph("• <b>Technical Feasibility:</b> Built on Python 3.10+, SQLite3, and CustomTkinter. Runs natively on standard consumer PCs (≥4 GB RAM) without external server dependencies. <i>(Status: Highly Feasible)</i>", bullet_style))
    story.append(Paragraph("• <b>Operational Feasibility:</b> The clean visual UI requires minimal training; operators can log incidents, view triage queues, and check routes in seconds. <i>(Status: Highly Feasible)</i>", bullet_style))
    story.append(Paragraph("• <b>Economic Feasibility:</b> Utilizes 100% Free and Open-Source Software (FOSS). Total software license cost is 0.00 BDT. <i>(Status: Highly Feasible)</i>", bullet_style))

    story.append(Paragraph("<b>Risk Matrix & Mitigation:</b>", sub_heading))
    risk_data = [
        [
            Paragraph("<b>Identified Risk</b>", tbl_header_style),
            Paragraph("<b>Severity</b>", tbl_header_style),
            Paragraph("<b>Mitigation Strategy</b>", tbl_header_style)
        ],
        [
            Paragraph("Graph Route Calculation Lag", tbl_cell_bold),
            Paragraph("Medium", tbl_cell_center),
            Paragraph("Use optimized adjacency list data structure with min-heap priority queue.", tbl_cell_style)
        ],
        [
            Paragraph("Database Concurrency & Locking", tbl_cell_bold),
            Paragraph("Low", tbl_cell_center),
            Paragraph("Enable SQLite WAL (Write-Ahead Logging) mode and structured connection lifecycles.", tbl_cell_style)
        ],
        [
            Paragraph("UI Freeze during Batch Operations", tbl_cell_bold),
            Paragraph("Medium", tbl_cell_center),
            Paragraph("Modular event binding and efficient CustomTkinter widget updates.", tbl_cell_style)
        ]
    ]
    risk_table = Table(risk_data, colWidths=[140, 80, 284])
    risk_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(risk_table)

    # ================= 8. REQUIREMENTS =================
    story.append(Paragraph("8. Requirements", section_heading))
    story.append(Paragraph("• <b>Hardware:</b> Dual-core CPU (Intel i3 / AMD Ryzen 3 or higher), 4 GB RAM (8 GB recommended), 500 MB storage.", bullet_style))
    story.append(Paragraph("• <b>Operating System:</b> Windows 10/11, Linux, or macOS.", bullet_style))
    story.append(Paragraph("• <b>Software & Tools:</b> Python 3.10+, SQLite 3, CustomTkinter, Git / GitHub, Visual Studio Code.", bullet_style))
    story.append(Paragraph("• <b>Personnel:</b> 6 CSE undergraduate team members with clear task assignments.", bullet_style))

    # ================= 9. ACTIVITY AND TIME SCHEDULE =================
    story.append(Paragraph("9. Activity and Time Schedule (Project Breakdown)", section_heading))
    
    sched_data = [
        [
            Paragraph("<b>#</b>", tbl_header_style),
            Paragraph("<b>Stages / Tasks</b>", tbl_header_style),
            Paragraph("<b>Efforts, Man-Hours</b>", tbl_header_style)
        ],
        [Paragraph("<b>Stage 1</b>", tbl_cell_bold), Paragraph("<b>Analysis and Design</b>", tbl_cell_bold), Paragraph("<b>24</b>", tbl_cell_center)],
        [Paragraph("1.1", tbl_cell_center), Paragraph("Requirements analysis, SRS documentation, UI wireframing", tbl_cell_style), Paragraph("14", tbl_cell_center)],
        [Paragraph("1.2", tbl_cell_center), Paragraph("Database ERD design & Work breakdown structure", tbl_cell_style), Paragraph("10", tbl_cell_center)],
        
        [Paragraph("<b>Stage 2</b>", tbl_cell_bold), Paragraph("<b>Implementation</b>", tbl_cell_bold), Paragraph("<b>160</b>", tbl_cell_center)],
        [Paragraph("2.1", tbl_cell_center), Paragraph("Database schema creation & SQLite connector module", tbl_cell_style), Paragraph("16", tbl_cell_center)],
        [Paragraph("2.2", tbl_cell_center), Paragraph("Role-based authentication & admin session management", tbl_cell_style), Paragraph("12", tbl_cell_center)],
        [Paragraph("2.3", tbl_cell_center), Paragraph("Disaster incident registry & dynamic risk scoring engine", tbl_cell_style), Paragraph("24", tbl_cell_center)],
        [Paragraph("2.4", tbl_cell_center), Paragraph("Shelter capacity management & Best-Fit recommender algorithm", tbl_cell_style), Paragraph("20", tbl_cell_center)],
        [Paragraph("2.5", tbl_cell_center), Paragraph("Relief supply tracking & population-proportional allocation", tbl_cell_style), Paragraph("18", tbl_cell_center)],
        [Paragraph("2.6", tbl_cell_center), Paragraph("Rescue squad tracking & civilian volunteer skill pool registry", tbl_cell_style), Paragraph("16", tbl_cell_center)],
        [Paragraph("2.7", tbl_cell_center), Paragraph("Road network graph & Dijkstra shortest path navigation engine", tbl_cell_style), Paragraph("24", tbl_cell_center)],
        [Paragraph("2.8", tbl_cell_center), Paragraph("CustomTkinter GUI views, Executive Dashboard & Dark/Light mode", tbl_cell_style), Paragraph("30", tbl_cell_center)],

        [Paragraph("<b>Stage 3</b>", tbl_cell_bold), Paragraph("<b>Testing and Quality Assurance (QA)</b>", tbl_cell_bold), Paragraph("<b>30</b>", tbl_cell_center)],
        [Paragraph("3.1", tbl_cell_center), Paragraph("Unit testing, algorithm boundary validation, bug fixing", tbl_cell_style), Paragraph("30", tbl_cell_center)],

        [Paragraph("<b>Stage 4</b>", tbl_cell_bold), Paragraph("<b>Deployment & Final Documentation</b>", tbl_cell_bold), Paragraph("<b>16</b>", tbl_cell_center)],
        [Paragraph("4.1", tbl_cell_center), Paragraph("Standalone executable packaging, user manual & final presentation", tbl_cell_style), Paragraph("16", tbl_cell_center)],

        [Paragraph("<b>TOTAL</b>", tbl_cell_bold), Paragraph("<b>Total Estimated Project Efforts</b>", tbl_cell_bold), Paragraph("<b>230 Man-Hours</b>", tbl_cell_bold)]
    ]
    sched_table = Table(sched_data, colWidths=[40, 364, 100])
    sched_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,4), (-1,4), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,13), (-1,13), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,15), (-1,15), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0,17), (-1,17), colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(sched_table)

    # ================= 10. BUDGET =================
    story.append(Paragraph("10. Budget", section_heading))
    story.append(Paragraph("The tentative academic project budget includes hardware, open-source software licenses, lab infrastructure, and documentation:", body_style))

    budget_data = [
        [
            Paragraph("<b>Project Item</b>", tbl_header_style),
            Paragraph("<b>Amount / Qty</b>", tbl_header_style),
            Paragraph("<b>Unit Price (BDT)</b>", tbl_header_style),
            Paragraph("<b>Total (BDT)</b>", tbl_header_style)
        ],
        [Paragraph("Software License (Python, SQLite, VS Code)", tbl_cell_style), Paragraph("FOSS", tbl_cell_center), Paragraph("0.00", tbl_cell_center), Paragraph("0.00", tbl_cell_center)],
        [Paragraph("Development Machine(s)", tbl_cell_style), Paragraph("6 PCs (Lab/Personal)", tbl_cell_center), Paragraph("0.00", tbl_cell_center), Paragraph("0.00", tbl_cell_center)],
        [Paragraph("Server / Database License", tbl_cell_style), Paragraph("Embedded SQLite", tbl_cell_center), Paragraph("0.00", tbl_cell_center), Paragraph("0.00", tbl_cell_center)],
        [Paragraph("Development Labor (230 Man-Hours)", tbl_cell_style), Paragraph("6 Students", tbl_cell_center), Paragraph("Academic", tbl_cell_center), Paragraph("0.00", tbl_cell_center)],
        [Paragraph("Project Management & Consultation", tbl_cell_style), Paragraph("Faculty Guidance", tbl_cell_center), Paragraph("Academic", tbl_cell_center), Paragraph("0.00", tbl_cell_center)],
        [Paragraph("Documentation, Report Binding & Presentation", tbl_cell_style), Paragraph("3 Sets", tbl_cell_center), Paragraph("500.00", tbl_cell_center), Paragraph("1,500.00", tbl_cell_center)],
        [Paragraph("Contingency / Miscellaneous Expenses", tbl_cell_style), Paragraph("Buffer", tbl_cell_center), Paragraph("1,000.00", tbl_cell_center), Paragraph("1,000.00", tbl_cell_center)],
        [Paragraph("<b>Grand Total Estimated Budget</b>", tbl_cell_bold), Paragraph("-", tbl_cell_center), Paragraph("-", tbl_cell_center), Paragraph("<b>2,500.00 BDT</b>", tbl_cell_bold)]
    ]
    budget_table = Table(budget_data, colWidths=[204, 110, 100, 90])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#F7FAFC")]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#EDF2F7")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(budget_table)

    # ================= 11. DEVELOPMENT TEAM & STAKEHOLDERS =================
    story.append(Paragraph("11. Development Team & Stakeholders", section_heading))
    story.append(Paragraph("The development team consists of 6 members with balanced task allocations (maximum 2 people per task) ensuring fair distribution:", body_style))

    team_data = [
        [
            Paragraph("<b>ID</b>", tbl_header_style),
            Paragraph("<b>Name</b>", tbl_header_style),
            Paragraph("<b>Designation</b>", tbl_header_style),
            Paragraph("<b>Responsibilities</b>", tbl_header_style)
        ],
        [
            Paragraph("20255203047", tbl_cell_center),
            Paragraph("<b>Md Maruf Hossain</b>", tbl_cell_style),
            Paragraph("Team Leader & Backend Developer", tbl_cell_style),
            Paragraph("Project planning, architecture design, Risk Scoring engine, and Dijkstra pathfinding algorithm.", tbl_cell_style)
        ],
        [
            Paragraph("20255203050", tbl_cell_center),
            Paragraph("<b>Masud Rana</b>", tbl_cell_style),
            Paragraph("Co-Leader & UI/UX Developer", tbl_cell_style),
            Paragraph("CustomTkinter GUI layout, Dashboard analytics widgets, and Dark/Light theme management.", tbl_cell_style)
        ],
        [
            Paragraph("20255203052", tbl_cell_center),
            Paragraph("<b>MD. MAHABUR RAHMAN MUHIN</b>", tbl_cell_style),
            Paragraph("Database Administrator (DBA)", tbl_cell_style),
            Paragraph("SQLite schema design, SQL CRUD operations, database connector, and CSV audit exporter.", tbl_cell_style)
        ],
        [
            Paragraph("20255203055", tbl_cell_center),
            Paragraph("<b>Sumaiya Afroz</b>", tbl_cell_style),
            Paragraph("Algorithm & Relief Module Dev", tbl_cell_style),
            Paragraph("Shelter Best-Fit recommendation and Population-Proportional relief allocation logic.", tbl_cell_style)
        ],
        [
            Paragraph("20255203057", tbl_cell_center),
            Paragraph("<b>Urmi Akther</b>", tbl_cell_style),
            Paragraph("Module Developer & Dispatch Lead", tbl_cell_style),
            Paragraph("Rescue squad status dispatching, volunteer skill registry, and authentication view.", tbl_cell_style)
        ],
        [
            Paragraph("20255203125", tbl_cell_center),
            Paragraph("<b>Nazmus sakib junayed</b>", tbl_cell_style),
            Paragraph("QA & Testing Specialist", tbl_cell_style),
            Paragraph("Unit testing, algorithm boundary validation, bug tracking, and final project documentation.", tbl_cell_style)
        ]
    ]
    team_table = Table(team_data, colWidths=[70, 115, 125, 194])
    team_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F7FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(team_table)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Key Project Stakeholders:</b>", sub_heading))
    story.append(Paragraph("• <b>Disaster Management Officers & Coordinators:</b> Primary end-users supervising operations and dispatching relief.", bullet_style))
    story.append(Paragraph("• <b>Rescue Squads & Volunteers:</b> Responders receiving optimized routes and task allocations.", bullet_style))
    story.append(Paragraph("• <b>Academic Evaluators & BUBT Faculty:</b> Course instructor evaluating technical soundness and system implementation.", bullet_style))

    # ================= 12. LIMITATIONS & FUTURE WORKS =================
    story.append(Paragraph("12. Limitations & Future Works", section_heading))
    story.append(Paragraph("<b>Limitations:</b>", sub_heading))
    story.append(Paragraph("1. Road network pathfinding currently operates on simulated district node graphs rather than live satellite GIS streaming.", bullet_style))
    story.append(Paragraph("2. Standalone desktop architecture uses local SQLite storage rather than distributed real-time cloud multi-device sync.", bullet_style))
    story.append(Paragraph("<b>Future Works:</b>", sub_heading))
    story.append(Paragraph("1. <b>Live GPS & GIS Integration:</b> Integrate Leaflet / OpenStreetMap API for real-time live map rendering.", bullet_style))
    story.append(Paragraph("2. <b>Automated SMS Alerts:</b> Integrate Twilio or local telecom SMS gateways to broadcast emergency evacuation warnings.", bullet_style))
    story.append(Paragraph("3. <b>Mobile Citizen App:</b> Develop a companion cross-platform mobile app for citizens to trigger one-touch SOS distress beacons.", bullet_style))

    # ================= 13. REFERENCES =================
    story.append(Paragraph("13. References", section_heading))
    story.append(Paragraph("<i>(Formatted following MLA 7th Edition citation standard)</i>", body_style))
    story.append(Paragraph("[1]. Sahana Software Foundation. <i>Sahana Eden Open Source Disaster Management Framework</i>. Sahana Eden, 2021, Web. &lt;https://sahanafoundation.org/eden/&gt;.", bullet_style))
    story.append(Paragraph("[2]. Dijkstra, Edsger W. \"A Note on Two Problems in Connexion with Graphs.\" <i>Numerische Mathematik</i> 1.1 (1959): 269–271. Print.", bullet_style))
    story.append(Paragraph("[3]. Altay, Nezih, and Walter G. Green III. \"OR/MS Research in Disaster Operations Management.\" <i>European Journal of Operational Research</i> 175.1 (2006): 475–493. Print.", bullet_style))
    story.append(Paragraph("[4]. Schimansky, Tom. <i>CustomTkinter: Modern Python UI-Library based on Tkinter</i>. GitHub, 2023, Web. &lt;https://github.com/TomSchimansky/CustomTkinter&gt;.", bullet_style))
    story.append(Paragraph("[5]. United Nations Office for Disaster Risk Reduction (UNDRR). <i>DesInventar Sendai Disaster Information Management System</i>. UNDRR, 2022, Web. &lt;https://www.desinventar.net/&gt;.", bullet_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated PDF: {output_filename}")

if __name__ == "__main__":
    create_proposal_pdf()
