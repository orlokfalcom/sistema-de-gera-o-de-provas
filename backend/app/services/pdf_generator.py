import os
from pathlib import Path
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

from backend.app.models import Exam, ExamItem, Question
from backend.app.config import GENERATED_DIR, BASE_DIR

class NumberedCanvas(canvas.Canvas):
    """Adds automated footer with 'Página X de Y' on all pages."""
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
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 40, 25, footer_text)
        self.drawString(40, 25, "Gerador Inteligente de Avaliações — Ensino Médio")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(40, 38, A4[0] - 40, 38)
        self.restoreState()

class PDFGeneratorService:
    @staticmethod
    def generate_exam_pdf(
        exam: Exam,
        items: List[ExamItem],
        include_answer_key: bool = True,
        only_answer_key: bool = False,
        output_filename: Optional[str] = None
    ) -> str:
        if not output_filename:
            suffix = "_gabarito" if only_answer_key else ("_completa" if include_answer_key else "_estudante")
            output_filename = f"prova_{exam.id[:8]}{suffix}.pdf"

        filepath = GENERATED_DIR / output_filename
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        
        # Custom Typography
        inst_style = ParagraphStyle(
            "Institution",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            alignment=1, # Center
            textColor=colors.HexColor("#1e293b")
        )
        title_style = ParagraphStyle(
            "ExamTitle",
            parent=normal,
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            alignment=1,
            textColor=colors.HexColor("#334155")
        )
        meta_label = ParagraphStyle("MetaLabel", parent=normal, fontName="Helvetica-Bold", fontSize=8.5, leading=11)
        meta_val = ParagraphStyle("MetaVal", parent=normal, fontName="Helvetica", fontSize=8.5, leading=11)
        
        instruc_title = ParagraphStyle("InstTitle", parent=normal, fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#0f172a"))
        instruc_body = ParagraphStyle("InstBody", parent=normal, fontName="Helvetica", fontSize=8, leading=11, textColor=colors.HexColor("#334155"))

        q_num_style = ParagraphStyle("QNum", parent=normal, fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.HexColor("#0f172a"))
        q_disc_style = ParagraphStyle("QDisc", parent=normal, fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.HexColor("#0284c7"))
        statement_style = ParagraphStyle("QStatement", parent=normal, fontName="Helvetica", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1e293b"))
        option_style = ParagraphStyle("QOption", parent=normal, fontName="Helvetica", fontSize=9, leading=12.5, textColor=colors.HexColor("#334155"))

        story = []

        # If only answer key requested
        if only_answer_key:
            story.append(Paragraph(exam.institution_name.upper(), inst_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"GABARITO OFICIAL — {exam.title.upper()} ({exam.academic_period})", title_style))
            story.append(Spacer(1, 15))
            PDFGeneratorService._append_answer_key_table(story, items, styles)
            doc.build(story, canvasmaker=NumberedCanvas)
            return str(filepath)

        # 1. Institutional Header
        header_data = [
            [Paragraph(f"<b>{exam.institution_name.upper()}</b>", inst_style)],
            [Paragraph(f"<b>{exam.title}</b> — {exam.academic_period}", title_style)]
        ]
        t_header = Table(header_data, colWidths=[A4[0] - 72])
        t_header.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_header)
        story.append(Spacer(1, 6))

        # Student Identification Block
        ident_data = [
            [
                Paragraph("<b>ESTUDANTE:</b> ____________________________________________________________________", meta_label),
                Paragraph("<b>TURMA:</b> ___________", meta_label)
            ],
            [
                Paragraph("<b>PROFESSOR(ES):</b> Disciplinas Integradas do Ensino Médio", meta_val),
                Paragraph("<b>DATA:</b> ____/____/2026", meta_val)
            ],
            [
                Paragraph("<b>ASSINATURA DO ESTUDANTE:</b> ____________________________________________________", meta_label),
                Paragraph(f"<b>TOTAL QUESTÕES:</b> {len(items):02d}", meta_label)
            ]
        ]
        t_ident = Table(ident_data, colWidths=[380, 142])
        t_ident.setStyle(TableStyle([
            ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor("#475569")),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc"))
        ]))
        story.append(t_ident)
        story.append(Spacer(1, 8))

        # General Instructions
        instructions = (
            "<b>INSTRUÇÕES GERAIS:</b> 1. Verifique se o caderno contém todas as questões de todas as disciplinas anunciadas. "
            "2. Utilize caneta esferográfica azul ou preta. "
            "3. Leia atentamente cada questão antes de assinalar a alternativa definitiva. "
            "4. Rasuras nas alternativas de múltipla escolha anulam a resposta."
        )
        story.append(Paragraph(instructions, instruc_body))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#94a3b8"), spaceAfter=12))

        # 2. Questions Listing
        current_discipline = None

        for item in items:
            q: Question = item.question
            elements_in_q = []

            # Group Discipline Header if enabled
            if exam.show_discipline_header and exam.organization_mode == "by_discipline":
                if q.discipline != current_discipline:
                    current_discipline = q.discipline
                    elements_in_q.append(Spacer(1, 6))
                    disc_banner = Table(
                        [[Paragraph(f"DISCIPLINA: {current_discipline.upper()}", ParagraphStyle("DiscBanner", parent=normal, fontName="Helvetica-Bold", fontSize=9.5, textColor=colors.HexColor("#0369a1")))]],
                        colWidths=[A4[0] - 72]
                    )
                    disc_banner.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e0f2fe")),
                        ('TOPPADDING', (0,0), (-1,-1), 4),
                        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                        ('LEFTPADDING', (0,0), (-1,-1), 8),
                    ]))
                    elements_in_q.append(disc_banner)
                    elements_in_q.append(Spacer(1, 6))

            # Question Header: Number + Discipline Tag
            tag_text = f" [{q.discipline.upper()}]" if (exam.show_discipline_header and exam.organization_mode != "by_discipline") else ""
            header_text = f"<b>QUESTÃO {item.order_number:02d}</b>{tag_text}"
            elements_in_q.append(Paragraph(header_text, q_num_style))
            elements_in_q.append(Spacer(1, 3))

            # Statement
            # Escape HTML brackets if any in statement
            clean_statement = q.statement.replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
            elements_in_q.append(Paragraph(clean_statement, statement_style))
            elements_in_q.append(Spacer(1, 5))

            # Embedded Images if present
            if q.has_image and q.image_paths_json:
                for img_rel in q.image_paths_json:
                    # Convert static URL to disk path
                    filename = Path(img_rel).name
                    disk_path = BASE_DIR / "storage" / "extracted_images" / filename
                    if disk_path.exists():
                        try:
                            rl_img = RLImage(str(disk_path), width=240, height=140)
                            elements_in_q.append(rl_img)
                            elements_in_q.append(Spacer(1, 4))
                        except Exception:
                            pass

            # Alternatives (A, B, C, D, E)
            if q.question_type == "multiple_choice" and q.options_json:
                for letter in ["A", "B", "C", "D", "E"]:
                    if letter in q.options_json and q.options_json[letter]:
                        opt_text = q.options_json[letter].replace("<", "&lt;").replace(">", "&gt;")
                        opt_p = Paragraph(f"<b>( {letter} )</b> {opt_text}", option_style)
                        elements_in_q.append(opt_p)
                        elements_in_q.append(Spacer(1, 2))
            else:
                # Discursive response lines
                elements_in_q.append(Spacer(1, 4))
                for _ in range(4):
                    elements_in_q.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbd5e1"), spaceAfter=14))

            elements_in_q.append(Spacer(1, 10))
            story.append(KeepTogether(elements_in_q))

        # 3. Answer Key Section at the END (Mandatory by Rule 7 & 8)
        if include_answer_key:
            story.append(PageBreak())
            story.append(Paragraph(exam.institution_name.upper(), inst_style))
            story.append(Spacer(1, 4))
            story.append(Paragraph(f"GABARITO OFICIAL — {exam.title.upper()} ({exam.academic_period})", title_style))
            story.append(Spacer(1, 12))
            story.append(Paragraph("<b>ATENÇÃO:</b> Gabarito confidencial para conferência da comissão pedagógica.", instruc_body))
            story.append(Spacer(1, 10))
            PDFGeneratorService._append_answer_key_table(story, items, styles)

        doc.build(story, canvasmaker=NumberedCanvas)
        return str(filepath)

    @staticmethod
    def _append_answer_key_table(story: list, items: List[ExamItem], styles):
        normal = styles["Normal"]
        th_style = ParagraphStyle("TH", parent=normal, fontName="Helvetica-Bold", fontSize=9, textColor=colors.white, alignment=1)
        td_style = ParagraphStyle("TD", parent=normal, fontName="Helvetica", fontSize=8.5, alignment=1)
        td_disc = ParagraphStyle("TDDisc", parent=normal, fontName="Helvetica", fontSize=8.5, alignment=0)

        table_data = [
            [Paragraph("QUESTÃO", th_style), Paragraph("DISCIPLINA", th_style), Paragraph("RESPOSTA", th_style)]
        ]

        for item in items:
            q = item.question
            ans = q.correct_answer or "PENDENTE"
            table_data.append([
                Paragraph(f"{item.order_number:02d}", td_style),
                Paragraph(q.discipline, td_disc),
                Paragraph(f"<b>{ans}</b>", td_style)
            ])

        ans_table = Table(table_data, colWidths=[80, 240, 100])
        ans_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e293b")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94a3b8")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(ans_table)
