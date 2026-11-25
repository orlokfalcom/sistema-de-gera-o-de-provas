import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF

from backend.app.config import IMAGES_DIR


class PDFExtractionService:
    def __init__(self):
        pass

    def _extract_page_text_columns(self, page: fitz.Page) -> Tuple[str, bool]:
        """
        Extracts text respecting both 1-column and 2-column exam layouts (e.g., ENEM / SEE-MG).
        Uses block bounding boxes (x0, y0, x1, y1, text) to avoid interleaving left and right columns.
        """
        rect = page.rect
        page_w = rect.width if rect.width > 0 else 595.0
        raw_blocks = page.get_text("blocks")
        text_blocks = [
            (b[0], b[1], b[2], b[3], b[4].strip())
            for b in raw_blocks
            if len(b) >= 7 and b[6] == 0 and b[4] and b[4].strip()
        ]
        if not text_blocks:
            return "", False

        mid_left = page_w * 0.47
        mid_right = page_w * 0.52

        left_blocks = []
        right_blocks = []
        spanning_blocks = []

        for b in text_blocks:
            x0, y0, x1, y1, txt = b
            if x1 <= mid_right and x0 < mid_left:
                left_blocks.append(b)
            elif x0 >= mid_left:
                right_blocks.append(b)
            else:
                spanning_blocks.append(b)

        total = len(text_blocks)
        is_two_col = (
            total >= 4
            and len(left_blocks) >= 1
            and len(right_blocks) >= 1
            and len(spanning_blocks) <= max(2, int(total * 0.35))
        )

        if not is_two_col:
            ordered = sorted(text_blocks, key=lambda b: (round(b[1] / 6.0), b[0]))
            return "\n".join(b[4] for b in ordered), False

        # Separate top spanning headers vs bottom spanning footers around column content
        min_col_y = min(b[1] for b in (left_blocks + right_blocks))
        top_headers = sorted([b for b in spanning_blocks if b[1] <= min_col_y + 15], key=lambda b: (b[1], b[0]))
        bottom_footers = sorted([b for b in spanning_blocks if b not in top_headers], key=lambda b: (b[1], b[0]))
        left_sorted = sorted(left_blocks, key=lambda b: (b[1], b[0]))
        right_sorted = sorted(right_blocks, key=lambda b: (b[1], b[0]))

        parts = (
            [b[4] for b in top_headers]
            + [b[4] for b in left_sorted]
            + [b[4] for b in right_sorted]
            + [b[4] for b in bottom_footers]
        )
        return "\n".join(parts), True

    def extract_document(
        self,
        pdf_path: str,
        discipline_hint: str = "",
        teacher_hint: str = "Professor(a)"
    ) -> List[Dict[str, Any]]:
        """
        Parses a PDF file tolerantly: handles 2-column layouts, cross-page broken questions,
        standard & inline alternatives (A-E), Roman numerals (I/II/III/IV), formulas, images,
        inline & separate-sheet answer keys, and assigns confidence scores (high/medium/low).
        """
        doc = fitz.open(pdf_path)
        filename = Path(pdf_path).name
        full_text_parts = []
        page_texts: List[Tuple[int, str, bool]] = []
        page_images: Dict[int, List[str]] = {}

        for page_num in range(len(doc)):
            page = doc[page_num]
            text, is_two_col = self._extract_page_text_columns(page)
            # Strip standalone page-number footers so cross-page questions stitch cleanly
            text_clean = re.sub(r'(?im)^\s*p[áa]gina\s+\d+(?:\s*(?:de|/)\s*\d+)?\s*$', '', text).strip()
            page_texts.append((page_num + 1, text_clean, is_two_col))
            full_text_parts.append(text_clean)

            img_list = page.get_images(full=True)
            page_images[page_num + 1] = []
            for img_idx, img_info in enumerate(img_list):
                xref = img_info[0]
                try:
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    img_filename = f"img_{uuid.uuid4().hex[:8]}_p{page_num+1}_{img_idx}.{image_ext}"
                    img_dest = IMAGES_DIR / img_filename
                    with open(img_dest, "wb") as f:
                        f.write(image_bytes)
                    page_images[page_num + 1].append(f"/static/images/{img_filename}")
                except Exception:
                    pass

        doc.close()
        full_text = "\n\n".join(full_text_parts)

        # Step 1: Detect discipline
        discipline = discipline_hint or self._detect_discipline(full_text) or "Geral"

        # Step 2: Extract explicit answer keys (gabarito sheet or inline table)
        answer_key_map = self._extract_answer_keys(full_text)

        # Step 3: Segment questions with cross-page stitching and answer-sheet isolation
        raw_questions = self._segment_questions(page_texts, page_images)

        # Step 4: Parse alternatives, formulas, Roman numerals, and compute confidence
        processed_questions = []
        for q in raw_questions:
            q_num = q.get("detected_number")
            text_block = q.get("raw_text", "").strip()
            if not text_block:
                continue

            parsed = self._parse_question_details(text_block)

            final_answer = parsed.get("inline_answer")
            if not final_answer and q_num and q_num in answer_key_map:
                final_answer = answer_key_map[q_num]

            confidence_score = 100
            validation_notes = []

            stmt = parsed["statement"]
            opts = parsed.get("options", {})
            q_type = parsed["question_type"]

            if len(stmt) < 18:
                confidence_score -= 35
                validation_notes.append("Enunciado muito curto ou fragmentado.")

            if q_type == "multiple_choice":
                if len(opts) < 2:
                    confidence_score -= 40
                    validation_notes.append(f"Número insuficiente de alternativas identificadas ({len(opts)}).")
                elif len(opts) < 4:
                    confidence_score -= 25
                    validation_notes.append(f"Questão possui menos de 4 alternativas ({len(opts)} encontradas).")
            else:
                confidence_score -= 20
                validation_notes.append("Questão discursiva ou alternativas irregulares fora do padrão A–E.")

            if not final_answer:
                confidence_score -= 30
                validation_notes.append("Gabarito ausente ou pendente de conferência manual.")

            if q.get("spans_pages"):
                confidence_score -= 10
                validation_notes.append("Questão reconstruída entre quebra de páginas.")

            if parsed.get("has_roman_numerals"):
                validation_notes.append("Contém proposições em algarismos romanos (I/II/III).")

            if parsed.get("has_formula"):
                validation_notes.append("Contém fórmula matemática/científica.")

            confidence_score = max(10, min(100, confidence_score))
            if confidence_score >= 80:
                confidence_level = "high"
            elif confidence_score >= 55:
                confidence_level = "medium"
            else:
                confidence_level = "low"

            # Route low-confidence OR missing-answer questions automatically to Pedagogical Review
            validation_status = "pending_review" if (confidence_level == "low" or not final_answer or (q_type == "multiple_choice" and len(opts) < 2)) else "approved"

            item = {
                "discipline": discipline,
                "teacher_name": teacher_hint,
                "question_type": q_type,
                "statement": stmt,
                "options_json": opts if opts else None,
                "correct_answer": final_answer,
                "has_image": len(q["images"]) > 0,
                "image_paths_json": q["images"],
                "page_number": q["page_number"],
                "difficulty": "medio",
                "confidence_score": confidence_score,
                "confidence_level": confidence_level,
                "has_formula": parsed.get("has_formula", False),
                "has_roman_numerals": parsed.get("has_roman_numerals", False),
                "is_two_column": q.get("is_two_column", False),
                "spans_pages": q.get("spans_pages", False),
                "validation_status": validation_status,
                "validation_notes": " | ".join(validation_notes) if validation_notes else None,
                "source_filename": filename,
                "detected_number": q_num
            }
            processed_questions.append(item)

        return processed_questions

    def _detect_discipline(self, text: str) -> str:
        disciplines = [
            "Matemática", "Português", "Língua Portuguesa", "Literatura", "Literatura Brasileira", "Redação",
            "Física", "Química", "Biologia", "História", "Geografia",
            "Filosofia", "Sociologia", "Inglês", "Língua Inglesa", "Espanhol", "Língua Espanhola",
            "Arte", "Artes", "Artes Visuais", "Música", "Teatro", "Dança", "Educação Física",
            "Produção Textual", "Escrita Criativa", "Linguagens Digitais", "Comunicação e Oratória",
            "Literatura Comparada", "Artes Cênicas",
            "Educação Financeira", "Matemática Financeira", "Estatística Aplicada", "Modelagem Matemática",
            "Desenho Técnico", "Geometria Espacial", "Lógica Matemática",
            "Biotecnologia", "Genética", "Sustentabilidade", "Gestão Ambiental", "Práticas Experimentais",
            "Laboratório", "Astronomia", "Astrofísica", "Química Tecnológica", "Farmacologia", "Saúde Pública", "Bioética",
            "Geopolítica", "Direitos Humanos", "Cidadania", "Empreendedorismo", "Empreendedorismo Social",
            "História Regional", "Patrimônio Cultural", "Ética e Política", "Antropologia",
            "Desenvolvimento de Sistemas", "Informática", "Informática para Internet", "Redes de Computadores",
            "Manutenção e Suporte em Informática", "Jogos Digitais", "Programação", "Robótica", "Inteligência Artificial",
            "Ciência de Dados", "Banco de Dados", "Administração", "Logística", "Marketing Digital", "Marketing",
            "Recursos Humanos", "Contabilidade", "Finanças", "Comércio", "Vendas", "Secretariado",
            "Transações Imobiliárias", "Serviços Jurídicos", "Qualidade",
            "Agropecuária", "Agronegócio", "Agricultura", "Zootecnia", "Agroecologia", "Florestas",
            "Meio Ambiente", "Cafeicultura", "Fruticultura", "Piscicultura",
            "Enfermagem", "Análises Clínicas", "Farmácia", "Nutrição e Dietética", "Segurança do Trabalho",
            "Saúde Bucal", "Radiologia", "Agente Comunitário de Saúde", "Gerência em Saúde", "Estética",
            "Eletrotécnica", "Eletrônica", "Mecânica", "Mecatrônica", "Automação Industrial", "Metalurgia",
            "Eletromecânica", "Soldagem", "Refrigeração e Climatização", "Manutenção Automotiva",
            "Edificações", "Mineração", "Agrimensura", "Estradas", "Saneamento", "Geoprocessamento", "Design de Interiores",
            "Alimentos", "Agroindústria", "Laticínios", "Leite e Derivados", "Panificação e Confeitaria",
            "Vestuário", "Moda", "Têxtil", "Móveis", "Biocombustíveis", "Açúcar e Álcool",
            "Gastronomia", "Cozinha", "Hospedagem", "Eventos", "Guia de Turismo", "Lazer",
            "Comunicação Visual", "Multimídia", "Áudio e Vídeo", "Design Gráfico",
            "Secretaria Escolar", "Biblioteconomia", "Libras", "Multimeios Didáticos",
            "Projeto de Vida", "Estudos Orientados", "Práticas Experimentais",
            "Nivelamento em Língua Portuguesa", "Nivelamento em Matemática",
            "Projetos Integradores e de Corresponsabilidade Social (PICS)", "PICS",
            "Cultura Digital e Fundamentos de IA", "Ferramentas para o Mundo do Trabalho",
            "Eletivas", "Iniciação Científica", "Cultura Digital"
        ]
        text_lower = text.lower()
        for disc in disciplines:
            if re.search(r'\b' + re.escape(disc.lower()) + r'\b', text_lower):
                return disc
        return "Multidisciplinar"

    def _extract_answer_keys(self, full_text: str) -> Dict[int, str]:
        answers = {}
        # Prefer explicit standalone GABARITO / RESPOSTAS section at the end of the exam
        gab_matches = list(re.finditer(
            r'(?im)^\s*(?:gabarito(?:\s+oficial)?|folha\s+de\s+respostas?|chaves?\s+de\s+respostas?|respostas?\s*[:\-]\s*(?:quest[ãa]o\s*)?\d)',
            full_text
        ))
        if gab_matches:
            search_space = full_text[gab_matches[-1].start():]
            pattern = r'(?:quest[ãa]o\s*|item\s*|\b)0*(\d{1,3})\s*[\.\-\)\:\=\|–—]\s*([A-Ea-e])\b'
            for num_str, ans in re.findall(pattern, search_space, flags=re.IGNORECASE):
                answers[int(num_str)] = ans.upper()
        return answers

    def _strip_standalone_answer_sheet(self, text: str) -> str:
        """Removes a standalone multi-item answer-key sheet/table from the end of a page without stripping per-question inline 'Gabarito: C'."""
        return re.sub(
            r'(?is)(?:^|\n)\s*(?:gabarito\s+oficial|folha\s+de\s+respostas?|chaves?\s+de\s+respostas?|(?:gabarito|respostas?)\s*[:\-]?\s*(?:\n\s*)?(?:quest[ãa]o\s*)?0*\d{1,3}\s*[\.\-\)\:\=]).*$',
            '',
            text
        ).strip()

    def _segment_questions(
        self,
        page_texts: List[Tuple[int, str, bool]],
        page_images: Dict[int, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Segments text across pages, stitching broken questions across page boundaries!
        """
        questions: List[Dict[str, Any]] = []
        q_start_regex = re.compile(
            r'(?:^|\n)\s*(?:(?:quest[ãa]o|item|q\.?)\s*0*(\d{1,3})\b(?:\s*[:\-\.\)])?|0*(\d{1,2})\s*[\.\-\)]\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ"\(\[\']))',
            re.IGNORECASE
        )

        for page_num, raw_p_text, is_two_col in page_texts:
            p_text = self._strip_standalone_answer_sheet(raw_p_text)
            if not p_text:
                continue

            matches = list(q_start_regex.finditer(p_text))
            if not matches:
                if questions:
                    questions[-1]["raw_text"] += "\n" + p_text
                    questions[-1]["spans_pages"] = True
                    questions[-1]["images"].extend(page_images.get(page_num, []))
                else:
                    questions.append({
                        "detected_number": 1,
                        "raw_text": p_text,
                        "page_number": page_num,
                        "is_two_column": is_two_col,
                        "spans_pages": False,
                        "images": list(page_images.get(page_num, []))
                    })
                continue

            # Stitch leading continuation text (before the first new question header on this page) onto previous question!
            first_start = matches[0].start()
            leading_continuation = p_text[:first_start].strip()
            if leading_continuation and questions:
                # Only stitch if it looks like continuation (options or paragraph, not just a school header)
                if not re.match(r'(?i)^(?:disciplina|col[ée]gio|escola|avalia[çc][ãa]o|professor|aluno)\s*:', leading_continuation):
                    questions[-1]["raw_text"] += "\n" + leading_continuation
                    questions[-1]["spans_pages"] = True

            for i, match in enumerate(matches):
                q_num = int(match.group(1) or match.group(2))
                start_idx = match.start()
                end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(p_text)
                chunk = p_text[start_idx:end_idx].strip()

                questions.append({
                    "detected_number": q_num,
                    "raw_text": chunk,
                    "page_number": page_num,
                    "is_two_column": is_two_col,
                    "spans_pages": False,
                    "images": list(page_images.get(page_num, [])) if i == 0 else []
                })

        return questions

    def _parse_question_details(self, text: str) -> Dict[str, Any]:
        # Extract inline answer like "Gabarito: B", "Resposta correta: (D)"
        inline_ans = None
        ans_match = re.search(
            r'(?i)(?:gabarito|resposta(?:\s+correta)?|alternativa\s+correta|res\.?)\s*[:\-\=]?\s*\(?([A-Ea-e])\)?\b',
            text
        )
        if ans_match:
            inline_ans = ans_match.group(1).upper()
            text = (text[:ans_match.start()] + text[ans_match.end():]).strip()

        has_roman = bool(re.search(r'(?:^|\n|\s)(?:I|II|III|IV|V)\s*[\.\-\)]\s+\S', text))
        has_formula = bool(re.search(r'[√∑∏∫∆Δπ±≤≥≠≈∞²³⁴]|(?:\b(?:sen|cos|tg|log|lim)\b)|(?:\d+\s*[\+\-\*\/\^]\s*\d+\s*=)|\\[a-zA-Z]+\{', text))

        # Match both line-start options AND horizontal multi-column options (separated by 2+ spaces)
        opt_regex = re.compile(
            r'(?:^|\n|\s{2,})(?:[\(\[]\s*([A-Ea-e])\s*[\)\]]|([A-Ea-e])\s*[\.\-\)\:])\s+'
        )
        raw_opt_matches = list(opt_regex.finditer(text))

        # Keep first occurrence of each distinct letter in order
        opt_matches = []
        seen = set()
        for m in raw_opt_matches:
            letter = (m.group(1) or m.group(2)).upper()
            if letter not in seen:
                seen.add(letter)
                opt_matches.append((letter, m))

        if len(opt_matches) >= 2:
            first_opt_start = opt_matches[0][1].start()
            statement = text[:first_opt_start].strip()
            statement = re.sub(
                r'^\s*(?:(?:quest[ãa]o|item|q\.?)\s*\d{1,3}\b(?:\s*[:\-\.\)])?|\d{1,2}\s*[\.\-\)])\s*',
                '',
                statement,
                flags=re.IGNORECASE
            ).strip()

            options = {}
            for idx, (letter, m) in enumerate(opt_matches):
                opt_start = m.end()
                opt_end = opt_matches[idx + 1][1].start() if idx + 1 < len(opt_matches) else len(text)
                opt_content = text[opt_start:opt_end].strip()
                opt_content = " ".join(opt_content.split())
                options[letter] = opt_content

            return {
                "question_type": "multiple_choice",
                "statement": statement,
                "options": options,
                "inline_answer": inline_ans,
                "has_roman_numerals": has_roman,
                "has_formula": has_formula
            }

        # Discursive or irregular alternatives
        clean_stmt = re.sub(
            r'^\s*(?:(?:quest[ãa]o|item|q\.?)\s*\d{1,3}\b(?:\s*[:\-\.\)])?|\d{1,2}\s*[\.\-\)])\s*',
            '',
            text,
            flags=re.IGNORECASE
        ).strip()
        return {
            "question_type": "discursive",
            "statement": clean_stmt,
            "options": {},
            "inline_answer": inline_ans,
            "has_roman_numerals": has_roman,
            "has_formula": has_formula
        }
