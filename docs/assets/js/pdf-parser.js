/**
 * Módulo Lazy-Loaded de Extração Tolerante de PDFs, Cache SHA-256 e Pontuação de Confiança (Fases 2 e 3).
 * Recursos:
 *  - Execução em Web Worker (não bloqueia UI) com barra de progresso real e botão Cancelar
 *  - Cache por hash SHA-256 do arquivo em IndexedDB (evita reprocessar o mesmo PDF)
 *  - Parser tolerante: alternativas A-E, proposições romanas (I, II, III, IV), fórmulas matemáticas,
 *    gabarito inline ou em folha separada, PDFs de 2 colunas e questões quebradas entre páginas
 *  - Classificação automática de confiança (high / medium / low) -> 'low' vai direto para Conferência Pedagógica
 */
(function(global) {
  'use strict';

  let workerInstance = null;
  let currentJob = null;

  async function computeFileSHA256(arrayBuffer) {
    const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function getOrCreateWorker() {
    if (workerInstance) return workerInstance;
    try {
      workerInstance = new Worker('./assets/js/pdf-worker.js');
      return workerInstance;
    } catch (_) {
      // Fallback inline Blob Worker if origin restricts relative Worker URLs (e.g., file://)
      const blobCode = `
        importScripts('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js');
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
        let cancelled = {};
        self.onmessage = async (e) => {
          const m = e.data || {};
          if (m.type === 'cancel') { cancelled[m.jobId] = true; return; }
          if (m.type === 'extract') {
            const t0 = performance.now();
            try {
              const pdf = await pdfjsLib.getDocument({ data: m.buffer }).promise;
              const pages = [];
              for (let i = 1; i <= pdf.numPages; i++) {
                if (cancelled[m.jobId]) { self.postMessage({ type: 'cancelled', jobId: m.jobId }); return; }
                const p = await pdf.getPage(i);
                const tc = await p.getTextContent();
                pages.push({ pageNumber: i, text: tc.items.map(x => x.str).join(' '), isTwoColumn: false, hasImage: false });
                self.postMessage({ type: 'progress', jobId: m.jobId, page: i, totalPages: pdf.numPages, pct: Math.round((i / pdf.numPages) * 100) });
              }
              self.postMessage({ type: 'done', jobId: m.jobId, totalPages: pdf.numPages, elapsedMs: Math.round(performance.now() - t0), pages });
            } catch (err) {
              self.postMessage({ type: 'error', jobId: m.jobId, error: String(err) });
            }
          }
        };
      `;
      const blob = new Blob([blobCode], { type: 'application/javascript' });
      workerInstance = new Worker(URL.createObjectURL(blob));
      return workerInstance;
    }
  }

  function cancelActiveExtraction() {
    if (currentJob && workerInstance) {
      workerInstance.postMessage({ type: 'cancel', jobId: currentJob.jobId });
      currentJob.reject(new Error('CANCELLED_BY_USER'));
      currentJob = null;
      return true;
    }
    return false;
  }

  function extractPDFPagesInWorker(arrayBuffer, onProgress) {
    const worker = getOrCreateWorker();
    const jobId = 'job-' + Date.now() + '-' + Math.random().toString(36).slice(2, 7);
    // Clone buffer before transfer so caller can still hash or inspect if needed
    const cloned = arrayBuffer.slice(0);

    return new Promise((resolve, reject) => {
      currentJob = { jobId, reject };

      const handler = (e) => {
        const data = e.data || {};
        if (data.jobId !== jobId) return;

        if (data.type === 'progress') {
          if (typeof onProgress === 'function') onProgress(data);
        } else if (data.type === 'done') {
          worker.removeEventListener('message', handler);
          currentJob = null;
          resolve(data);
        } else if (data.type === 'cancelled') {
          worker.removeEventListener('message', handler);
          currentJob = null;
          reject(new Error('CANCELLED_BY_USER'));
        } else if (data.type === 'error') {
          worker.removeEventListener('message', handler);
          currentJob = null;
          reject(new Error(data.error || 'Erro ao ler PDF'));
        }
      };

      worker.addEventListener('message', handler);
      worker.postMessage({ type: 'extract', jobId, buffer: cloned }, [cloned]);
    });
  }

  /**
   * Detecta disciplina a partir do texto usando o catálogo completo SEE/MG.
   */
  function detectDisciplineFromText(text, hint) {
    if (hint && hint.trim()) return hint.trim();
    const catalog = (global.GIACatalog && global.GIACatalog.SEEMG_DISCIPLINES) || [];
    const normText = (text || '').toLowerCase();

    for (const disc of catalog) {
      const cleanName = disc.replace(/\s*\(SEE\/MG\)/i, '').trim().toLowerCase();
      if (cleanName.length >= 4 && normText.includes(cleanName)) {
        return disc;
      }
    }
    return 'Multidisciplinar';
  }

  /**
   * Extrai mapa de gabarito tanto em folha separada ao final quanto padrões tabelados (ex: "01-A 02-C" ou "1. B").
   */
  function extractAnswerKeySheet(fullText) {
    const map = {};
    if (!fullText) return map;

    // Prioritize explicit GABARITO / RESPOSTAS section at the end of the document if present
    const gabSectionMatch = fullText.match(/(?:gabarito(?:\s+oficial)?|folha\s+de\s+respostas?|chaves?\s+de\s+respostas?|respostas?\s*[:\-]\s*(?:quest[ãa]o\s*)?\d)[\s\S]{0,4000}$/i);
    const targetZone = gabSectionMatch ? gabSectionMatch[0] : '';

    const pairRegex = /(?:quest[ãa]o\s*|item\s*|\b)0*(\d{1,3})\s*(?:[\.\-\)\:\=\|]|–|—)\s*([A-Ea-e])\b/g;
    let m;
    while ((m = pairRegex.exec(targetZone)) !== null) {
      const num = parseInt(m[1], 10);
      const letter = m[2].toUpperCase();
      if (num >= 1) {
        map[num] = letter;
      }
    }
    return map;
  }

  /**
   * Detecta fórmulas matemáticas / científicas e proposições em algarismos romanos (I, II, III, IV).
   */
  function analyzeSpecialFeatures(block) {
    const hasRomanNumerals = /(?:^|\n|\s)(?:I|II|III|IV|V)\s*[\.\-\)]\s+\S/.test(block);
    const hasMathFormula = /[√∑∏∫∆Δπ±≤≥≠≈∞²³⁴]|(?:\b(?:sen|cos|tg|log|lim)\b)|(?:\d+\s*[\+\-\*\/\^]\s*\d+\s*=)|\\[a-zA-Z]+\{/.test(block);
    return { hasRomanNumerals, hasMathFormula };
  }

  /**
   * Parser tolerante multi-página com pontuação de confiança (alta / média / baixa).
   */
  function parsePagesToQuestions(pages, options = {}) {
    const { defaultDiscipline = '', teacherName = 'Docente', filename = 'documento.pdf' } = options;

    // Stitch pages seamlessly while tracking page origin per character offset
    const pageOffsets = [];
    let cursor = 0;
    const stitchedParts = [];

    for (const p of pages) {
      const cleanPageText = (p.text || '')
        .replace(/\r\n/g, '\n')
        // Remove isolated page headers/footers like "Página 2 de 5" so broken questions across pages stitch cleanly
        .replace(/^\s*p[áa]gina\s+\d+(?:\s+de\s+\d+)?\s*$/gim, '')
        .trim();
      pageOffsets.push({ start: cursor, end: cursor + cleanPageText.length, pageNumber: p.pageNumber, hasImage: !!p.hasImage, isTwoColumn: !!p.isTwoColumn });
      stitchedParts.push(cleanPageText);
      cursor += cleanPageText.length + 2;
    }

    const fullText = stitchedParts.join('\n\n');
    const detectedDisc = detectDisciplineFromText(fullText, defaultDiscipline);
    const answerKeySheet = extractAnswerKeySheet(fullText);

    // Remove trailing answer key section from question segmentation zone
    const bodyWithoutAnswerSheet = fullText.replace(/\n\s*(?:gabarito(?:\s+oficial)?|folha\s+de\s+respostas?|chave\s+de\s+respostas?)\b[\s\S]*$/i, '').trim();

    // Tolerant question header matcher: "QUESTÃO 01", "Questão 1 -", "Item 2.", "01)", "1." at start of line
    const qHeaderRegex = /(?:^|\n)\s*(?:(?:quest[ãa]o|item|q\.?)\s*0*(\d{1,3})\b(?:\s*[\.\-\)\:])?|0*(\d{1,2})\s*[\.\-\)]\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ"\(\[']))/gi;
    const headers = [];
    let hm;
    while ((hm = qHeaderRegex.exec(bodyWithoutAnswerSheet)) !== null) {
      const qNum = parseInt(hm[1] || hm[2], 10);
      headers.push({ index: hm.index, num: qNum, headerRaw: hm[0] });
    }

    const findPageInfo = (charIdx) => {
      for (const po of pageOffsets) {
        if (charIdx >= po.start && charIdx <= po.end + 2) return po;
      }
      return pageOffsets[0] || { pageNumber: 1, hasImage: false, isTwoColumn: false };
    };

    const parsedQuestions = [];

    if (headers.length > 0) {
      for (let i = 0; i < headers.length; i++) {
        const start = headers[i].index;
        const end = i + 1 < headers.length ? headers[i + 1].index : bodyWithoutAnswerSheet.length;
        let rawBlock = bodyWithoutAnswerSheet.slice(start, end).trim();

        const startPage = findPageInfo(start);
        const endPage = findPageInfo(end - 1);
        const spansMultiplePages = startPage.pageNumber !== endPage.pageNumber;

        // Check inline answer inside block (e.g. "Gabarito: D" or "Resposta correta: B")
        let inlineAns = null;
        const inlineMatch = rawBlock.match(/(?:gabarito|resposta(?:\s+correta)?|alternativa\s+correta)\s*[\:\-\=]?\s*\(?([A-Ea-e])\)?\b/i);
        if (inlineMatch) {
          inlineAns = inlineMatch[1].toUpperCase();
          rawBlock = rawBlock.replace(inlineMatch[0], '').trim();
        }

        // Remove question header prefix
        let contentBlock = rawBlock.replace(/^\s*(?:(?:quest[ãa]o|item|q\.?)\s*\d+\s*[\.\-\)\:]?|\d+\s*[\.\-\)])\s*/i, '').trim();

        // Tolerant options matcher: (A), A), A., a), [A], A -
        const optRegex = /(?:^|\n|\s{2,})(?:\(\s*([A-Ea-e])\s*\)|\[\s*([A-Ea-e])\s*\]|([A-Ea-e])\s*[\)\.\-–])\s+/g;
        const optPositions = [];
        let om;
        while ((om = optRegex.exec(contentBlock)) !== null) {
          const letter = (om[1] || om[2] || om[3]).toUpperCase();
          optPositions.push({ index: om.index, matchLen: om[0].length, letter });
        }

        // Deduplicate & validate monotonic option sequence (e.g. A, B, C, D, E)
        const validOpts = [];
        const seenLetters = new Set();
        for (const op of optPositions) {
          if (!seenLetters.has(op.letter)) {
            seenLetters.add(op.letter);
            validOpts.push(op);
          }
        }

        const optionsMap = {};
        let statement = contentBlock;
        if (validOpts.length >= 2) {
          statement = contentBlock.slice(0, validOpts[0].index).trim();
          for (let j = 0; j < validOpts.length; j++) {
            const oStart = validOpts[j].index + validOpts[j].matchLen;
            const oEnd = j + 1 < validOpts.length ? validOpts[j + 1].index : contentBlock.length;
            optionsMap[validOpts[j].letter] = contentBlock.slice(oStart, oEnd).replace(/\s+/g, ' ').trim();
          }
        }

        const features = analyzeSpecialFeatures(contentBlock);
        const qNum = headers[i].num;
        const finalAnswer = inlineAns || answerKeySheet[qNum] || null;
        const optCount = Object.keys(optionsMap).length;
        const qType = optCount >= 2 ? 'multiple_choice' : 'discursive';

        // Confidence scoring (0..100) + pedagogical triage
        let confidenceScore = 100;
        const reasons = [];

        if (statement.length < 18) {
          confidenceScore -= 35;
          reasons.push('Enunciado muito curto ou fragmentado');
        }
        if (qType === 'multiple_choice' && optCount < 4) {
          confidenceScore -= 25;
          reasons.push(`Apenas ${optCount} alternativas detectadas (esperado 4 ou 5)`);
        }
        if (qType === 'discursive') {
          confidenceScore -= 20;
          reasons.push('Questão discursiva ou alternativas fora do padrão A–E');
        }
        if (!finalAnswer) {
          confidenceScore -= 30;
          reasons.push('Gabarito ausente no documento');
        }
        if (spansMultiplePages) {
          confidenceScore -= 10;
          reasons.push(`Questão reconstruída entre as páginas ${startPage.pageNumber} e ${endPage.pageNumber}`);
        }
        if (startPage.hasImage) {
          reasons.push(`Contém figura/imagem na página ${startPage.pageNumber}`);
        }
        if (features.hasRomanNumerals) {
          reasons.push('Contém proposições em algarismos romanos (I/II/III)');
        }
        if (features.hasMathFormula) {
          reasons.push('Contém notação algébrica/fórmula científica');
        }

        confidenceScore = Math.max(10, Math.min(100, confidenceScore));
        const confidenceLevel = confidenceScore >= 80 ? 'high' : (confidenceScore >= 55 ? 'medium' : 'low');

        // Automatic routing: low confidence OR missing answer key -> Conferência Pedagógica ('pending_review')
        const validationStatus = (confidenceLevel === 'low' || !finalAnswer) ? 'pending_review' : 'approved';

        parsedQuestions.push({
          id: `q-${Date.now()}-${Math.random().toString(36).slice(2, 6)}-${i + 1}`,
          discipline: detectedDisc,
          teacher_name: teacherName,
          question_type: qType,
          statement: statement || contentBlock,
          options_json: optCount ? optionsMap : null,
          correct_answer: finalAnswer,
          has_image: startPage.hasImage,
          has_formula: features.hasMathFormula,
          has_roman_numerals: features.hasRomanNumerals,
          spans_pages: spansMultiplePages,
          page_number: startPage.pageNumber,
          confidence_score: confidenceScore,
          confidence_level: confidenceLevel,
          validation_status: validationStatus,
          validation_notes: reasons.length ? reasons.join(' • ') : 'Extração automática de alta confiança.',
          source_filename: filename
        });
      }
    } else if (bodyWithoutAnswerSheet.length > 0) {
      // Fallback when PDF has unnumbered text: mark LOW confidence -> Conferência Pedagógica
      parsedQuestions.push({
        id: `q-${Date.now()}-fallback`,
        discipline: detectedDisc,
        teacher_name: teacherName,
        question_type: 'discursive',
        statement: bodyWithoutAnswerSheet.slice(0, 600).trim(),
        options_json: null,
        correct_answer: null,
        has_image: pages.some(p => p.hasImage),
        confidence_score: 30,
        confidence_level: 'low',
        validation_status: 'pending_review',
        validation_notes: 'Numeração de questões não identificada • Encaminhada automaticamente para Conferência Pedagógica.',
        source_filename: filename
      });
    }

    return {
      discipline: detectedDisc,
      questions: parsedQuestions
    };
  }

  /**
   * Pipeline completo de processamento de arquivo PDF com cache SHA-256 + Worker + Progresso Real.
   */
  async function processPDFFile(file, options = {}) {
    const { defaultDiscipline = '', teacherName = 'Docente', onProgress = null, db = global.GIADatabase } = options;
    const t0 = performance.now();
    const buffer = await file.arrayBuffer();
    const sha256 = await computeFileSHA256(buffer);

    // 1. Check SHA-256 cache in IndexedDB
    if (db && typeof db.getPDFCache === 'function') {
      const cached = await db.getPDFCache(sha256);
      if (cached && Array.isArray(cached.questions) && cached.questions.length > 0) {
        if (typeof onProgress === 'function') {
          onProgress({ page: cached.totalPages || 1, totalPages: cached.totalPages || 1, pct: 100, fromCache: true });
        }
        // Re-mint unique IDs if re-imported while preserving parsed structure & overriding discipline if user explicitly typed one
        const clonedQuestions = cached.questions.map((q, idx) => ({
          ...q,
          id: `q-${Date.now()}-${Math.random().toString(36).slice(2, 6)}-${idx + 1}`,
          discipline: defaultDiscipline || q.discipline,
          teacher_name: teacherName || q.teacher_name,
          source_filename: file.name
        }));
        return {
          sha256,
          fromCache: true,
          elapsedMs: Math.round(performance.now() - t0),
          totalPages: cached.totalPages || 1,
          discipline: defaultDiscipline || cached.discipline,
          questions: clonedQuestions
        };
      }
    }

    // 2. Parse in Web Worker with real streaming progress
    const workerResult = await extractPDFPagesInWorker(buffer, onProgress);
    const parsed = parsePagesToQuestions(workerResult.pages, {
      defaultDiscipline,
      teacherName,
      filename: file.name
    });

    const elapsedMs = Math.round(performance.now() - t0);

    // 3. Save result in SHA-256 cache
    if (db && typeof db.setPDFCache === 'function') {
      await db.setPDFCache(sha256, {
        sha256,
        filename: file.name,
        totalPages: workerResult.totalPages,
        discipline: parsed.discipline,
        questions: parsed.questions,
        cachedAt: new Date().toISOString()
      });
    }

    return {
      sha256,
      fromCache: false,
      elapsedMs,
      totalPages: workerResult.totalPages,
      twoColumnPages: workerResult.twoColumnPages || 0,
      pagesWithImages: workerResult.pagesWithImages || 0,
      discipline: parsed.discipline,
      questions: parsed.questions
    };
  }

  global.GIAPDFParser = {
    computeFileSHA256,
    processPDFFile,
    parsePagesToQuestions,
    cancelActiveExtraction
  };
})(window);
