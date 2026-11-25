import re
import uuid
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import fitz  # PyMuPDF
from PIL import Image
import io

from backend.app.config import IMAGES_DIR

class PDFExtractionService:
    def __init__(self):
        pass

    def extract_document(
        self,
        pdf_path: str,
        discipline_hint: str = "",
        teacher_hint: str = "Professor(a)"
    ) -> List[Dict[str, Any]]:
        """
        Parses a PDF file, extracts text, recognizes embedded images,
        segments questions, alternatives, and matches answer keys.
        """
        doc = fitz.open(pdf_path)
        filename = Path(pdf_path).name
        full_text = ""
        page_texts = []
        page_images = {}

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            page_texts.append((page_num + 1, text))
            full_text += f"\n--- [PÁGINA {page_num + 1}] ---\n" + text

            # Extract images from page
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
                except Exception as e:
                    # Ignore corrupted image blocks
                    pass

        doc.close()

        # Step 1: Detect discipline if not provided or refine it
        discipline = discipline_hint or self._detect_discipline(full_text) or "Geral"

        # Step 2: Extract explicit answer keys (gabarito) if present in the document
        answer_key_map = self._extract_answer_keys(full_text)

        # Step 3: Segment questions
        raw_questions = self._segment_questions(page_texts, page_images)

        # Step 4: Refine each question: parse alternatives, statement, and attach correct answer
        processed_questions = []
        for q in raw_questions:
            q_num = q.get("detected_number")
            text_block = q.get("raw_text", "").strip()

            parsed = self._parse_question_details(text_block)
            
            # Resolve answer: from inline answer or document answer key
            final_answer = parsed.get("inline_answer")
            if not final_answer and q_num and q_num in answer_key_map:
                final_answer = answer_key_map[q_num]

            # Validation check according to pedagogical rules
            validation_status = "approved"
            validation_notes = []

            if not final_answer:
                validation_status = "pending_review"
                validation_notes.append("Gabarito ausente ou pendente de conferência manual.")

            if parsed["question_type"] == "multiple_choice":
                opts = parsed.get("options", {})
                if len(opts) < 2:
                    validation_status = "pending_review"
                    validation_notes.append(f"Número insuficiente de alternativas identificadas ({len(opts)}).")
                elif len(opts) < 4:
                    validation_notes.append(f"Questão possui menos de 4 alternativas ({len(opts)} encontradas).")

            item = {
                "discipline": discipline,
                "teacher_name": teacher_hint,
                "question_type": parsed["question_type"],
                "statement": parsed["statement"],
                "options_json": parsed["options"],
                "correct_answer": final_answer,
                "has_image": len(q["images"]) > 0,
                "image_paths_json": q["images"],
                "page_number": q["page_number"],
                "difficulty": "medio",
                "validation_status": validation_status,
                "validation_notes": " | ".join(validation_notes) if validation_notes else None,
                "source_filename": filename,
                "detected_number": q_num
            }
            processed_questions.append(item)

        return processed_questions

    def _detect_discipline(self, text: str) -> str:
        disciplines = [
            # Formação Geral Básica (BNCC)
            "Matemática", "Português", "Língua Portuguesa", "Literatura", "Redação",
            "Física", "Química", "Biologia", "História", "Geografia",
            "Filosofia", "Sociologia", "Inglês", "Língua Inglesa", "Espanhol", "Artes", "Arte", "Educação Física",
            # Itinerários Formativos & Cursos Integrados (Novo Ensino Médio)
            "Robótica", "Educação Financeira", "Empreendedorismo", "Projeto de Vida",
            "Iniciação Científica", "Biotecnologia", "Redação Avançada", "Geopolítica",
            "Astronomia", "Desenvolvimento de Sistemas", "Informática", "Administração",
            "Logística", "Marketing Digital", "Meio Ambiente", "Inteligência Artificial",
            "Comunicação e Mídias", "Cultura Digital"
        ]
        text_lower = text.lower()
        for disc in disciplines:
            if re.search(r'\b' + re.escape(disc.lower()) + r'\b', text_lower):
                return disc
        return "Multidisciplinar"

    def _extract_answer_keys(self, full_text: str) -> Dict[int, str]:
        """
        Detects tables or lines containing answer keys, e.g.:
        GABARITO:
        1 - A, 2 - B, 03) C, 4. D
        ou 1: A, 2: B
        """
        answers = {}
        # Find Gabarito section if present
        gabarito_match = re.search(r'(?i)(?:gabarito|respostas?|chaves? de respostas?)(.*)', full_text, re.DOTALL)
        search_space = gabarito_match.group(1) if gabarito_match else full_text

        # Matches patterns like "01 - A", "1. B", "1) C", "Questão 1: D", "01: E", "1=A"
        pattern = r'(?:quest[ãa]o\s*)?(\d{1,2})\s*[\.\-\)\:\=]\s*([A-Ea-e])\b'
        matches = re.findall(pattern, search_space)
        for num_str, ans in matches:
            answers[int(num_str)] = ans.upper()

        return answers

    def _segment_questions(
        self,
        page_texts: List[Tuple[int, str]],
        page_images: Dict[int, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Segments continuous text into question blocks based on numbered delimiters.
        """
        questions = []
        
        # Regex to detect question starts:
        # e.g.: "Questão 01", "QUESTÃO 1 -", "1.", "1)", "1 -"
        q_start_regex = re.compile(
            r'(?:^|\n)\s*(?:(?:quest[ãa]o|item)\s*(\d{1,2})|(\d{1,2})\s*[\.\-\)])(?:\s*[:\-\.]|\s+)',
            re.IGNORECASE
        )

        for page_num, p_text in page_texts:
            # We locate matches on the page
            matches = list(q_start_regex.finditer(p_text))
            if not matches:
                # If no question header on this page, might belong to previous or be discursiva
                if questions:
                    questions[-1]["raw_text"] += "\n" + p_text
                    questions[-1]["images"].extend(page_images.get(page_num, []))
                else:
                    # Single item document or intro
                    questions.append({
                        "detected_number": 1,
                        "raw_text": p_text,
                        "page_number": page_num,
                        "images": page_images.get(page_num, [])
                    })
                continue

            for i, match in enumerate(matches):
                q_num = int(match.group(1) or match.group(2))
                start_idx = match.start()
                end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(p_text)
                chunk = p_text[start_idx:end_idx].strip()

                questions.append({
                    "detected_number": q_num,
                    "raw_text": chunk,
                    "page_number": page_num,
                    "images": page_images.get(page_num, []) if i == 0 else []
                })

        return questions

    def _parse_question_details(self, text: str) -> Dict[str, Any]:
        """
        Splits a raw question block into statement, alternatives (A-E),
        and any inline answer key.
        """
        # Strip any document-level or block-level gabarito / answer key section
        # so it never leaks into the statement or alternative text
        text = re.sub(
            r'(?i)(?:^|\n)\s*(?:gabarito(?:\s+oficial)?|respostas?|chaves? de respostas?)\s*[:\-].*$',
            '',
            text,
            flags=re.DOTALL | re.MULTILINE
        ).strip()

        # Look for inline answer notation like "Gabarito: B" or "Resposta: C"
        inline_ans = None
        ans_match = re.search(r'(?i)(?:gabarito|resposta|res\.?)\s*[:\-]?\s*([A-Ea-e])\b', text)
        if ans_match:
            inline_ans = ans_match.group(1).upper()
            # Remove the answer line from the question text so it doesn't spoil the student exam
            text = text[:ans_match.start()] + text[ans_match.end():]

        # Alternative markers: a), b), c), d), e) OR (A), (B), (C) OR [A], [B] OR A-, B-, A., A:
        opt_regex = re.compile(
            r'(?:^|\n)\s*(?:[\(\[]\s*([A-Ea-e])\s*[\)\]]|\b([A-Ea-e])\s*[\.\-\)\:\=])\s+',
            re.MULTILINE
        )

        opt_matches = list(opt_regex.finditer(text))

        if len(opt_matches) >= 2:
            # Multiple choice question
            first_opt_start = opt_matches[0].start()
            statement = text[:first_opt_start].strip()

            # Clean statement header (e.g. "Questão 1 - ", "1.")
            statement = re.sub(
                r'^(?:(?:quest[ãa]o|item)\s*\d{1,2}|\d{1,2}\s*[\.\-\)])(?:\s*[:\-\.]|\s+)',
                '',
                statement,
                flags=re.IGNORECASE
            ).strip()

            options = {}
            for i, m in enumerate(opt_matches):
                letter = (m.group(1) or m.group(2)).upper()
                opt_start = m.end()
                opt_end = opt_matches[i + 1].start() if i + 1 < len(opt_matches) else len(text)
                opt_content = text[opt_start:opt_end].strip()
                # Clean any answer key block from option content
                opt_content = re.sub(
                    r'(?i)(?:gabarito(?:\s+oficial)?|respostas?|chaves? de respostas?).*$',
                    '',
                    opt_content
                ).strip()
                # Clean line breaks inside alternative
                opt_content = " ".join(opt_content.split())
                options[letter] = opt_content

            return {
                "question_type": "multiple_choice",
                "statement": statement,
                "options": options,
                "inline_answer": inline_ans
            }
        else:
            # Discursive question
            statement = re.sub(
                r'^(?:(?:quest[ãa]o|item)\s*\d{1,2}|\d{1,2}\s*[\.\-\)])(?:\s*[:\-\.]|\s+)',
                '',
                text,
                flags=re.IGNORECASE
            ).strip()

            return {
                "question_type": "discursive",
                "statement": statement,
                "options": {},
                "inline_answer": inline_ans
            }
