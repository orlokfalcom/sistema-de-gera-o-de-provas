# GERADOR INTELIGENTE DE AVALIAÇÕES DO ENSINO MÉDIO
> *“Uma avaliação. Todas as disciplinas. Inteligência a serviço da educação.”*

---

## 1. Visão Geral da Solução

Plataforma Web moderna, responsiva e instalável como **PWA (Progressive Web App)**, desenvolvida para resolver o desafio de consolidação de provas escolares do Ensino Médio. O sistema recebe múltiplos arquivos PDF elaborados por diferentes professores, extrai enunciados, alternativas (A-E), questões discursivas, imagens e gabaritos, e reúne todo o material em **UMA ÚNICA PROVA MULTIDISCIPLINAR INSTITUCIONAL**.

### Regras Pedagógicas Inegociáveis Implementadas
1. **Prova Única Multidisciplinar**: Não gera provas separadas por matéria; consolida todas as disciplinas recebidas em um único caderno com numeração sequencial contínua (01 a N).
2. **Preservação da Autoria**: Utiliza estritamente as questões e respostas originais dos professores.
3. **IA Segura & Anti-Alucinação**: O sistema **nunca** inventa questões, alternativas ou respostas. Gabaritos ausentes são marcados como `PENDENTE DE CONFERÊNCIA` para conferência humana.
4. **Gabarito Oficial ao Final**: Posicionado obrigatoriamente na última página no formato tabular oficial `QUESTÃO | DISCIPLINA | RESPOSTA`.
5. **Sigilo Garantido**: A versão destinada aos estudantes é gerada 100% isenta de gabarito.
6. **Exportação Dual**: Disponível em **PDF tipográfico oficial** (ReportLab) e **DOCX editável** (python-docx).

---

## 2. Tecnologias Utilizadas

- **Backend**: Python 3.15+ com **FastAPI** e **Uvicorn**.
- **Processamento de PDFs**: **PyMuPDF (fitz)** para segmentação de blocos, coordenadas e extração de imagens de diagramas.
- **Banco de Dados**: **SQLAlchemy 2.0 ORM** (compatível com SQLite para desenvolvimento local e PostgreSQL para produção).
- **Geradores de Documentos**: **ReportLab** (PDF de alta fidelidade) e **python-docx** (DOCX editável).
- **Integração Google Workspace**: Google OAuth 2.0, Google Drive (pastas por ano/período), Google Sheets (relatórios e logs de gabarito) e template Google Apps Script (`.gs`).
- **Frontend & PWA**: HTML5, **Tailwind CSS**, design responsivo (desktop, tablet, mobile), manifesto PWA (`manifest.json`) e Service Worker (`sw.js`).

---

## 3. Estrutura de Diretórios

```text
mini/
├── backend/
│   ├── app/
│   │   ├── config.py              # Variáveis de ambiente, diretórios e chaves
│   │   ├── database.py            # Sessão do SQLAlchemy
│   │   ├── init_db.py             # Criação de tabelas e seed de usuários
│   │   ├── main.py                # Aplicação FastAPI e montagem de rotas
│   │   ├── models.py              # Modelos ORM (User, Document, Question, Exam, ExamItem)
│   │   ├── schemas.py             # Schemas Pydantic
│   │   ├── routers/
│   │   │   ├── auth.py            # Autenticação Google e RBAC
│   │   │   ├── documents.py       # Upload de múltiplos PDFs e histórico
│   │   │   ├── questions.py       # Banco de questões e conferência
│   │   │   ├── exams.py           # Montagem e download da prova única
│   │   │   ├── google_sync.py     # Sincronização Drive, Sheets e Apps Script
│   │   │   └── dashboard.py       # Métricas e relatórios
│   │   └── services/
│   │       ├── pdf_extractor.py   # Extração PyMuPDF, segmentação e parsing de gabarito
│   │       ├── deduplication.py   # Similaridade de enunciados e duplicatas
│   │       ├── exam_builder.py    # Algoritmo de junção e numeração contínua
│   │       ├── pdf_generator.py   # Renderizador ReportLab com paginação 'X de Y'
│   │       ├── docx_generator.py  # Renderizador python-docx
│   │       └── google_service.py  # Clientes Google Workspace
│   ├── static/                    # Frontend PWA (index.html, manifest.json, sw.js)
│   └── storage/                   # Armazenamento persistente de uploads, mídias e provas
├── tests/
│   ├── generate_sample_pdfs.py    # Gerador dos 5 PDFs sintéticos de disciplinas distintas
│   ├── test_end_to_end_acceptance.py # Teste de aceitação ponta a ponta (10 critérios)
│   └── sample_files/              # Arquivos de Matemática, Português, Biologia, História e Física
├── run_server.py                  # Ponto de inicialização do servidor
└── README.md
```

---

## 4. Como Executar a Aplicação

### 4.1 Iniciar o Servidor Web e PWA
```bash
python run_server.py
```
Acesse a aplicação no navegador em:
- **Plataforma Web / PWA**: `http://127.0.0.1:8000`
- **Documentação Interativa Swagger**: `http://127.0.0.1:8000/docs`

### 4.2 Instalação como Aplicativo PWA
Ao abrir no Google Chrome, Edge ou em navegadores mobile (Android/iOS):
1. Clique no botão **"Instalar App"** na barra lateral ou no ícone de instalação do navegador.
2. O aplicativo será adicionado à área de trabalho ou à tela inicial do celular/tablet, funcionando com suporte a cache offline via Service Worker.

---

## 5. Como Executar os Testes Automatizados de Aceitação

Para validar todo o fluxo de ponta a ponta com as **5 disciplinas distintas** (Matemática, Língua Portuguesa, Biologia, História e Física):

```bash
python tests/test_end_to_end_acceptance.py
```

### Resultados Validados pelo Teste:
- [x] **Critério 1 & 2**: Todos os 5 PDFs recebidos e 10 questões identificadas.
- [x] **Critério 3 & 4**: 5 disciplinas e todos os gabaritos associados com precisão.
- [x] **Critério 5 & 6**: Prova única montada com numeração contínua de 01 a 10.
- [x] **Critério 7 & 8**: Nenhuma questão omitida; Gabarito Oficial ao final da prova.
- [x] **Critério 9**: Versão do estudante 100% isenta de gabarito (sigilo preservado).
- [x] **Critério 10**: Geração validada de **PDF do Aluno**, **PDF Completo**, **PDF de Gabarito Separado** e **DOCX Editável**.

---

## 6. Configuração das Credenciais do Google Workspace

Para conectar o Google Workspace em ambiente de produção:
1. Obtenha as credenciais OAuth 2.0 no [Google Cloud Console](https://console.cloud.google.com/).
2. Configure as seguintes variáveis de ambiente:
```bash
GOOGLE_CLIENT_ID="seu-client-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="seu-client-secret"
GOOGLE_REDIRECT_URI="http://localhost:8000/api/auth/google/callback"
```
3. O sistema possui modo de fallback que opera localmente sem necessidade de credenciais externas para testes de avaliação e homologação imediata.
