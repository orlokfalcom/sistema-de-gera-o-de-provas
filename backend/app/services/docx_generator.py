import os
from pathlib import Path
from typing import List, Optional
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
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
        """
        Generates an editable Microsoft Word document (.docx) strictly following
        Brazilian ABNT standards (NBR 14724):
        - Paper: A4 (21,0 cm x 29,7 cm)
        - Margins: Top 3,0 cm, Left 3,0 cm, Bottom 2,0 cm, Right 2,0 cm
        - Typography: Arial standard, 12pt body, justified text alignment
        - Formal institutional header and standard answer key table
        """
        if not output_filename:
            output_filename = f"prova_{exam.id[:8]}.docx"

        filepath = GENERATED_DIR / output_filename
        doc = docx.Document()

        # Page setup: Standard ABNT NBR 14724 Margins & A4 Paper
        sections = doc.sections
        for section in sections:
            section.page_width = Cm(21.0)
            section.page_height = Cm(29.7)
            section.top_margin = Cm(3.0)     # Superior: 3,0 cm
            section.left_margin = Cm(3.0)    # Esquerda: 3,0 cm
            section.bottom_margin = Cm(2.0)  # Inferior: 2,0 cm
            section.right_margin = Cm(2.0)   # Direita: 2,0 cm

            # ABNT Header
            header = section.header
            header_p = header.paragraphs[0]
            header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            h_run = header_p.add_run(f"{exam.institution_name.upper()} • AVALIAÇÃO INTEGRADA DO ENSINO MÉDIO")
            h_run.font.name = "Arial"
            h_run.font.size = Pt(8.5)
            h_run.font.color.rgb = RGBColor(100, 116, 139)

        # 1. Institutional Header (ABNT: Centralizado, Negrito, Caixa Alta)
        p_inst = doc.add_paragraph()
        p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_inst.paragraph_format.space_before = Pt(0)
        p_inst.paragraph_format.space_after = Pt(2)
        r_inst = p_inst.add_run(exam.institution_name.upper())
        r_inst.bold = True
        r_inst.font.name = "Arial"
        r_inst.font.size = Pt(12)
        r_inst.font.color.rgb = RGBColor(0, 0, 0)

        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_title.paragraph_format.space_after = Pt(8)
        r_title = p_title.add_run(f"{exam.title.upper()} — {exam.academic_period.upper()}")
        r_title.bold = True
        r_title.font.name = "Arial"
        r_title.font.size = Pt(11)
        r_title.font.color.rgb = RGBColor(30, 41, 59)

        # Student Identification Table (ABNT / Sobriedade Institucional)
        table = doc.add_table(rows=3, cols=2)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False

        rows = table.rows
        rows[0].cells[0].text = "ESTUDANTE: ____________________________________________"
        rows[0].cells[1].text = "TURMA: ____________"
        rows[1].cells[0].text = "PROFESSORES: Componentes Curriculares Integrados do Ensino Médio"
        rows[1].cells[1].text = "DATA: ____/____/2026"
        rows[2].cells[0].text = "ASSINATURA DO ALUNO: __________________________________"
        rows[2].cells[1].text = f"TOTAL DE QUESTÕES: {len(items):02d}"

        # Style table cells font (Arial 9.5pt)
        for row in rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_before = Pt(2)
                    paragraph.paragraph_format.space_after = Pt(2)
                    for run in paragraph.runs:
                        run.font.name = "Arial"
                        run.font.size = Pt(9.5)
                        run.font.color.rgb = RGBColor(0, 0, 0)

        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_before = Pt(4)
        p_space.paragraph_format.space_after = Pt(4)

        # General Instructions (ABNT: Justificado)
        p_instruc = doc.add_paragraph()
        p_instruc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_instruc.paragraph_format.line_spacing = 1.15
        p_instruc.paragraph_format.space_after = Pt(8)
        r_instruc_label = p_instruc.add_run("INSTRUÇÕES GERAIS (PADRÃO ABNT): ")
        r_instruc_label.bold = True
        r_instruc_label.font.name = "Arial"
        r_instruc_label.font.size = Pt(9)
        r_instruc = p_instruc.add_run(
            "1. Confira se este caderno de avaliação contém a numeração sequencial contínua completa de todas as disciplinas "
            "da Formação Geral Básica e dos Itinerários Formativos. "
            "2. Responda com clareza utilizando caneta esferográfica de tinta azul ou preta. "
            "3. Em questões de múltipla escolha, assinale apenas uma alternativa; rasuras anulam a resposta."
        )
        r_instruc.font.name = "Arial"
        r_instruc.font.size = Pt(9)

        # Separator line
        p_sep = doc.add_paragraph()
        p_sep.paragraph_format.space_after = Pt(10)
        p_sep_run = p_sep.add_run("—" * 68)
        p_sep_run.font.name = "Arial"
        p_sep_run.font.color.rgb = RGBColor(148, 163, 184)

        # 2. Questions Listing (ABNT: Arial, 11-12pt, Justificado, Alternativas com recuo)
        current_discipline = None
        for item in items:
            q: Question = item.question

            # Group Discipline Header
            if exam.show_discipline_header and exam.organization_mode == "by_discipline":
                if q.discipline != current_discipline:
                    current_discipline = q.discipline
                    p_disc = doc.add_paragraph()
                    p_disc.paragraph_format.space_before = Pt(12)
                    p_disc.paragraph_format.space_after = Pt(4)
                    r_disc = p_disc.add_run(f"■ ÁREA / DISCIPLINA: {current_discipline.upper()}")
                    r_disc.bold = True
                    r_disc.font.name = "Arial"
                    r_disc.font.size = Pt(11)
                    r_disc.font.color.rgb = RGBColor(2, 132, 199)

            # Question Number
            tag_text = f" [{q.discipline.upper()}]" if (exam.show_discipline_header and exam.organization_mode != "by_discipline") else ""
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(8)
            p_q.paragraph_format.space_after = Pt(3)
            r_qnum = p_q.add_run(f"QUESTÃO {item.order_number:02d}{tag_text}")
            r_qnum.bold = True
            r_qnum.font.name = "Arial"
            r_qnum.font.size = Pt(11)
            r_qnum.font.color.rgb = RGBColor(0, 0, 0)

            # Statement (ABNT: Justificado, entrelinhas 1.15)
            p_stmt = doc.add_paragraph()
            p_stmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_stmt.paragraph_format.line_spacing = 1.15
            p_stmt.paragraph_format.space_after = Pt(4)
            r_stmt = p_stmt.add_run(q.statement)
            r_stmt.font.name = "Arial"
            r_stmt.font.size = Pt(10.5)
            r_stmt.font.color.rgb = RGBColor(0, 0, 0)

            # Embedded Image
            if q.has_image and q.image_paths_json:
                for img_rel in q.image_paths_json:
                    img_name = Path(img_rel).name
                    disk_path = BASE_DIR / "storage" / "extracted_images" / img_name
                    if disk_path.exists():
                        try:
                            p_img = doc.add_paragraph()
                            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                            doc.add_picture(str(disk_path), width=Inches(3.2))
                        except Exception:
                            pass

            # Alternatives (ABNT: Recuo à esquerda de 1,25 cm, Justificado/Alinhado)
            if q.question_type == "multiple_choice" and q.options_json:
                for letter in ["A", "B", "C", "D", "E"]:
                    if letter in q.options_json and q.options_json[letter]:
                        p_opt = doc.add_paragraph()
                        p_opt.alignment = WD_ALIGN_PARAGRAPH.LEFT
                        p_opt.paragraph_format.left_indent = Cm(1.25)
                        p_opt.paragraph_format.line_spacing = 1.15
                        p_opt.paragraph_format.space_after = Pt(2)
                        
                        r_letter = p_opt.add_run(f"({letter}) ")
                        r_letter.bold = True
                        r_letter.font.name = "Arial"
                        r_letter.font.size = Pt(10)
                        r_letter.font.color.rgb = RGBColor(0, 0, 0)
                        
                        r_opt = p_opt.add_run(q.options_json[letter])
                        r_opt.font.name = "Arial"
                        r_opt.font.size = Pt(10)
                        r_opt.font.color.rgb = RGBColor(0, 0, 0)
            else:
                # Discursive lines
                for _ in range(4):
                    p_line = doc.add_paragraph()
                    p_line.paragraph_format.space_after = Pt(8)
                    r_l = p_line.add_run("." * 105)
                    r_l.font.name = "Arial"
                    r_l.font.color.rgb = RGBColor(203, 213, 225)

        # 3. Answer Key at the end (ABNT: Tabela padronizada)
        if include_answer_key:
            doc.add_page_break()
            p_ak_title = doc.add_paragraph()
            p_ak_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_ak_title.paragraph_format.space_before = Pt(6)
            p_ak_title.paragraph_format.space_after = Pt(8)
            r_ak_t = p_ak_title.add_run(f"GABARITO OFICIAL — {exam.title.upper()} ({exam.academic_period})")
            r_ak_t.bold = True
            r_ak_t.font.name = "Arial"
            r_ak_t.font.size = Pt(12)
            r_ak_t.font.color.rgb = RGBColor(0, 0, 0)

            ak_table = doc.add_table(rows=1, cols=3)
            ak_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = ak_table.rows[0].cells
            hdr_cells[0].text = "QUESTÃO"
            hdr_cells[1].text = "DISCIPLINA"
            hdr_cells[2].text = "RESPOSTA"

            # Style header (ABNT: Negrito, sóbrio)
            for cell in hdr_cells:
                shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="0F172A"/>')
                cell._tc.get_or_add_tcPr().append(shading_elm)
                for paragraph in cell.paragraphs:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.name = "Arial"
                        run.font.color.rgb = RGBColor(255, 255, 255)
                        run.font.size = Pt(9.5)

            for item in items:
                q = item.question
                row_cells = ak_table.add_row().cells
                row_cells[0].text = f"{item.order_number:02d}"
                row_cells[1].text = q.discipline
                row_cells[2].text = q.correct_answer or "PENDENTE"
                
                # Center Question number and Answer
                row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                row_cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

                for cell in row_cells:
                    for paragraph in cell.paragraphs:
                        paragraph.paragraph_format.space_before = Pt(2)
                        paragraph.paragraph_format.space_after = Pt(2)
                        for run in paragraph.runs:
                            run.font.name = "Arial"
                            run.font.size = Pt(9.5)
                            run.font.color.rgb = RGBColor(0, 0, 0)

        doc.save(str(filepath))
        return str(filepath)
