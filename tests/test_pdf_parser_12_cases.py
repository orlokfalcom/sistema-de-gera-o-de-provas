"""
Suíte Automatizada de Testes de Robustez do Extrator de Questões (Fase 5.4).
Gera programaticamente 12 PDFs distintos cobrindo cenários reais e casos extremos do Ensino Médio / SEE-MG:
  1. PDF padrão 1 coluna com gabarito em folha separada ao final (alta confiança -> approved)
  2. PDF com gabarito inline após cada questão ("Gabarito: D" — sem vazar no enunciado!)
  3. PDF SEM gabarito (deve ir automaticamente para Conferência Pedagógica: pending_review)
  4. PDF em 2 colunas estilo ENEM (não pode embaralhar coluna esquerda com coluna direita!)
  5. PDF com questão quebrada entre 2 páginas (enunciado na pág. 1 + alternativas C/D/E na pág. 2)
  6. PDF com proposições em algarismos romanos (I, II, III, IV) + alternativas A–E
  7. PDF com fórmulas matemáticas e científicas (√, Δ, ∑, x², log, sen/cos)
  8. PDF com alternativas irregulares/incompletas (apenas A, B, C -> confiança média/baixa)
  9. PDF com alternativas horizontais na mesma linha ("(A) 10   (B) 20   (C) 30   (D) 40   (E) 50")
  10. PDF com imagem/figura vetorial/raster embutida na questão (has_image=True)
  11. PDF de questões discursivas / abertas sem alternativas (question_type='discursive' -> pending_review)
  12. PDF de Itinerário Técnico SEE/MG (Desenvolvimento de Sistemas / PICS) com detecção automática de disciplina
"""
import sys
import time
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import fitz  # PyMuPDF
from PIL import Image
import io
from backend.app.services.pdf_extractor import PDFExtractionService


def _make_pdf_single_page(lines_text: str, dest: Path):
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_textbox(fitz.Rect(45, 45, 550, 795), lines_text, fontsize=10.5, fontname="helv")
    doc.save(str(dest))
    doc.close()


def build_12_test_pdfs(folder: Path):
    pdfs = {}

    # 1. Standard 1-column + separate answer sheet
    doc = fitz.open()
    p1 = doc.new_page()
    p1.insert_textbox(fitz.Rect(45, 45, 550, 790), (
        "DISCIPLINA: MATEMÁTICA\n\n"
        "Questão 01. Uma função afim f(x) = 3x - 6 intercepta o eixo das abscissas no ponto cuja coordenada x vale:\n"
        "(A) 1\n(B) 2\n(C) 3\n(D) 4\n(E) 6\n\n"
        "Questão 02. O valor da soma dos ângulos internos de um triângulo qualquer na geometria euclidiana plana é:\n"
        "(A) 90 graus\n(B) 120 graus\n(C) 180 graus\n(D) 270 graus\n(E) 360 graus\n"
    ), fontsize=10.5)
    p2 = doc.new_page()
    p2.insert_textbox(fitz.Rect(45, 45, 550, 790), "GABARITO OFICIAL\n01 - B\n02 - C\n", fontsize=11)
    pdfs["01_padrao_folha_gabarito"] = folder / "01_padrao_folha_gabarito.pdf"
    doc.save(str(pdfs["01_padrao_folha_gabarito"]))
    doc.close()

    # 2. Inline answer key (must extract answer AND strip from statement/options)
    pdfs["02_gabarito_inline"] = folder / "02_gabarito_inline.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: BIOLOGIA\n\n"
        "Questão 1. Qual ácido nucleico atua diretamente no transporte de aminoácidos até os ribossomos durante a tradução proteica?\n"
        "A) DNA mitocondrial\nB) RNA mensageiro\nC) RNA transportador\nD) RNA ribossômico\nE) ATP sintetase\n"
        "Gabarito: C\n",
        pdfs["02_gabarito_inline"]
    )

    # 3. Missing answer key -> must go to pending_review
    pdfs["03_gabarito_ausente"] = folder / "03_gabarito_ausente.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: HISTÓRIA\n\n"
        "Questão 1. Analise os fatores econômicos e fiscais que desencadearam a Inconfidência Mineira em Vila Rica no final do século XVIII:\n"
        "(A) Apoio popular à derrama\n(B) Crise aurífera e cobrança compulsória de impostos atrasados\n(C) Industrialização têxtil\n(D) Tratado de Tordesilhas\n(E) Abertura dos portos\n",
        pdfs["03_gabarito_ausente"]
    )

    # 4. True 2-column ENEM layout
    doc = fitz.open()
    pg = doc.new_page(width=595, height=842)
    pg.insert_textbox(fitz.Rect(40, 30, 555, 65), "CADERNO MULTIDISCIPLINAR — GEOGRAFIA", fontsize=12)
    # Left column (x: 40..275)
    pg.insert_textbox(fitz.Rect(40, 80, 275, 420), (
        "QUESTÃO 01\n"
        "O domínio morfoclimático do Cerrado, predominante em Minas Gerais, caracteriza-se por:\n"
        "(A) Solos ácidos e vegetação tropófila adaptada à sazonalidade.\n"
        "(B) Clima equatorial superúmido sem estação seca.\n"
        "(C) Vegetação de coníferas boreais.\n"
        "(D) Permafrost contínuo.\n"
        "(E) Ausência de bacias hidrográficas.\n"
        "Gabarito: A"
    ), fontsize=9.5)
    # Right column (x: 315..555)
    pg.insert_textbox(fitz.Rect(315, 80, 555, 420), (
        "QUESTÃO 02\n"
        "O fenômeno climático urbano caracterizado pela elevação das temperaturas nas áreas centrais densamente impermeabilizadas denomina-se:\n"
        "(A) Inversão geostrófica.\n"
        "(B) Ilha de calor urbana.\n"
        "(C) La Niña costeira.\n"
        "(D) Frente polar seca.\n"
        "(E) Brisa marítima.\n"
        "Gabarito: B"
    ), fontsize=9.5)
    pdfs["04_duas_colunas_enem"] = folder / "04_duas_colunas_enem.pdf"
    doc.save(str(pdfs["04_duas_colunas_enem"]))
    doc.close()

    # 5. Question broken across two pages
    doc = fitz.open()
    pg1 = doc.new_page()
    pg1.insert_textbox(fitz.Rect(45, 580, 550, 810), (
        "DISCIPLINA: FÍSICA\n\n"
        "Questão 01. Um bloco de massa 4 kg sofre a ação de uma força resultante constante de 20 N sobre um plano horizontal sem atrito. Nessas condições, sua aceleração escalar será:\n"
        "(A) 2 m/s²\n"
        "(B) 4 m/s²\n"
        "Página 1 de 2"
    ), fontsize=10.5)
    pg2 = doc.new_page()
    pg2.insert_textbox(fitz.Rect(45, 45, 550, 790), (
        "(C) 5 m/s²\n"
        "(D) 10 m/s²\n"
        "(E) 80 m/s²\n"
        "Resposta: C\n\n"
        "Questão 02. A unidade de potência elétrica no Sistema Internacional de Unidades (SI) é o:\n"
        "(A) Joule\n(B) Watt\n(C) Volt\n(D) Ohm\n(E) Coulomb\n"
        "Resposta: B\n"
    ), fontsize=10.5)
    pdfs["05_quebra_entre_paginas"] = folder / "05_quebra_entre_paginas.pdf"
    doc.save(str(pdfs["05_quebra_entre_paginas"]))
    doc.close()

    # 6. Roman numerals propositions (I, II, III, IV)
    pdfs["06_algarismos_romanos"] = folder / "06_algarismos_romanos.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: SOCIOLOGIA\n\n"
        "Questão 1. Sobre o conceito de cidadania e direitos fundamentais na Constituição de 1988, avalie as afirmativas:\n"
        "I. Os direitos sociais incluem educação, saúde, trabalho e moradia.\n"
        "II. O voto no Brasil é direto, secreto, universal e periódico.\n"
        "III. A dignidade da pessoa humana constitui fundamento da República.\n"
        "Está correto o que se afirma em:\n"
        "(A) I, apenas.\n(B) II, apenas.\n(C) I e III, apenas.\n(D) II e III, apenas.\n(E) I, II e III.\n"
        "Gabarito: E\n",
        pdfs["06_algarismos_romanos"]
    )

    # 7. Mathematical & scientific formulas
    pdfs["07_formulas_matematicas"] = folder / "07_formulas_matematicas.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: QUÍMICA\n\n"
        "Questão 1. Considere a equação quadrática x² - 5x + 6 = 0 onde Δ = b² - 4ac ≥ 0 e √Δ = 1. As raízes reais são:\n"
        "[A] 1 e 6\n[B] 2 e 3\n[C] -2 e -3\n[D] 0 e 5\n[E] 3 e 4\n"
        "Gabarito: B\n",
        pdfs["07_formulas_matematicas"]
    )

    # 8. Irregular alternatives (only 3 options A, B, C -> medium confidence)
    pdfs["08_alternativas_irregulares"] = folder / "08_alternativas_irregulares.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: FILOSOFIA\n\n"
        "Questão 1. Para Aristóteles, a virtude ética consiste na justa medida (mediania) entre dois vícios extremos. Isso significa:\n"
        "a) Agir com equilíbrio racional prudente.\n"
        "b) Buscar o excesso impulsivo.\n"
        "c) Negar qualquer escolha moral.\n"
        "Gabarito: A\n",
        pdfs["08_alternativas_irregulares"]
    )

    # 9. Horizontal inline options on the same line
    pdfs["09_alternativas_horizontais"] = folder / "09_alternativas_horizontais.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: MATEMÁTICA\n\n"
        "Questão 1. Qual é o valor de log10(1000) na base decimal?\n"
        "(A) 1    (B) 2    (C) 3    (D) 10    (E) 100\n"
        "Gabarito: C\n",
        pdfs["09_alternativas_horizontais"]
    )

    # 10. Embedded raster image inside question
    doc = fitz.open()
    pg = doc.new_page()
    img = Image.new("RGB", (120, 80), color=(2, 132, 199))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    pg.insert_image(fitz.Rect(45, 95, 165, 175), stream=buf.getvalue())
    pg.insert_textbox(fitz.Rect(45, 40, 550, 90), "DISCIPLINA: ARTE\nQuestão 1. Observe a composição cromática representada na figura abaixo e assinale o matiz predominante:", fontsize=10.5)
    pg.insert_textbox(fitz.Rect(45, 190, 550, 400), "(A) Vermelho carmim\n(B) Azul ciano institucional\n(C) Amarelo ocre\n(D) Verde musgo\n(E) Violeta escuro\nGabarito: B", fontsize=10.5)
    pdfs["10_questao_com_imagem"] = folder / "10_questao_com_imagem.pdf"
    doc.save(str(pdfs["10_questao_com_imagem"]))
    doc.close()

    # 11. Discursive open-ended question -> routed to pending_review
    pdfs["11_discursiva_aberta"] = folder / "11_discursiva_aberta.pdf"
    _make_pdf_single_page(
        "DISCIPLINA: PROJETO DE VIDA\n\n"
        "Questão 1. Elabore um texto reflexivo relacionando suas metas acadêmicas para o Ensino Médio com as oportunidades profissionais na sua região.",
        pdfs["11_discursiva_aberta"]
    )

    # 12. SEE/MG Technical Itinerary + Integrador detection
    pdfs["12_itinerario_tecnico_seemg"] = folder / "12_itinerario_tecnico_seemg.pdf"
    _make_pdf_single_page(
        "COMPONENTE: DESENVOLVIMENTO DE SISTEMAS\n\n"
        "Questão 01. Em bancos de dados SQL, qual cláusula filtra linhas antes do agrupamento?\n"
        "(A) WHERE\n(B) ORDER BY\n(C) LIMIT\n(D) JOIN\n(E) UNION\n"
        "Gabarito: A\n",
        pdfs["12_itinerario_tecnico_seemg"]
    )

    return pdfs


def run_12_pdf_parser_suite():
    extractor = PDFExtractionService()
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp)
        pdfs = build_12_test_pdfs(folder)
        assert len(pdfs) == 12

        timings = []
        print("=================================================================")
        print("SUÍTE DE 12 PDFs DE TESTE DO EXTRATOR TOLERANTE (FASE 5.4)")
        print("=================================================================")

        for name, path in pdfs.items():
            t0 = time.perf_counter()
            items = extractor.extract_document(str(path))
            dt_ms = (time.perf_counter() - t0) * 1000
            timings.append(dt_ms)
            print(f" -> {name}: {len(items)} questão(ões) em {dt_ms:.2f} ms")

            if name == "01_padrao_folha_gabarito":
                assert len(items) == 2
                assert items[0]["correct_answer"] == "B" and items[1]["correct_answer"] == "C"
                assert items[0]["confidence_level"] == "high" and items[0]["validation_status"] == "approved"

            elif name == "02_gabarito_inline":
                assert len(items) == 1
                assert items[0]["correct_answer"] == "C"
                assert "Gabarito" not in items[0]["statement"]
                assert all("Gabarito" not in v for v in items[0]["options_json"].values())

            elif name == "03_gabarito_ausente":
                assert len(items) == 1
                assert items[0]["correct_answer"] is None
                assert items[0]["validation_status"] == "pending_review"

            elif name == "04_duas_colunas_enem":
                assert len(items) == 2, f"Expected 2 questions in 2-col PDF, got {len(items)}"
                assert items[0]["correct_answer"] == "A" and items[1]["correct_answer"] == "B"
                assert "Cerrado" in items[0]["statement"] and "Ilha de calor" in items[1]["options_json"]["B"]

            elif name == "05_quebra_entre_paginas":
                assert len(items) == 2, f"Expected 2 stitched questions, got {len(items)}"
                assert set(items[0]["options_json"].keys()) == {"A", "B", "C", "D", "E"}, f"Broken options: {items[0]['options_json']}"
                assert items[0]["correct_answer"] == "C" and items[0]["spans_pages"] is True

            elif name == "06_algarismos_romanos":
                assert len(items) == 1
                assert items[0]["has_roman_numerals"] is True
                assert items[0]["correct_answer"] == "E"

            elif name == "07_formulas_matematicas":
                assert len(items) == 1
                assert items[0]["has_formula"] is True
                assert items[0]["options_json"]["B"] == "2 e 3"

            elif name == "08_alternativas_irregulares":
                assert len(items) == 1
                assert len(items[0]["options_json"]) == 3
                assert items[0]["confidence_score"] <= 80

            elif name == "09_alternativas_horizontais":
                assert len(items) == 1
                assert len(items[0]["options_json"]) == 5
                assert items[0]["correct_answer"] == "C"

            elif name == "10_questao_com_imagem":
                assert len(items) == 1
                assert items[0]["has_image"] is True
                assert items[0]["correct_answer"] == "B"

            elif name == "11_discursiva_aberta":
                assert len(items) == 1
                assert items[0]["question_type"] == "discursive"
                assert items[0]["validation_status"] == "pending_review"

            elif name == "12_itinerario_tecnico_seemg":
                assert len(items) == 1
                assert "Desenvolvimento de Sistemas" in items[0]["discipline"]
                assert items[0]["correct_answer"] == "A"

        avg_ms = sum(timings) / len(timings)
        print(f"\n ✓ TODOS OS 12 CENÁRIOS DE PDF APROVADOS! Tempo médio de parsing: {avg_ms:.2f} ms/PDF.")


if __name__ == "__main__":
    run_12_pdf_parser_suite()
