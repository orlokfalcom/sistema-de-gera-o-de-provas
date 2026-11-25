import os
from pathlib import Path
from typing import List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

from backend.app.models import Exam, ExamItem, Question
from backend.app.config import GENERATED_DIR, BASE_DIR

class DocxGeneratorService:
    @staticmethod
    def generate_exam_docx(
        exam: Exam,
        items: List[ExamItem],
        include_answer_key: bool = True,
        output_filename: Optional[str] = None
    ) -> str:
        if not output_filename:
            output_filename = f"prova_{exam.id[:8]}.docx"

        filepath = GENERATED_DIR / output_filename
        doc = docx.Document()

        # Page setup: Margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        # 1. Institutional Header
        p_inst = doc.add_paragraph()
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_inst = p_inst.add_run(exam.institution_name.upper())
        r_inst.bold = True
        r_inst.font.size = Pt(13)
        r_inst.font.color.rgb = RGBColor(30, 41, 59)

        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_title = p_title.add_run(f"{exam.title} — {exam.academic_period}")
        r_title.bold = True
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = RGBColor(71, 85, 105)

        # Student Identification Table
        table = doc.add_table(rows=3, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        rows = table.rows
        rows[0].cells[0].text = "ESTUDANTE: ____________________________________________"
        rows[0].cells[1].text = "TURMA: ____________"
        rows[1].cells[0].text = "PROFESSOR(ES): Disciplinas Integradas do Ensino Médio"
        rows[1].cells[1].text = "DATA: ____/____/2026"
        rows[2].cells[0].text = "ASSINATURA: ___________________________________________"
        rows[2].cells[1].text = f"TOTAL QUESTÕES: {len(items):02d}"

        # Style table cells font
        for row in rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)
                        run.font.name = "Arial"

        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(6)
        p_space.paragraph_format.space_after = Pt(4)

        # General Instructions
        p_instruc = doc.add_paragraph()
        r_instruc_label = p_instruc.add_run("INSTRUÇÕES GERAIS: ")
        r_instruc_label.bold = True
        r_instruc_label.font.size = Pt(8.5)
        r_instruc = p_instruc.add_run(
            "1. Verifique se o caderno contém todas as questões de todas as disciplinas anunciadas. "
            "2. Utilize caneta azul ou preta. 3. Leia com atenção antes de responder."
        )
        r_instruc.font.size = Pt(8.5)

        # Separator line
        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_after = Pt(10)
        p_sep_run = p_sep.add_run("—" * 65)
        p_sep_run.font.color.rgb = RGBColor(148, 163, 184)

        # 2. Questions Listing
        current_discipline = None
        for item in items:
            q: Question = item.question

            # Group Discipline Header
            if exam.show_discipline_header and exam.organization_mode == "by_discipline":
                if q.discipline != current_discipline:
                    current_discipline = q.discipline
                    p_disc = doc.add_paragraph()
                    p_disc.paragraph_format.space_before = Pt(10)
                    p_disc.paragraph_format.space_after = Pt(4)
                    r_disc = p_disc.add_run(f"■ DISCIPLINA: {current_discipline.upper()}")
                    r_disc.bold = True
                    r_disc.font.size = Pt(10)
                    r_disc.font.color.rgb = RGBColor(2, 132, 199)

            # Question Title & Discipline Tag
            tag_text = f" [{q.discipline.upper()}]" if (exam.show_discipline_header and exam.organization_mode != "by_discipline") else ""
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(8)
            p_q.paragraph_format.space_after = Pt(3)
            r_qnum = p_q.add_run(f"QUESTÃO {item.order_number:02d}{tag_text}")
            r_qnum.bold = True
            r_qnum.font.size = Pt(10)
            r_qnum.font.color.rgb = RGBColor(15, 23, 42)

            # Statement
            p_stmt = doc.add_paragraph()
            p_stmt.paragraph_format.space_after = Pt(4)
            r_stmt = p_stmt.add_run(q.statement)
            r_stmt.font.size = Pt(9.5)

            # Embedded Image
            if q.has_image and q.image_paths_json:
                for img_rel in q.image_paths_json:
                    img_name = Path(img_rel).name
                    disk_path = BASE_DIR / "storage" / "extracted_images" / img_name
                    if disk_path.exists():
                        try:
                            doc.add_picture(str(disk_path), width=Inches(3.2))
                        except Exception:
                            pass

            # Alternatives
            if q.question_type == "multiple_choice" and q.options_json:
                for letter in ["A", "B", "C", "D", "E"]:
                    if letter in q.options_json and q.options_json[letter]:
                        p_opt = doc.add_paragraph()
                        p_opt.paragraph_format.left_indent = Inches(0.2)
                        p_opt.paragraph_format.space_after = Pt(2)
                        r_letter = p_opt.add_run(f"( {letter} ) ")
                        r_letter.bold = True
                        r_letter.font.size = Pt(9)
                        r_opt = p_opt.add_run(q.options_json[letter])
                        r_opt.font.size = Pt(9)
            else:
                # Discursive lines
                for _ in range(4):
                    p_line = doc.add_paragraph()
                    p_line.paragraph_format.space_after = Pt(8)
                    r_l = p_line.add_run("." * 105)
                    r_l.font.color.rgb = RGBColor(203, 213, 225)

        # 3. Answer Key at the end
        if include_answer_key:
            doc.add_page_break()
            p_ak_title = doc.add_paragraph()
            p_ak_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_ak_t = p_ak_title.add_run(f"GABARITO OFICIAL — {exam.title.upper()} ({exam.academic_period})")
            r_ak_t.bold = True
            r_ak_t.font.size = Pt(12)
            r_ak_t.font.color.rgb = RGBColor(30, 41, 59)

            ak_table = doc.add_table(rows=1, cols=3)
            ak_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = ak_table.rows[0].cells
            hdr_cells[0].text = "QUESTÃO"
            hdr_cells[1].text = "DISCIPLINA"
            hdr_cells[2].text = "RESPOSTA"

            # Style header
            for cell in hdr_cells:
                shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="1E293B"/>')
                cell._tc.get_or_add_tcPr().append(shading_elm)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9)

            for item in items:
                q = item.question
                row_cells = ak_table.add_row().cells
                row_cells[0].text = f"{item.order_number:02d}"
                row_cells[1].text = q.discipline
                row_cells[2].text = q.correct_answer or "PENDENTE"
                for cell in row_cells:
                    for paragraph in cell.paragraphs:
                        for run in paragraph.runs:
                            run.font.size = Pt(9)

        doc.save(str(filepath))
        return str(filepath)
