from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SAMPLE_DIR = Path(__file__).resolve().parent / "sample_files"
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("T", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=15)
body_style = ParagraphStyle("B", parent=styles["Normal"], fontName="Helvetica", fontSize=10, leading=14)

def create_pdf(filename: str, title: str, questions: list, answer_key: str):
    doc = SimpleDocTemplate(str(SAMPLE_DIR / filename), pagesize=A4, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    story = [
        Paragraph(title, title_style),
        Spacer(1, 12)
    ]
    for q in questions:
        story.append(Paragraph(q["header"], ParagraphStyle("QH", parent=body_style, fontName="Helvetica-Bold")))
        story.append(Paragraph(q["statement"], body_style))
        story.append(Spacer(1, 4))
        for opt in q["options"]:
            story.append(Paragraph(opt, body_style))
        story.append(Spacer(1, 8))
    
    if answer_key:
        story.append(Spacer(1, 10))
        story.append(Paragraph(answer_key, ParagraphStyle("AK", parent=body_style, fontName="Helvetica-Bold")))
        
    doc.build(story)
    print(f"Generated {filename}")

def generate_all_samples():
    # 1. Matemática
    create_pdf(
        "1_matematica.pdf",
        "AVALIAÇÃO DE MATEMÁTICA — 3º ANO DO ENSINO MÉDIO",
        [
            {
                "header": "Questão 01",
                "statement": "Determine o valor do determinante da matriz quadrada de ordem 2 cujos elementos são a11 = 3, a12 = 5, a21 = 2 e a22 = 4.",
                "options": [
                    "A) 2",
                    "B) 7",
                    "C) -2",
                    "D) 10",
                    "E) 12"
                ]
            },
            {
                "header": "Questão 02",
                "statement": "Uma progressão aritmética (PA) possui primeiro termo igual a 5 e razão igual a 3. Qual é o décimo termo dessa PA?",
                "options": [
                    "A) 28",
                    "B) 32",
                    "C) 35",
                    "D) 40",
                    "E) 45"
                ]
            }
        ],
        "GABARITO: 1 - A, 2 - B"
    )

    # 2. Português
    create_pdf(
        "2_portugues.pdf",
        "CADERNO DE QUESTÕES — LÍNGUA PORTUGUESA",
        [
            {
                "header": "Questão 01",
                "statement": "Assinale a alternativa em que todas as palavras estão grafadas em estrita conformidade com as regras do Novo Acordo Ortográfico:",
                "options": [
                    "A) Micro-ondas, autoestrada, contraproposta, anti-inflamatório.",
                    "B) Microondas, auto-estrada, contra-proposta, antiinflamatório.",
                    "C) Micro-ondas, auto-estrada, contraproposta, antiinflamatório.",
                    "D) Microondas, autoestrada, contraproposta, anti-inflamatório.",
                    "E) Micro-ondas, autoestrada, contra-proposta, antiinflamatório."
                ]
            },
            {
                "header": "Questão 02",
                "statement": "Na oração 'Embora estivesse exausto, continuou estudando para o simulado', a conjunção em destaque estabelece relação semântica de:",
                "options": [
                    "A) Causa.",
                    "B) Consequência.",
                    "C) Concessão.",
                    "D) Condição.",
                    "E) Proporção."
                ]
            }
        ],
        "GABARITO OFICIAL: 1 - A, 2 - C"
    )

    # 3. Biologia
    create_pdf(
        "3_biologia.pdf",
        "AVALIAÇÃO DE BIOLOGIA — GENÉTICA E CITOLOGIA",
        [
            {
                "header": "Questão 01",
                "statement": "No cruzamento entre dois indivíduos heterozigotos para um caráter monogênico com dominância completa (Aa x Aa), a proporção fenotípica esperada na descendência é de:",
                "options": [
                    "A) 1 : 2 : 1",
                    "B) 3 : 1",
                    "C) 9 : 3 : 3 : 1",
                    "D) 1 : 1",
                    "E) 4 : 0"
                ]
            },
            {
                "header": "Questão 02",
                "statement": "A organela celular responsável pela síntese de ATP por meio da respiração celular aeróbia é denominada:",
                "options": [
                    "A) Complexo golgiense.",
                    "B) Retículo endoplasmático liso.",
                    "C) Ribossomo.",
                    "D) Mitocôndria.",
                    "E) Lisossomo."
                ]
            }
        ],
        "RESPOSTAS: 1: B, 2: D"
    )

    # 4. História
    create_pdf(
        "4_historia.pdf",
        "PROVA DE HISTÓRIA — BRASIL REPÚBLICA",
        [
            {
                "header": "Questão 01",
                "statement": "O período da história republicana brasileira conhecido como 'República Velha' ou 'República Oligárquica' (1889-1930) caracterizou-se politicamente por:",
                "options": [
                    "A) Hegemonia do poder exercido alternadamente pelas elites de São Paulo e Minas Gerais na política do café com leite.",
                    "B) Amplo sufrágio universal com voto secreto estendido a analfabetos e mulheres.",
                    "C) Intervenção estatal contínua no fortalecimento dos direitos trabalhistas urbanos.",
                    "D) Predomínio absoluto do tenentismo nos primeiros escalões do Ministério da Fazenda.",
                    "E) Criação da Consolidação das Leis do Trabalho e industrialização de base."
                ]
            },
            {
                "header": "Questão 02",
                "statement": "A Revolução Constitucionalista de 1932 ocorrida no estado de São Paulo tinha como principal reivindicação:",
                "options": [
                    "A) A instauração de uma monarquia parlamentarista.",
                    "B) A promulgação de uma nova Constituição e o fim do governo provisório de Getúlio Vargas.",
                    "C) A abolição imediata da escravidão nas fazendas de café.",
                    "D) A aliança militar com o bloco dos Aliados na Primeira Guerra Mundial.",
                    "E) O cancelamento da dívida externa com os bancos ingleses."
                ]
            }
        ],
        "GABARITO: 1 - A, 2 - B"
    )

    # 5. Física
    create_pdf(
        "5_fisica.pdf",
        "PROVA DE FÍSICA — MECÂNICA E CINEMÁTICA",
        [
            {
                "header": "Questão 01",
                "statement": "Um veículo trafega em movimento retilíneo uniforme com velocidade constante de 72 km/h. Qual a distância, em metros, percorrida por esse móvel no intervalo de 10 segundos?",
                "options": [
                    "A) 100 m",
                    "B) 150 m",
                    "C) 200 m",
                    "D) 720 m",
                    "E) 2000 m"
                ]
            },
            {
                "header": "Questão 02",
                "statement": "De acordo com a Primeira Lei de Newton (Princípio da Inércia), um corpo em repouso ou em movimento retilíneo uniforme continuará nesse estado a menos que:",
                "options": [
                    "A) Exista atrito suficiente entre as superfícies de contato.",
                    "B) Uma força resultante não nula atue sobre ele.",
                    "C) Sua aceleração seja igual a zero.",
                    "D) Sua energia cinética permaneça inalterada.",
                    "E) A gravidade local seja anulada."
                ]
            }
        ],
        "GABARITO: 1 - C, 2 - B"
    )

if __name__ == "__main__":
    generate_all_samples()
