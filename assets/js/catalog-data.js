/**
 * Catálogo Curricular Lazy-Loaded SEE/MG (BNCC + Integradores + Itinerários Técnicos)
 * Carregado sob demanda com busca fuzzy tolerante a acentos e digitação parcial.
 */
(function(global) {
  'use strict';

  const SEEMG_DISCIPLINES = [
  "Língua Portuguesa",
  "Língua Inglesa",
  "Arte",
  "Educação Física",
  "Matemática",
  "Biologia",
  "Física",
  "Química",
  "História",
  "Geografia",
  "Filosofia",
  "Sociologia",
  "Projeto de Vida",
  "Estudos Orientados",
  "Práticas Experimentais",
  "Nivelamento em Língua Portuguesa",
  "Nivelamento em Matemática",
  "Projetos Integradores e de Corresponsabilidade Social (PICS)",
  "Cultura Digital e Fundamentos de IA",
  "Ferramentas para o Mundo do Trabalho",
  "Literatura Brasileira",
  "Redação e Produção Textual",
  "Língua Espanhola",
  "Arte (Artes Visuais, Música, Teatro, Dança)",
  "Eletivas",
  "Nivelamento (Língua Portuguesa e Matemática)",
  "Preparação para o Mundo do Trabalho / Pós-Médio",
  "Tecnologia e Inovação",
  "Educação Financeira e Empreendedorismo",
  "Iniciação Científica / Pesquisa e Intervenção",
  "Cultura Digital e Cidadania na Rede",
  "Linguagens — Produção Textual Avançada e Escrita Criativa",
  "Linguagens — Práticas de Linguagens Digitais e Mídias",
  "Linguagens — Comunicação, Mídias e Oratória",
  "Linguagens — Literatura Comparada e Contemporânea",
  "Linguagens — Teatro, Expressão Corporal e Artes Cênicas",
  "Matemática — Educação Financeira",
  "Matemática — Matemática Financeira e Estatística Aplicada",
  "Matemática — Modelagem Matemática e Resolução de Problemas",
  "Matemática — Geometria Espacial e Desenho Técnico",
  "Matemática — Lógica Matemática e Algoritmos",
  "Natureza — Biotecnologia e Genética Aplicada",
  "Natureza — Sustentabilidade e Gestão Ambiental",
  "Natureza — Astronomia e Astrofísica",
  "Natureza — Química Tecnológica e Farmacologia",
  "Natureza — Saúde Pública e Bioética",
  "Humanas — Geopolítica Contemporânea e Relações Internacionais",
  "Humanas — Direitos Humanos, Cidadania e Movimentos Sociais",
  "Humanas — Empreendedorismo Social",
  "Humanas — História de Minas Gerais, Patrimônio e Memória",
  "Humanas — Ética, Política e Sociedade Contemporânea",
  "Humanas — Antropologia e Estudos Culturais",
  "Técnico em Desenvolvimento de Sistemas (SEE/MG)",
  "Técnico em Informática (SEE/MG)",
  "Técnico em Informática para Internet (SEE/MG)",
  "Técnico em Redes de Computadores (SEE/MG)",
  "Técnico em Manutenção e Suporte em Informática (SEE/MG)",
  "Técnico em Programação de Jogos Digitais (SEE/MG)",
  "Técnico em Ciência de Dados e Inteligência Artificial (SEE/MG)",
  "Técnico em Robótica e Automação (SEE/MG)",
  "Técnico em Administração (SEE/MG)",
  "Técnico em Logística (SEE/MG)",
  "Técnico em Contabilidade (SEE/MG)",
  "Técnico em Recursos Humanos (SEE/MG)",
  "Técnico em Marketing e Marketing Digital (SEE/MG)",
  "Técnico em Comércio / Vendas (SEE/MG)",
  "Técnico em Finanças (SEE/MG)",
  "Técnico em Secretariado (SEE/MG)",
  "Técnico em Transações Imobiliárias (SEE/MG)",
  "Técnico em Serviços Jurídicos (SEE/MG)",
  "Técnico em Qualidade (SEE/MG)",
  "Técnico em Agropecuária (SEE/MG)",
  "Técnico em Agronegócio (SEE/MG)",
  "Técnico em Agricultura (SEE/MG)",
  "Técnico em Zootecnia (SEE/MG)",
  "Técnico em Agroecologia (SEE/MG)",
  "Técnico em Florestas (SEE/MG)",
  "Técnico em Meio Ambiente (SEE/MG)",
  "Técnico em Cafeicultura (SEE/MG)",
  "Técnico em Fruticultura (SEE/MG)",
  "Técnico em Piscicultura (SEE/MG)",
  "Técnico em Enfermagem (SEE/MG)",
  "Técnico em Análises Clínicas (SEE/MG)",
  "Técnico em Farmácia (SEE/MG)",
  "Técnico em Nutrição e Dietética (SEE/MG)",
  "Técnico em Segurança do Trabalho (SEE/MG)",
  "Técnico em Saúde Bucal (SEE/MG)",
  "Técnico em Radiologia (SEE/MG)",
  "Técnico em Agente Comunitário de Saúde (SEE/MG)",
  "Técnico em Gerência em Saúde (SEE/MG)",
  "Técnico em Estética (SEE/MG)",
  "Técnico em Eletrotécnica (SEE/MG)",
  "Técnico em Eletrônica (SEE/MG)",
  "Técnico em Mecânica (SEE/MG)",
  "Técnico em Mecatrônica (SEE/MG)",
  "Técnico em Automação Industrial (SEE/MG)",
  "Técnico em Química (SEE/MG)",
  "Técnico em Metalurgia (SEE/MG)",
  "Técnico em Eletromecânica (SEE/MG)",
  "Técnico em Soldagem (SEE/MG)",
  "Técnico em Refrigeração e Climatização (SEE/MG)",
  "Técnico em Manutenção Automotiva (SEE/MG)",
  "Técnico em Edificações (SEE/MG)",
  "Técnico em Mineração (SEE/MG)",
  "Técnico em Agrimensura (SEE/MG)",
  "Técnico em Estradas (SEE/MG)",
  "Técnico em Saneamento (SEE/MG)",
  "Técnico em Geoprocessamento (SEE/MG)",
  "Técnico em Design de Interiores (SEE/MG)",
  "Técnico em Alimentos (SEE/MG)",
  "Técnico em Agroindústria (SEE/MG)",
  "Técnico em Leite e Derivados / Laticínios (SEE/MG)",
  "Técnico em Panificação e Confeitaria (SEE/MG)",
  "Técnico em Vestuário e Moda (SEE/MG)",
  "Técnico em Têxtil (SEE/MG)",
  "Técnico em Móveis (SEE/MG)",
  "Técnico em Biocombustíveis (SEE/MG)",
  "Técnico em Açúcar e Álcool (SEE/MG)",
  "Técnico em Gastronomia / Cozinha (SEE/MG)",
  "Técnico em Hospedagem (SEE/MG)",
  "Técnico em Eventos (SEE/MG)",
  "Técnico em Guia de Turismo (SEE/MG)",
  "Técnico em Lazer (SEE/MG)",
  "Técnico em Comunicação Visual (SEE/MG)",
  "Técnico em Multimídia (SEE/MG)",
  "Técnico em Produção de Áudio e Vídeo (SEE/MG)",
  "Técnico em Design Gráfico (SEE/MG)",
  "Técnico em Secretaria Escolar (SEE/MG)",
  "Técnico em Biblioteconomia (SEE/MG)",
  "Técnico em Tradução e Interpretação de Libras (SEE/MG)",
  "Técnico em Multimeios Didáticos (SEE/MG)"
];

  const DEFAULT_SAMPLE_DOCS = [
      {
            "id": "doc-seemg-1",
            "filename": "01_língua_portuguesa.pdf",
            "discipline": "Língua Portuguesa",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 2,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-2",
            "filename": "02_literatura_brasileira.pdf",
            "discipline": "Literatura Brasileira",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-3",
            "filename": "03_redação_e_produção_textual.pdf",
            "discipline": "Redação e Produção Textual",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-4",
            "filename": "04_língua_inglesa.pdf",
            "discipline": "Língua Inglesa",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-5",
            "filename": "05_língua_espanhola.pdf",
            "discipline": "Língua Espanhola",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-6",
            "filename": "06_arte.pdf",
            "discipline": "Arte",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-7",
            "filename": "07_educação_física.pdf",
            "discipline": "Educação Física",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-8",
            "filename": "08_matemática.pdf",
            "discipline": "Matemática",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 2,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-9",
            "filename": "09_física.pdf",
            "discipline": "Física",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 2,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-10",
            "filename": "10_química.pdf",
            "discipline": "Química",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-11",
            "filename": "11_biologia.pdf",
            "discipline": "Biologia",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 2,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-12",
            "filename": "12_história.pdf",
            "discipline": "História",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-13",
            "filename": "13_geografia.pdf",
            "discipline": "Geografia",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-14",
            "filename": "14_filosofia.pdf",
            "discipline": "Filosofia",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-15",
            "filename": "15_sociologia.pdf",
            "discipline": "Sociologia",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-16",
            "filename": "16_projeto_de_vida.pdf",
            "discipline": "Projeto de Vida",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-17",
            "filename": "17_estudos_orientados.pdf",
            "discipline": "Estudos Orientados",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-18",
            "filename": "18_práticas_experimentais.pdf",
            "discipline": "Práticas Experimentais",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-19",
            "filename": "19_eletivas.pdf",
            "discipline": "Eletivas",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-20",
            "filename": "20_nivelamento_em_língua_portug.pdf",
            "discipline": "Nivelamento em Língua Portuguesa",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-21",
            "filename": "21_nivelamento_em_matemática.pdf",
            "discipline": "Nivelamento em Matemática",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-22",
            "filename": "22_projetos_integradores_e_de_c.pdf",
            "discipline": "Projetos Integradores e de Corresponsabilidade Social (PICS)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-23",
            "filename": "23_cultura_digital_e_fundamento.pdf",
            "discipline": "Cultura Digital e Fundamentos de IA",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-24",
            "filename": "24_ferramentas_para_o_mundo_do_.pdf",
            "discipline": "Ferramentas para o Mundo do Trabalho",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-25",
            "filename": "25_linguagens__produção_textual.pdf",
            "discipline": "Linguagens — Produção Textual Avançada e Escrita Criativa",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-26",
            "filename": "26_matemática__matemática_finan.pdf",
            "discipline": "Matemática — Matemática Financeira e Estatística Aplicada",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-27",
            "filename": "27_natureza__biotecnologia_e_ge.pdf",
            "discipline": "Natureza — Biotecnologia e Genética Aplicada",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-28",
            "filename": "28_humanas__história_de_minas_g.pdf",
            "discipline": "Humanas — História de Minas Gerais, Patrimônio e Memória",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-29",
            "filename": "29_técnico_em_desenvolvimento_d.pdf",
            "discipline": "Técnico em Desenvolvimento de Sistemas (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-30",
            "filename": "30_técnico_em_informática_see_m.pdf",
            "discipline": "Técnico em Informática (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-31",
            "filename": "31_técnico_em_informática_para_.pdf",
            "discipline": "Técnico em Informática para Internet (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-32",
            "filename": "32_técnico_em_redes_de_computad.pdf",
            "discipline": "Técnico em Redes de Computadores (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-33",
            "filename": "33_técnico_em_manutenção_e_supo.pdf",
            "discipline": "Técnico em Manutenção e Suporte em Informática (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-34",
            "filename": "34_técnico_em_programação_de_jo.pdf",
            "discipline": "Técnico em Programação de Jogos Digitais (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-35",
            "filename": "35_técnico_em_ciência_de_dados_.pdf",
            "discipline": "Técnico em Ciência de Dados e Inteligência Artificial (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-36",
            "filename": "36_técnico_em_robótica_e_automa.pdf",
            "discipline": "Técnico em Robótica e Automação (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-37",
            "filename": "37_técnico_em_administração_see.pdf",
            "discipline": "Técnico em Administração (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-38",
            "filename": "38_técnico_em_logística_see_mg.pdf",
            "discipline": "Técnico em Logística (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-39",
            "filename": "39_técnico_em_contabilidade_see.pdf",
            "discipline": "Técnico em Contabilidade (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-40",
            "filename": "40_técnico_em_recursos_humanos_.pdf",
            "discipline": "Técnico em Recursos Humanos (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-41",
            "filename": "41_técnico_em_marketing_e_marke.pdf",
            "discipline": "Técnico em Marketing e Marketing Digital (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-42",
            "filename": "42_técnico_em_finanças_see_mg.pdf",
            "discipline": "Técnico em Finanças (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-43",
            "filename": "43_técnico_em_secretariado_see_.pdf",
            "discipline": "Técnico em Secretariado (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-44",
            "filename": "44_técnico_em_serviços_jurídico.pdf",
            "discipline": "Técnico em Serviços Jurídicos (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-45",
            "filename": "45_técnico_em_qualidade_see_mg.pdf",
            "discipline": "Técnico em Qualidade (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-46",
            "filename": "46_técnico_em_agropecuária_see_.pdf",
            "discipline": "Técnico em Agropecuária (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-47",
            "filename": "47_técnico_em_agronegócio_see_m.pdf",
            "discipline": "Técnico em Agronegócio (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-48",
            "filename": "48_técnico_em_zootecnia_see_mg.pdf",
            "discipline": "Técnico em Zootecnia (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-49",
            "filename": "49_técnico_em_meio_ambiente_see.pdf",
            "discipline": "Técnico em Meio Ambiente (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-50",
            "filename": "50_técnico_em_cafeicultura_see_.pdf",
            "discipline": "Técnico em Cafeicultura (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-51",
            "filename": "51_técnico_em_enfermagem_see_mg.pdf",
            "discipline": "Técnico em Enfermagem (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-52",
            "filename": "52_técnico_em_farmácia_see_mg.pdf",
            "discipline": "Técnico em Farmácia (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-53",
            "filename": "53_técnico_em_nutrição_e_dietét.pdf",
            "discipline": "Técnico em Nutrição e Dietética (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-54",
            "filename": "54_técnico_em_segurança_do_trab.pdf",
            "discipline": "Técnico em Segurança do Trabalho (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-55",
            "filename": "55_técnico_em_eletrotécnica_see.pdf",
            "discipline": "Técnico em Eletrotécnica (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-56",
            "filename": "56_técnico_em_mecânica_see_mg.pdf",
            "discipline": "Técnico em Mecânica (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-57",
            "filename": "57_técnico_em_automação_industr.pdf",
            "discipline": "Técnico em Automação Industrial (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-58",
            "filename": "58_técnico_em_química_see_mg.pdf",
            "discipline": "Técnico em Química (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-59",
            "filename": "59_técnico_em_edificações_see_m.pdf",
            "discipline": "Técnico em Edificações (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-60",
            "filename": "60_técnico_em_mineração_see_mg.pdf",
            "discipline": "Técnico em Mineração (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-61",
            "filename": "61_técnico_em_alimentos_see_mg.pdf",
            "discipline": "Técnico em Alimentos (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-62",
            "filename": "62_técnico_em_leite_e_derivados.pdf",
            "discipline": "Técnico em Leite e Derivados / Laticínios (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-63",
            "filename": "63_técnico_em_vestuário_e_moda_.pdf",
            "discipline": "Técnico em Vestuário e Moda (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-64",
            "filename": "64_técnico_em_gastronomia___coz.pdf",
            "discipline": "Técnico em Gastronomia / Cozinha (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-65",
            "filename": "65_técnico_em_guia_de_turismo_s.pdf",
            "discipline": "Técnico em Guia de Turismo (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-66",
            "filename": "66_técnico_em_design_gráfico_se.pdf",
            "discipline": "Técnico em Design Gráfico (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-67",
            "filename": "67_técnico_em_secretaria_escola.pdf",
            "discipline": "Técnico em Secretaria Escolar (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      },
      {
            "id": "doc-seemg-68",
            "filename": "68_técnico_em_tradução_e_interp.pdf",
            "discipline": "Técnico em Tradução e Interpretação de Libras (SEE/MG)",
            "target_grade": "Ensino Médio / SEE-MG",
            "academic_period": "2026 - 1º Trimestre",
            "total_questions_found": 1,
            "status": "completed",
            "created_at": new Date().toISOString()
      }
];

  const DEFAULT_SAMPLE_QUESTIONS = [
      {
            "id": "q-por-1",
            "discipline": "Língua Portuguesa",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "Assinale a alternativa em que todas as palavras estão grafadas em estrita conformidade com o Novo Acordo Ortográfico:",
            "options_json": {
                  "A": "Micro-ondas, autoestrada, contraproposta, anti-inflamatório.",
                  "B": "Microondas, auto-estrada, contra-proposta, antiinflamatório.",
                  "C": "Micro-ondas, auto-estrada, contraproposta, antiinflamatório.",
                  "D": "Microondas, autoestrada, contraproposta, anti-inflamatório.",
                  "E": "Micro-ondas, autoestrada, contra-proposta, antiinflamatório."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "língua_portuguesa.pdf"
      },
      {
            "id": "q-por-2",
            "discipline": "Língua Portuguesa",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "Na oração 'Embora estivesse exausto, continuou estudando para o simulado', a conjunção em destaque estabelece relação semântica de:",
            "options_json": {
                  "A": "Causa.",
                  "B": "Consequência.",
                  "C": "Concessão.",
                  "D": "Condição.",
                  "E": "Proporção."
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "língua_portuguesa.pdf"
      },
      {
            "id": "q-lit-1",
            "discipline": "Literatura Brasileira",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "Qual movimento literário brasileiro do século XIX destacou-se pela análise psicológica, crítica social à burguesia e ironia refinada, tendo Machado de Assis como principal expoente?",
            "options_json": {
                  "A": "Barroco.",
                  "B": "Arcadismo.",
                  "C": "Romantismo.",
                  "D": "Realismo.",
                  "E": "Parnasianismo."
            },
            "correct_answer": "D",
            "validation_status": "approved",
            "source_filename": "literatura_brasileira.pdf"
      },
      {
            "id": "q-red-1",
            "discipline": "Redação e Produção Textual",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "Na estrutura do texto dissertativo-argumentativo padrão ENEM, a proposta de intervenção na conclusão deve apresentar obrigatoriamente:",
            "options_json": {
                  "A": "Apenas a repetição literal da tese da introdução.",
                  "B": "Agente, ação, meio/modo, finalidade e detalhamento, respeitando os direitos humanos.",
                  "C": "Citações em língua estrangeira sem tradução.",
                  "D": "Narrativa pessoal em primeira pessoa do singular.",
                  "E": "Lista de tópicos numerados sem conectivos."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "redação_e_produção_textual.pdf"
      },
      {
            "id": "q-ing-1",
            "discipline": "Língua Inglesa",
            "teacher_name": "Profª. Aline Costa",
            "question_type": "multiple_choice",
            "statement": "Choose the correct alternative that completes the sentence in the Present Perfect tense: 'She _____ in Belo Horizonte since 2020.'",
            "options_json": {
                  "A": "live",
                  "B": "lived",
                  "C": "has lived",
                  "D": "is living",
                  "E": "will live"
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "língua_inglesa.pdf"
      },
      {
            "id": "q-esp-1",
            "discipline": "Língua Espanhola",
            "teacher_name": "Prof. Diego Morales",
            "question_type": "multiple_choice",
            "statement": "En español, la palabra 'embarazada' es un falso cognado (heterosemántico) con respecto al portugués y significa:",
            "options_json": {
                  "A": "Envergonhada.",
                  "B": "Confusa.",
                  "C": "Grávida.",
                  "D": "Ocupada.",
                  "E": "Atrasada."
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "língua_espanhola.pdf"
      },
      {
            "id": "q-art-1",
            "discipline": "Arte",
            "teacher_name": "Profª. Clara Nogueira",
            "question_type": "multiple_choice",
            "statement": "Em Minas Gerais, o estilo artístico que floresceu no século XVIII nas cidades históricas como Ouro Preto e Congonhas, tendo Aleijadinho e Mestre Ataíde como expoentes, é o:",
            "options_json": {
                  "A": "Cubismo.",
                  "B": "Barroco Mineiro.",
                  "C": "Surrealismo.",
                  "D": "Expressionismo Abstrato.",
                  "E": "Pop Art."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "arte.pdf"
      },
      {
            "id": "q-edf-1",
            "discipline": "Educação Física",
            "teacher_name": "Prof. Rafael Oliveira",
            "question_type": "multiple_choice",
            "statement": "Durante a prática regular de exercícios aeróbicos de intensidade moderada, qual adaptação fisiológica ocorre no sistema cardiovascular?",
            "options_json": {
                  "A": "Redução da capacidade pulmonar vital.",
                  "B": "Aumento da eficiência cardíaca e melhora do condicionamento cardiorrespiratório.",
                  "C": "Diminuição permanente do fluxo sanguíneo muscular.",
                  "D": "Perda de elasticidade arterial.",
                  "E": "Bloqueio do metabolismo oxidativo."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "educação_física.pdf"
      },
      {
            "id": "q-mat-1",
            "discipline": "Matemática",
            "teacher_name": "Prof. Carlos Silva",
            "question_type": "multiple_choice",
            "statement": "Determine o valor do determinante da matriz quadrada de ordem 2 cujos elementos são a11 = 3, a12 = 5, a21 = 2 e a22 = 4.",
            "options_json": {
                  "A": "2",
                  "B": "7",
                  "C": "-2",
                  "D": "10",
                  "E": "12"
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "matemática.pdf"
      },
      {
            "id": "q-mat-2",
            "discipline": "Matemática",
            "teacher_name": "Prof. Carlos Silva",
            "question_type": "multiple_choice",
            "statement": "Uma progressão aritmética (PA) possui primeiro termo igual a 5 e razão igual a 3. Qual é o décimo termo dessa PA?",
            "options_json": {
                  "A": "28",
                  "B": "32",
                  "C": "35",
                  "D": "40",
                  "E": "45"
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "matemática.pdf"
      },
      {
            "id": "q-fis-1",
            "discipline": "Física",
            "teacher_name": "Prof. Marcos Dias",
            "question_type": "multiple_choice",
            "statement": "Um veículo trafega em movimento retilíneo uniforme com velocidade constante de 72 km/h. Qual a distância, em metros, percorrida em 10 segundos?",
            "options_json": {
                  "A": "100 m",
                  "B": "150 m",
                  "C": "200 m",
                  "D": "720 m",
                  "E": "2000 m"
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "física.pdf"
      },
      {
            "id": "q-fis-2",
            "discipline": "Física",
            "teacher_name": "Prof. Marcos Dias",
            "question_type": "multiple_choice",
            "statement": "De acordo com a Primeira Lei de Newton (Princípio da Inércia), um corpo em repouso ou em MRU continuará nesse estado a menos que:",
            "options_json": {
                  "A": "Exista atrito suficiente.",
                  "B": "Uma força resultante não nula atue sobre ele.",
                  "C": "Sua aceleração seja zero.",
                  "D": "Sua energia cinética permaneça constante.",
                  "E": "A gravidade seja anulada."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "física.pdf"
      },
      {
            "id": "q-qui-1",
            "discipline": "Química",
            "teacher_name": "Profª. Beatriz Rocha",
            "question_type": "multiple_choice",
            "statement": "Qual é o pH de uma solução aquosa neutra a 25 °C, como a água pura?",
            "options_json": {
                  "A": "0",
                  "B": "3",
                  "C": "7",
                  "D": "10",
                  "E": "14"
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "química.pdf"
      },
      {
            "id": "q-bio-1",
            "discipline": "Biologia",
            "teacher_name": "Profª. Carla Souza",
            "question_type": "multiple_choice",
            "statement": "No cruzamento entre dois indivíduos heterozigotos para dominância completa (Aa x Aa), a proporção fenotípica esperada é:",
            "options_json": {
                  "A": "1 : 2 : 1",
                  "B": "3 : 1",
                  "C": "9 : 3 : 3 : 1",
                  "D": "1 : 1",
                  "E": "4 : 0"
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "biologia.pdf"
      },
      {
            "id": "q-bio-2",
            "discipline": "Biologia",
            "teacher_name": "Profª. Carla Souza",
            "question_type": "multiple_choice",
            "statement": "A organela celular responsável pela síntese de ATP por meio da respiração celular aeróbia é denominada:",
            "options_json": {
                  "A": "Complexo golgiense.",
                  "B": "Retículo endoplasmático liso.",
                  "C": "Ribossomo.",
                  "D": "Mitocôndria.",
                  "E": "Lisossomo."
            },
            "correct_answer": "D",
            "validation_status": "approved",
            "source_filename": "biologia.pdf"
      },
      {
            "id": "q-his-1",
            "discipline": "História",
            "teacher_name": "Prof. André Martins",
            "question_type": "multiple_choice",
            "statement": "A Inconfidência Mineira (1789), ocorrida em Vila Rica (atual Ouro Preto), foi motivada principalmente por:",
            "options_json": {
                  "A": "Apoio irrestrito à cobrança da derrama pela Coroa Portuguesa.",
                  "B": "Insatisfação com a alta carga tributária colonial e inspiração nos ideais iluministas.",
                  "C": "Reivindicação pela volta do regime feudal europeu.",
                  "D": "Conflito fronteiriço com a Argentina.",
                  "E": "Proibição do cultivo de café em São Paulo."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "história.pdf"
      },
      {
            "id": "q-geo-1",
            "discipline": "Geografia",
            "teacher_name": "Prof. Lucas Ferreira",
            "question_type": "multiple_choice",
            "statement": "Qual bioma brasileiro, predominante em grande parte do território de Minas Gerais, caracteriza-se por vegetação savânica, árvores de troncos retorcidos e duas estações bem definidas?",
            "options_json": {
                  "A": "Amazônia.",
                  "B": "Caatinga.",
                  "C": "Cerrado.",
                  "D": "Pampa.",
                  "E": "Pantanal."
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "geografia.pdf"
      },
      {
            "id": "q-fil-1",
            "discipline": "Filosofia",
            "teacher_name": "Prof. Gustavo Ribeiro",
            "question_type": "multiple_choice",
            "statement": "Na filosofia de René Descartes, a famosa máxima 'Penso, logo existo' (Cogito, ergo sum) representa:",
            "options_json": {
                  "A": "O abandono total da razão em favor dos sentidos.",
                  "B": "A primeira certeza indubitável alcançada por meio da dúvida metódica.",
                  "C": "A defesa do empirismo radical baseado apenas na experiência sensorial.",
                  "D": "A negação da existência do pensamento humano.",
                  "E": "Um dogma teológico medieval."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "filosofia.pdf"
      },
      {
            "id": "q-soc-1",
            "discipline": "Sociologia",
            "teacher_name": "Profª. Fernanda Lima",
            "question_type": "multiple_choice",
            "statement": "Para Émile Durkheim, o objeto de estudo próprio da Sociologia que exerce coerção exterior sobre os indivíduos é denominado:",
            "options_json": {
                  "A": "Ação social subjetiva.",
                  "B": "Luta de classes.",
                  "C": "Fato social.",
                  "D": "Mais-valia absoluta.",
                  "E": "Tipo ideal."
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "sociologia.pdf"
      },
      {
            "id": "q-pv-1",
            "discipline": "Projeto de Vida",
            "teacher_name": "Profª. Patrícia Alves",
            "question_type": "multiple_choice",
            "statement": "No componente Projeto de Vida da rede SEE/MG, o planejamento pessoal, acadêmico e profissional do estudante baseia-se fundamentalmente em:",
            "options_json": {
                  "A": "Autoconhecimento, definição de metas realistas e protagonismo juvenil.",
                  "B": "Escolha aleatória de profissões sem reflexão sobre interesses.",
                  "C": "Exclusão do convívio comunitário e familiar.",
                  "D": "Memorização mecânica de fórmulas sem aplicação prática.",
                  "E": "Substituição das disciplinas da Base Nacional Comum."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "projeto_de_vida.pdf"
      },
      {
            "id": "q-eo-1",
            "discipline": "Estudos Orientados",
            "teacher_name": "Profª. Patrícia Alves",
            "question_type": "multiple_choice",
            "statement": "Qual técnica de estudo é recomendada nos Estudos Orientados para melhorar a retenção de conteúdos a longo prazo?",
            "options_json": {
                  "A": "Estudar apenas na véspera da prova sem pausas.",
                  "B": "Revisão espaçada, mapas mentais e resolução ativa de exercícios.",
                  "C": "Copiar textos inteiros sem compreender o significado.",
                  "D": "Evitar anotações e resumos próprios.",
                  "E": "Ler em ambientes com distrações constantes."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "estudos_orientados.pdf"
      },
      {
            "id": "q-pe-1",
            "discipline": "Práticas Experimentais",
            "teacher_name": "Profª. Beatriz Rocha",
            "question_type": "multiple_choice",
            "statement": "Ao conduzir uma prática em laboratório escolar de Ciências, qual medida de segurança é indispensável?",
            "options_json": {
                  "A": "Provar reagentes desconhecidos para identificar o sabor.",
                  "B": "Utilizar EPIs adequados (jaleco, óculos) e seguir o roteiro experimental sob supervisão.",
                  "C": "Descartar substâncias químicas diretamente no lixo comum.",
                  "D": "Aquecer frascos fechados hermeticamente.",
                  "E": "Correr ou consumir alimentos na bancada."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "práticas_experimentais.pdf"
      },
      {
            "id": "q-ele-1",
            "discipline": "Eletivas",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "As disciplinas Eletivas no Ensino Médio em Tempo Integral (EMTI) da SEE/MG têm como objetivo principal:",
            "options_json": {
                  "A": "Aprofundar e diversificar experiências de aprendizagem conectadas aos interesses dos estudantes.",
                  "B": "Repetir exatamente o mesmo conteúdo das aulas regulares sem inovação.",
                  "C": "Eliminar a interdisciplinaridade na escola.",
                  "D": "Restringir o acesso dos alunos à cultura e tecnologia.",
                  "E": "Substituir a avaliação escolar oficial."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "eletivas.pdf"
      },
      {
            "id": "q-niv-lp-1",
            "discipline": "Nivelamento em Língua Portuguesa",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "No componente Nivelamento em Língua Portuguesa da SEE-MG, qual estratégia é fundamental para a recomposição das aprendizagens em leitura e interpretação textual?",
            "options_json": {
                  "A": "Identificar ideia central, inferências, elementos de coesão e gênero textual antes de responder.",
                  "B": "Ler apenas o título ignorando o corpo do texto.",
                  "C": "Memorizar listas isoladas de palavras fora de contexto.",
                  "D": "Evitar a produção escrita e a reescrita orientada.",
                  "E": "Substituir a leitura por respostas aleatórias."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "nivelamento_em_língua_portug.pdf"
      },
      {
            "id": "q-niv-mat-1",
            "discipline": "Nivelamento em Matemática",
            "teacher_name": "Prof. Carlos Silva",
            "question_type": "multiple_choice",
            "statement": "No Nivelamento em Matemática da SEE-MG, para resolver corretamente a expressão numérica 4 + 3 × (8 − 2) ÷ 2, deve-se respeitar a ordem de operações obtendo:",
            "options_json": {
                  "A": "10",
                  "B": "13",
                  "C": "21",
                  "D": "7",
                  "E": "18"
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "nivelamento_em_matemática.pdf"
      },
      {
            "id": "q-pics-1",
            "discipline": "Projetos Integradores e de Corresponsabilidade Social (PICS)",
            "teacher_name": "Profª. Patrícia Alves",
            "question_type": "multiple_choice",
            "statement": "Os Projetos Integradores e de Corresponsabilidade Social (PICS) da SEE-MG têm como finalidade central:",
            "options_json": {
                  "A": "Articular conhecimentos de diferentes áreas para propor soluções solidárias a desafios reais da comunidade escolar.",
                  "B": "Isolar as disciplinas sem diálogo entre professores.",
                  "C": "Substituir a participação estudantil por aulas exclusivamente expositivas.",
                  "D": "Focar apenas em exercícios individuais descontextualizados.",
                  "E": "Restringir projetos sociais ao ambiente externo sem vínculo pedagógico."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "projetos_integradores_e_de_c.pdf"
      },
      {
            "id": "q-cdia-1",
            "discipline": "Cultura Digital e Fundamentos de IA",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "No componente Cultura Digital e Fundamentos de IA (SEE-MG), o uso ético e crítico da Inteligência Artificial Generativa na escola pressupõe:",
            "options_json": {
                  "A": "Verificar fontes, combater vieses algorítmicos, respeitar a LGPD e usar a IA como apoio à aprendizagem autoral.",
                  "B": "Copiar respostas geradas automaticamente sem revisão crítica.",
                  "C": "Compartilhar dados pessoais sensíveis de alunos em plataformas abertas.",
                  "D": "Acreditar que sistemas de IA nunca cometem erros factuais.",
                  "E": "Abandonar o pensamento computacional e o senso crítico."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "cultura_digital_e_fundamento.pdf"
      },
      {
            "id": "q-fmt-1",
            "discipline": "Ferramentas para o Mundo do Trabalho",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Em Ferramentas para o Mundo do Trabalho (SEE-MG), qual conjunto de competências socioemocionais e técnicas é mais valorizado na inserção profissional do jovem?",
            "options_json": {
                  "A": "Comunicação assertiva, trabalho em equipe, ética profissional, domínio digital e elaboração de currículo.",
                  "B": "Isolamento interpessoal e recusa de feedback.",
                  "C": "Desconhecimento de direitos trabalhistas e normas de segurança.",
                  "D": "Falta de pontualidade e planejamento.",
                  "E": "Ausência de qualificação contínua."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "ferramentas_para_o_mundo_do_.pdf"
      },
      {
            "id": "q-ap-lin-1",
            "discipline": "Linguagens — Produção Textual Avançada e Escrita Criativa",
            "teacher_name": "Profª. Mariana Santos",
            "question_type": "multiple_choice",
            "statement": "A intertextualidade em produções textuais avançadas ocorre quando:",
            "options_json": {
                  "A": "Um texto estabelece diálogo explícito ou implícito com outros textos ou obras culturais.",
                  "B": "O autor evita qualquer referência cultural ou histórica.",
                  "C": "O texto não possui coesão nem coerência.",
                  "D": "Utiliza-se apenas linguagem matemática.",
                  "E": "Há repetição involuntária de palavras."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "linguagens__produção_textual.pdf"
      },
      {
            "id": "q-ap-mat-1",
            "discipline": "Matemática — Matemática Financeira e Estatística Aplicada",
            "teacher_name": "Prof. Carlos Silva",
            "question_type": "multiple_choice",
            "statement": "Em um conjunto de dados com valores extremos (outliers) muito discrepantes, qual medida de tendência central é menos distorcida?",
            "options_json": {
                  "A": "Média aritmética simples.",
                  "B": "Mediana.",
                  "C": "Amplitude total.",
                  "D": "Soma simples.",
                  "E": "Produto dos extremos."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "matemática__matemática_finan.pdf"
      },
      {
            "id": "q-ap-nat-1",
            "discipline": "Natureza — Biotecnologia e Genética Aplicada",
            "teacher_name": "Profª. Carla Souza",
            "question_type": "multiple_choice",
            "statement": "A técnica CRISPR-Cas9 revolucionou a biotecnologia moderna por permitir:",
            "options_json": {
                  "A": "A edição precisa de sequências específicas de DNA em organismos vivos.",
                  "B": "A geração de energia nuclear em usinas solares.",
                  "C": "A fabricação de cimento Portland.",
                  "D": "A comunicação via satélite de rádio.",
                  "E": "A destilação fracionada do petróleo."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "natureza__biotecnologia_e_ge.pdf"
      },
      {
            "id": "q-ap-hum-1",
            "discipline": "Humanas — História de Minas Gerais, Patrimônio e Memória",
            "teacher_name": "Prof. André Martins",
            "question_type": "multiple_choice",
            "statement": "O Conjunto Moderno da Pampulha, em Belo Horizonte, reconhecido pela UNESCO como Patrimônio Cultural da Humanidade, foi projetado pelo arquiteto:",
            "options_json": {
                  "A": "Aleijadinho.",
                  "B": "Oscar Niemeyer.",
                  "C": "Lúcio Costa.",
                  "D": "Ruy Ohtake.",
                  "E": "Paulo Mendes da Rocha."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "humanas__história_de_minas_g.pdf"
      },
      {
            "id": "q-tec-ds-1",
            "discipline": "Técnico em Desenvolvimento de Sistemas (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "No desenvolvimento de bancos de dados relacionais, qual comando SQL é utilizado para consultar e recuperar registros de uma tabela?",
            "options_json": {
                  "A": "SELECT",
                  "B": "DELETE",
                  "C": "DROP",
                  "D": "INSERT",
                  "E": "ALTER"
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_desenvolvimento_d.pdf"
      },
      {
            "id": "q-tec-inf-1",
            "discipline": "Técnico em Informática (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "Na arquitetura de computadores, qual memória é volátil e armazena temporariamente os dados e programas em execução pela CPU?",
            "options_json": {
                  "A": "Memória ROM.",
                  "B": "Disco SSD.",
                  "C": "Memória RAM.",
                  "D": "Pendrive USB.",
                  "E": "Cartão SD."
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "técnico_em_informática_see_m.pdf"
      },
      {
            "id": "q-tec-web-1",
            "discipline": "Técnico em Informática para Internet (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "No desenvolvimento web front-end, qual tecnologia é responsável especificamente pela estilização visual e layout responsivo das páginas?",
            "options_json": {
                  "A": "HTML5.",
                  "B": "CSS3.",
                  "C": "SQL.",
                  "D": "FTP.",
                  "E": "SMTP."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "técnico_em_informática_para_.pdf"
      },
      {
            "id": "q-tec-red-1",
            "discipline": "Técnico em Redes de Computadores (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "Qual protocolo da pilha TCP/IP é responsável por traduzir nomes de domínio (ex: educacao.mg.gov.br) em endereços IP numéricos?",
            "options_json": {
                  "A": "DHCP.",
                  "B": "DNS.",
                  "C": "FTP.",
                  "D": "SSH.",
                  "E": "ICMP."
            },
            "correct_answer": "B",
            "validation_status": "approved",
            "source_filename": "técnico_em_redes_de_computad.pdf"
      },
      {
            "id": "q-tec-msi-1",
            "discipline": "Técnico em Manutenção e Suporte em Informática (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "Ao realizar manutenção preventiva em um computador com superaquecimento do processador, qual procedimento técnico é o mais indicado?",
            "options_json": {
                  "A": "Limpeza do cooler/dissipador e substituição adequada da pasta térmica.",
                  "B": "Remoção definitiva da ventoinha.",
                  "C": "Lavagem da placa-mãe com água corrente.",
                  "D": "Desligamento do cabo de força com o sistema em uso.",
                  "E": "Aumento da voltagem da fonte para o dobro."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_manutenção_e_supo.pdf"
      },
      {
            "id": "q-tec-jog-1",
            "discipline": "Técnico em Programação de Jogos Digitais (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "No desenvolvimento de jogos digitais, o ciclo contínuo que processa entradas do jogador, atualiza a física/lógica e renderiza quadros na tela chama-se:",
            "options_json": {
                  "A": "Game Loop.",
                  "B": "Firewall.",
                  "C": "Compiler Error.",
                  "D": "SQL Injection.",
                  "E": "BIOS Setup."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_programação_de_jo.pdf"
      },
      {
            "id": "q-tec-ia-1",
            "discipline": "Técnico em Ciência de Dados e Inteligência Artificial (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "Em Aprendizado de Máquina (Machine Learning), quando um modelo aprende a partir de exemplos rotulados (entradas e respostas conhecidas), trata-se de aprendizado:",
            "options_json": {
                  "A": "Supervisionado.",
                  "B": "Não supervisionado.",
                  "C": "Aleatório.",
                  "D": "Manual estático.",
                  "E": "Desconectado."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_ciência_de_dados_.pdf"
      },
      {
            "id": "q-tec-rob-1",
            "discipline": "Técnico em Robótica e Automação (SEE/MG)",
            "teacher_name": "Prof. Henrique Lima",
            "question_type": "multiple_choice",
            "statement": "Em projetos de robótica com microcontroladores (como Arduino), qual sensor mede distâncias por emissão e reflexão de ondas ultrassônicas?",
            "options_json": {
                  "A": "Sensor ultrassônico (HC-SR04).",
                  "B": "Servomotor de passo.",
                  "C": "Potenciômetro linear.",
                  "D": "Ponte H.",
                  "E": "Fusível térmico."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_robótica_e_automa.pdf"
      },
      {
            "id": "q-tec-adm-1",
            "discipline": "Técnico em Administração (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Na matriz SWOT (FOFA), ferramenta clássica de planejamento estratégico organizacional, os fatores internos controláveis pela empresa são:",
            "options_json": {
                  "A": "Forças e Fraquezas.",
                  "B": "Oportunidades e Ameaças.",
                  "C": "Inflação e Juros.",
                  "D": "Concorrentes e Legislação.",
                  "E": "Clima e Câmbio."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_administração_see.pdf"
      },
      {
            "id": "q-tec-log-1",
            "discipline": "Técnico em Logística (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Na gestão de estoques, o método PEPS (ou FIFO) determina que:",
            "options_json": {
                  "A": "O primeiro item a entrar no estoque deve ser o primeiro a sair.",
                  "B": "O último item a entrar deve sair primeiro.",
                  "C": "Os produtos vencidos devem ser mantidos na frente.",
                  "D": "O estoque não precisa de inventário.",
                  "E": "Apenas produtos caros são controlados."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_logística_see_mg.pdf"
      },
      {
            "id": "q-tec-con-1",
            "discipline": "Técnico em Contabilidade (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Na equação fundamental do patrimônio contábil, o Patrimônio Líquido (PL) corresponde a:",
            "options_json": {
                  "A": "Ativo menos Passivo Exigível.",
                  "B": "Ativo mais Passivo.",
                  "C": "Receitas multiplicadas por Despesas.",
                  "D": "Apenas o saldo em caixa.",
                  "E": "Total de impostos anuais."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_contabilidade_see.pdf"
      },
      {
            "id": "q-tec-rh-1",
            "discipline": "Técnico em Recursos Humanos (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "No subsistema de Gestão de Pessoas, o processo voltado a atrair candidatos qualificados para as vagas disponíveis na organização é chamado de:",
            "options_json": {
                  "A": "Recrutamento.",
                  "B": "Demissão.",
                  "C": "Auditoria fiscal.",
                  "D": "Logística reversa.",
                  "E": "Faturamento."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_recursos_humanos_.pdf"
      },
      {
            "id": "q-tec-mkt-1",
            "discipline": "Técnico em Marketing e Marketing Digital (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Os 4 Ps clássicos do Mix de Marketing (Composto Mercadológico) definidos por Jerome McCarthy e popularizados por Philip Kotler são:",
            "options_json": {
                  "A": "Produto, Preço, Praça e Promoção.",
                  "B": "Lucro, Custo, Imposto e Frete.",
                  "C": "Venda, Compra, Troca e Estoque.",
                  "D": "Site, Blog, E-mail e Vídeo.",
                  "E": "Marca, Cor, Fonte e Papel."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_marketing_e_marke.pdf"
      },
      {
            "id": "q-tec-fin-1",
            "discipline": "Técnico em Finanças (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "O demonstrativo financeiro que registra todas as entradas e saídas efetivas de recursos monetários de uma empresa em determinado período é o:",
            "options_json": {
                  "A": "Fluxo de Caixa.",
                  "B": "Organograma Funcional.",
                  "C": "Manual de Conduta.",
                  "D": "Contrato Social.",
                  "E": "Mapa de Risco."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_finanças_see_mg.pdf"
      },
      {
            "id": "q-tec-sec-1",
            "discipline": "Técnico em Secretariado (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "Qual documento oficial registra de forma fiel e resumida as deliberações e ocorrências de uma reunião institucional?",
            "options_json": {
                  "A": "Ata.",
                  "B": "Nota Fiscal.",
                  "C": "Boleto Bancário.",
                  "D": "Curriculum Vitae.",
                  "E": "Alvará."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_secretariado_see_.pdf"
      },
      {
            "id": "q-tec-jur-1",
            "discipline": "Técnico em Serviços Jurídicos (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "No ordenamento jurídico brasileiro, qual é a lei máxima que organiza o Estado e garante os direitos e garantias fundamentais?",
            "options_json": {
                  "A": "Constituição Federal de 1988.",
                  "B": "Regimento Interno Escolar.",
                  "C": "Portaria Municipal.",
                  "D": "Contrato de Locação.",
                  "E": "Estatuto de Condomínio."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_serviços_jurídico.pdf"
      },
      {
            "id": "q-tec-qua-1",
            "discipline": "Técnico em Qualidade (SEE/MG)",
            "teacher_name": "Profª. Juliana Prado",
            "question_type": "multiple_choice",
            "statement": "O Ciclo PDCA, amplamente utilizado na melhoria contínua de processos e gestão da qualidade, corresponde às etapas:",
            "options_json": {
                  "A": "Plan (Planejar), Do (Fazer), Check (Checar) e Act (Agir).",
                  "B": "Pagar, Dividir, Cobrar e Arquivar.",
                  "C": "Produzir, Descartar, Comprar e Anunciar.",
                  "D": "Pesquisar, Desenhar, Cortar e Acabar.",
                  "E": "Postar, Deletar, Compartilhar e Acessar."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_qualidade_see_mg.pdf"
      },
      {
            "id": "q-tec-agr-1",
            "discipline": "Técnico em Agropecuária (SEE/MG)",
            "teacher_name": "Prof. Eduardo Campos",
            "question_type": "multiple_choice",
            "statement": "A prática conservacionista de correção da acidez do solo agrícola mediante aplicação de calcário é conhecida como:",
            "options_json": {
                  "A": "Calagem.",
                  "B": "Desmatamento.",
                  "C": "Queimada controlada.",
                  "D": "Salinização.",
                  "E": "Compactação."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_agropecuária_see_.pdf"
      },
      {
            "id": "q-tec-agn-1",
            "discipline": "Técnico em Agronegócio (SEE/MG)",
            "teacher_name": "Prof. Eduardo Campos",
            "question_type": "multiple_choice",
            "statement": "Na cadeia produtiva do agronegócio, o segmento 'antes da porteira' compreende:",
            "options_json": {
                  "A": "Fornecimento de insumos, sementes, fertilizantes, máquinas e crédito rural.",
                  "B": "Apenas o varejo em supermercados urbanos.",
                  "C": "Exclusivamente o consumo doméstico.",
                  "D": "O descarte de embalagens pelo consumidor final.",
                  "E": "A exportação portuária apenas."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_agronegócio_see_m.pdf"
      },
      {
            "id": "q-tec-zoo-1",
            "discipline": "Técnico em Zootecnia (SEE/MG)",
            "teacher_name": "Prof. Eduardo Campos",
            "question_type": "multiple_choice",
            "statement": "Na pecuária leiteira — atividade de grande relevância em Minas Gerais — o bem-estar animal contribui diretamente para:",
            "options_json": {
                  "A": "Maior produtividade, melhor qualidade do leite e redução de doenças no rebanho.",
                  "B": "Queda na qualidade nutricional do leite.",
                  "C": "Aumento do estresse térmico nos bovinos.",
                  "D": "Redução da longevidade do rebanho.",
                  "E": "Eliminação da necessidade de vacinação."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_zootecnia_see_mg.pdf"
      },
      {
            "id": "q-tec-mae-1",
            "discipline": "Técnico em Meio Ambiente (SEE/MG)",
            "teacher_name": "Prof. Eduardo Campos",
            "question_type": "multiple_choice",
            "statement": "A política dos 3 Rs da sustentabilidade para gestão de resíduos sólidos refere-se a:",
            "options_json": {
                  "A": "Reduzir, Reutilizar e Reciclar.",
                  "B": "Remover, Romper e Rejeitar.",
                  "C": "Reservar, Reter e Represar.",
                  "D": "Riscar, Rasgar e Reembolsar.",
                  "E": "Recuar, Retardar e Repetir."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_meio_ambiente_see.pdf"
      },
      {
            "id": "q-tec-caf-1",
            "discipline": "Técnico em Cafeicultura (SEE/MG)",
            "teacher_name": "Prof. Eduardo Campos",
            "question_type": "multiple_choice",
            "statement": "Minas Gerais é o maior produtor nacional de café. Qual espécie botânica domina a cafeicultura mineira pela alta qualidade de bebida?",
            "options_json": {
                  "A": "Coffea arabica (Café Arábica).",
                  "B": "Zea mays.",
                  "C": "Glycine max.",
                  "D": "Saccharum officinarum.",
                  "E": "Eucalyptus grandis."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_cafeicultura_see_.pdf"
      },
      {
            "id": "q-tec-enf-1",
            "discipline": "Técnico em Enfermagem (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "Na aferição dos sinais vitais de um adulto saudável em repouso, quais parâmetros são avaliados rotineiramente?",
            "options_json": {
                  "A": "Pressão arterial, frequência cardíaca, frequência respiratória e temperatura corporal.",
                  "B": "Apenas altura e peso mensal.",
                  "C": "Exclusivamente acuidade visual.",
                  "D": "Apenas tipo sanguíneo.",
                  "E": "Somente histórico escolar."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_enfermagem_see_mg.pdf"
      },
      {
            "id": "q-tec-far-1",
            "discipline": "Técnico em Farmácia (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "Nas Boas Práticas de Armazenamento de medicamentos em farmácias, quais fatores ambientais devem ser monitorados diariamente?",
            "options_json": {
                  "A": "Temperatura e umidade relativa do ar.",
                  "B": "Cor das paredes e música ambiente.",
                  "C": "Apenas a luminosidade externa da rua.",
                  "D": "Velocidade do vento na calçada.",
                  "E": "Número de visitantes diários."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_farmácia_see_mg.pdf"
      },
      {
            "id": "q-tec-nut-1",
            "discipline": "Técnico em Nutrição e Dietética (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "Segundo o Guia Alimentar para a População Brasileira, a base de uma alimentação saudável deve priorizar:",
            "options_json": {
                  "A": "Alimentos in natura ou minimamente processados.",
                  "B": "Alimentos ultraprocessados ricos em sódio e açúcares.",
                  "C": "Suplementos industriais em substituição a todas as refeições.",
                  "D": "Jejum prolongado sem orientação.",
                  "E": "Exclusivamente gorduras trans."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_nutrição_e_dietét.pdf"
      },
      {
            "id": "q-tec-seg-1",
            "discipline": "Técnico em Segurança do Trabalho (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "De acordo com a Norma Regulamentadora NR-6, o Equipamento de Proteção Individual (EPI) deve ser fornecido pelo empregador:",
            "options_json": {
                  "A": "Gratuitamente, adequado ao risco e em perfeito estado de conservação e funcionamento.",
                  "B": "Mediante desconto integral no salário do trabalhador.",
                  "C": "Apenas após a ocorrência de um acidente grave.",
                  "D": "Sem necessidade de Certificado de Aprovação (CA).",
                  "E": "Somente para diretores administrativos."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_segurança_do_trab.pdf"
      },
      {
            "id": "q-tec-elt-1",
            "discipline": "Técnico em Eletrotécnica (SEE/MG)",
            "teacher_name": "Prof. Sérgio Mendes",
            "question_type": "multiple_choice",
            "statement": "Pela Primeira Lei de Ohm, em um resistor ôhmico de 20 Ω percorrido por uma corrente elétrica de 2 A, a diferença de potencial (tensão) aplicada é:",
            "options_json": {
                  "A": "10 V",
                  "B": "22 V",
                  "C": "40 V",
                  "D": "80 V",
                  "E": "100 V"
            },
            "correct_answer": "C",
            "validation_status": "approved",
            "source_filename": "técnico_em_eletrotécnica_see.pdf"
      },
      {
            "id": "q-tec-mec-1",
            "discipline": "Técnico em Mecânica (SEE/MG)",
            "teacher_name": "Prof. Sérgio Mendes",
            "question_type": "multiple_choice",
            "statement": "Qual instrumento de metrologia industrial permite medir dimensões externas, internas e profundidades com precisão de centésimos de milímetro?",
            "options_json": {
                  "A": "Paquímetro.",
                  "B": "Trena de costura.",
                  "C": "Prumo de pedreiro.",
                  "D": "Termômetro clínico.",
                  "E": "Bússola magnética."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_mecânica_see_mg.pdf"
      },
      {
            "id": "q-tec-aut-1",
            "discipline": "Técnico em Automação Industrial (SEE/MG)",
            "teacher_name": "Prof. Sérgio Mendes",
            "question_type": "multiple_choice",
            "statement": "Na automação de linhas industriais, o equipamento eletrônico programável projetado para controlar máquinas e processos em tempo real é o:",
            "options_json": {
                  "A": "CLP (Controlador Lógico Programável).",
                  "B": "Projetor multimídia.",
                  "C": "Impressora térmica.",
                  "D": "Roteador doméstico.",
                  "E": "Estabilizador simples."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_automação_industr.pdf"
      },
      {
            "id": "q-tec-qui-1",
            "discipline": "Técnico em Química (SEE/MG)",
            "teacher_name": "Profª. Beatriz Rocha",
            "question_type": "multiple_choice",
            "statement": "Em uma titulação ácido-base em laboratório, qual vidraria graduada com torneira é utilizada para dispensar com precisão o volume da solução titulante?",
            "options_json": {
                  "A": "Bureta.",
                  "B": "Béquer comum.",
                  "C": "Vidro de relógio.",
                  "D": "Cadinho de porcelana.",
                  "E": "Tubo de ensaio."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_química_see_mg.pdf"
      },
      {
            "id": "q-tec-edi-1",
            "discipline": "Técnico em Edificações (SEE/MG)",
            "teacher_name": "Prof. Sérgio Mendes",
            "question_type": "multiple_choice",
            "statement": "Na representação gráfica de projetos arquitetônicos, a vista resultante de um corte horizontal a cerca de 1,50 m do piso acabado chama-se:",
            "options_json": {
                  "A": "Planta Baixa.",
                  "B": "Fachada Principal.",
                  "C": "Perspectiva Isométrica.",
                  "D": "Detalhe de Cobertura.",
                  "E": "Corte Longitudinal."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_edificações_see_m.pdf"
      },
      {
            "id": "q-tec-min-1",
            "discipline": "Técnico em Mineração (SEE/MG)",
            "teacher_name": "Prof. Sérgio Mendes",
            "question_type": "multiple_choice",
            "statement": "Em Minas Gerais, estado líder na produção mineral brasileira, qual minério metálico é o principal responsável pela pauta de exportação mineral?",
            "options_json": {
                  "A": "Minério de Ferro.",
                  "B": "Sal-gema marinho.",
                  "C": "Gesso agrícola.",
                  "D": "Petróleo offshore.",
                  "E": "Carvão mineral sulista."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_mineração_see_mg.pdf"
      },
      {
            "id": "q-tec-ali-1",
            "discipline": "Técnico em Alimentos (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "O processo térmico de pasteurização aplicado ao leite tem como objetivo sanitário principal:",
            "options_json": {
                  "A": "Eliminar micro-organismos patogênicos preservando ao máximo as características nutricionais.",
                  "B": "Congelar o produto a -80 °C.",
                  "C": "Adicionar corantes artificiais.",
                  "D": "Retirar toda a proteína do leite.",
                  "E": "Aumentar a acidez lática."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_alimentos_see_mg.pdf"
      },
      {
            "id": "q-tec-lat-1",
            "discipline": "Técnico em Leite e Derivados / Laticínios (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "Na fabricação do tradicional Queijo Minas Artesanal, a etapa responsável pela coagulação da caseína do leite utiliza:",
            "options_json": {
                  "A": "Coalho (enzimas coagulantes) e fermento lático natural (pingo).",
                  "B": "Ácido sulfúrico concentrado.",
                  "C": "Bicarbonato de sódio em excesso.",
                  "D": "Destilação a vácuo.",
                  "E": "Fervura por 6 horas contínuas."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_leite_e_derivados.pdf"
      },
      {
            "id": "q-tec-ves-1",
            "discipline": "Técnico em Vestuário e Moda (SEE/MG)",
            "teacher_name": "Profª. Clara Nogueira",
            "question_type": "multiple_choice",
            "statement": "Na indústria de confecção do vestuário, a etapa que transforma o desenho técnico em peças-molde dimensionadas por grade de tamanhos chama-se:",
            "options_json": {
                  "A": "Modelagem e gradação.",
                  "B": "Expedição.",
                  "C": "Tingimento de solo.",
                  "D": "Fundição.",
                  "E": "Refino."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_vestuário_e_moda_.pdf"
      },
      {
            "id": "q-tec-gas-1",
            "discipline": "Técnico em Gastronomia / Cozinha (SEE/MG)",
            "teacher_name": "Profª. Renata Medeiros",
            "question_type": "multiple_choice",
            "statement": "Na gastronomia profissional, a expressão francesa 'Mise en place' refere-se a:",
            "options_json": {
                  "A": "Organização, medição e preparo prévio de todos os ingredientes e utensílios antes do cozimento.",
                  "B": "Limpeza externa do restaurante após o expediente.",
                  "C": "Fechamento do caixa financeiro.",
                  "D": "Apenas a decoração de sobremesas.",
                  "E": "Entrega por aplicativo."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_gastronomia___coz.pdf"
      },
      {
            "id": "q-tec-tur-1",
            "discipline": "Técnico em Guia de Turismo (SEE/MG)",
            "teacher_name": "Prof. Lucas Ferreira",
            "question_type": "multiple_choice",
            "statement": "Em Minas Gerais, o Circuito do Ouro e a Estrada Real destacam-se nacionalmente principalmente pelo turismo:",
            "options_json": {
                  "A": "Histórico, cultural, gastronômico e ecológico.",
                  "B": "Exclusivamente praiano e marítimo.",
                  "C": "De esportes na neve.",
                  "D": "De deserto árido.",
                  "E": "Apenas industrial pesado."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_guia_de_turismo_s.pdf"
      },
      {
            "id": "q-tec-des-1",
            "discipline": "Técnico em Design Gráfico (SEE/MG)",
            "teacher_name": "Profª. Clara Nogueira",
            "question_type": "multiple_choice",
            "statement": "Na produção gráfica destinada à impressão profissional em gráfica (offset/digital), qual sistema de cores deve ser utilizado?",
            "options_json": {
                  "A": "CMYK (Ciano, Magenta, Amarelo e Preto).",
                  "B": "RGB exclusivo de monitores.",
                  "C": "Apenas escala infravermelha.",
                  "D": "Hexadecimal web sem conversão.",
                  "E": "Código Morse."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_design_gráfico_se.pdf"
      },
      {
            "id": "q-tec-sce-1",
            "discipline": "Técnico em Secretaria Escolar (SEE/MG)",
            "teacher_name": "Profª. Patrícia Alves",
            "question_type": "multiple_choice",
            "statement": "Qual documento oficial da escrituração escolar comprova a trajetória acadêmica completa do estudante para fins de transferência ou conclusão do Ensino Médio?",
            "options_json": {
                  "A": "Histórico Escolar.",
                  "B": "Bilhete de autorização de passeio.",
                  "C": "Cardápio da merenda.",
                  "D": "Escala de recreio.",
                  "E": "Folha de ponto docente."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_secretaria_escola.pdf"
      },
      {
            "id": "q-tec-lib-1",
            "discipline": "Técnico em Tradução e Interpretação de Libras (SEE/MG)",
            "teacher_name": "Profª. Patrícia Alves",
            "question_type": "multiple_choice",
            "statement": "Reconhecida oficialmente pela Lei nº 10.436/2002 no Brasil, a Libras (Língua Brasileira de Sinais) possui modalidade linguística:",
            "options_json": {
                  "A": "Visual-espacial, com gramática própria e estrutura independente do português.",
                  "B": "Oral-auditiva idêntica ao português falado.",
                  "C": "Universal e igual em todos os países do mundo.",
                  "D": "Apenas mímica sem regras gramaticais.",
                  "E": "Baseada somente em leitura labial."
            },
            "correct_answer": "A",
            "validation_status": "approved",
            "source_filename": "técnico_em_tradução_e_interp.pdf"
      }
];

  function normalizeText(str) {
    return (str || '')
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .trim();
  }

  /**
   * Busca fuzzy rápida (subsequência + substring + prefixo) sobre as 135+ disciplinas SEE/MG.
   * Retorna no máximo `limit` resultados ordenados por relevância sem travar o DOM.
   */
  function fuzzySearchDisciplines(query, limit = 25) {
    if (!query || !query.trim()) {
      return SEEMG_DISCIPLINES.slice(0, limit);
    }
    const q = normalizeText(query);
    const tokens = q.split(/\s+/).filter(Boolean);
    const scored = [];

    for (let i = 0; i < SEEMG_DISCIPLINES.length; i++) {
      const item = SEEMG_DISCIPLINES[i];
      const norm = normalizeText(item);
      let score = 0;

      if (norm === q) {
        score = 1000;
      } else if (norm.startsWith(q)) {
        score = 800 - norm.length;
      } else if (norm.includes(q)) {
        score = 600 - norm.indexOf(q);
      } else {
        // Multi-token & fuzzy subsequence matching
        let allTokensMatch = true;
        for (const tk of tokens) {
          if (!norm.includes(tk)) {
            allTokensMatch = false;
            break;
          }
        }
        if (allTokensMatch) {
          score = 450;
        } else {
          let qi = 0;
          for (let ci = 0; ci < norm.length && qi < q.length; ci++) {
            if (norm[ci] === q[qi]) qi++;
          }
          if (qi === q.length) {
            score = 200 - (norm.length - q.length);
          }
        }
      }

      if (score > 0) {
        scored.push({ item, score });
      }
    }

    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, limit).map(s => s.item);
  }

  /**
   * Conecta inputs com list="disciplines-suggestions" para renderizar apenas top N opções sob demanda.
   */
  function bindLazyDisciplineInputs() {
    const datalist = document.getElementById('disciplines-suggestions');
    if (!datalist) return;

    const renderOptions = (query) => {
      const matches = fuzzySearchDisciplines(query, query ? 30 : 25);
      datalist.innerHTML = matches.map(d => `<option value="${d.replace(/"/g, '&quot;')}">`).join('');
    };

    // Initial lightweight seed (25 items instead of 140+)
    renderOptions('');

    document.querySelectorAll('input[list="disciplines-suggestions"]').forEach(inp => {
      if (inp.dataset.fuzzyBound) return;
      inp.dataset.fuzzyBound = '1';
      inp.addEventListener('focus', () => renderOptions(inp.value));
      inp.addEventListener('input', () => renderOptions(inp.value));
    });
  }

  global.GIACatalog = {
    CATALOG_VERSION: 'seemg_idb_v4',
    SEEMG_DISCIPLINES,
    DEFAULT_SAMPLE_DOCS,
    DEFAULT_SAMPLE_QUESTIONS,
    fuzzySearchDisciplines,
    bindLazyDisciplineInputs,
    normalizeText
  };
})(window);
