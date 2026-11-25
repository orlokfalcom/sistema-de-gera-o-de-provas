/**
 * Web Worker dedicado para leitura e extração estruturada de PDFs (PDF.js).
 * Suporta:
 *  - Progresso real página a página (streaming em lote)
 *  - Cancelamento imediato sem travar a UI principal
 *  - Reconstrução de layout em 1 ou 2 colunas (ENEM / provas escolares)
 *  - Detecção de imagens / figuras por página
 */
/* global importScripts, pdfjsLib */

let activeCancelMap = {};

function ensurePDFJS() {
  if (typeof pdfjsLib === 'undefined') {
    importScripts('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js');
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';
  }
}

/**
 * Ordena itens de texto respeitando layout de 1 ou 2 colunas e quebras de linha reais.
 */
function reconstructPageText(items, pageWidth) {
  if (!items || !items.length) return '';

  const cleanItems = items
    .filter(it => it && typeof it.str === 'string' && it.str.trim().length > 0)
    .map(it => ({
      str: it.str,
      x: it.transform ? it.transform[4] : 0,
      y: it.transform ? it.transform[5] : 0,
      w: it.width || 0,
      h: it.height || 10
    }));

  if (!cleanItems.length) return '';

  // Heuristic for 2-column exam layout (e.g. ENEM / vestibular style):
  // Many items strictly on left (< 46% width) and right (> 51% width) with few crossing the center gutter
  const midLeft = pageWidth * 0.46;
  const midRight = pageWidth * 0.52;
  let leftCount = 0;
  let rightCount = 0;
  let crossingCount = 0;

  for (const it of cleanItems) {
    if (it.x + it.w < midRight && it.x < midLeft) leftCount++;
    else if (it.x >= midRight) rightCount++;
    else crossingCount++;
  }

  const total = cleanItems.length;
  const isTwoColumn = total >= 16 && leftCount >= total * 0.25 && rightCount >= total * 0.25 && crossingCount <= total * 0.18;

  const sortLines = (subset) => {
    // Group items with close Y coordinates (same visual line within 4pt tolerance)
    subset.sort((a, b) => (Math.abs(b.y - a.y) > 4 ? b.y - a.y : a.x - b.x));
    const lines = [];
    let currentLine = [];
    let lastY = null;

    for (const tok of subset) {
      if (lastY === null || Math.abs(tok.y - lastY) <= 4.2) {
        currentLine.push(tok);
        if (lastY === null) lastY = tok.y;
      } else {
        currentLine.sort((a, b) => a.x - b.x);
        lines.push(currentLine.map(t => t.str).join(' '));
        currentLine = [tok];
        lastY = tok.y;
      }
    }
    if (currentLine.length) {
      currentLine.sort((a, b) => a.x - b.x);
      lines.push(currentLine.map(t => t.str).join(' '));
    }
    return lines.join('\n');
  };

  if (!isTwoColumn) {
    return { text: sortLines(cleanItems), isTwoColumn: false };
  }

  // Separate full-width header/footer banners from left/right columns
  const headerItems = cleanItems.filter(it => it.x < midLeft && (it.x + it.w) > midRight);
  const leftCol = cleanItems.filter(it => !headerItems.includes(it) && it.x < (pageWidth * 0.5));
  const rightCol = cleanItems.filter(it => !headerItems.includes(it) && it.x >= (pageWidth * 0.5));

  const parts = [];
  if (headerItems.length) parts.push(sortLines(headerItems));
  if (leftCol.length) parts.push(sortLines(leftCol));
  if (rightCol.length) parts.push(sortLines(rightCol));

  return { text: parts.join('\n'), isTwoColumn: true };
}

self.onmessage = async function(e) {
  const msg = e.data || {};
  if (msg.type === 'cancel' && msg.jobId) {
    activeCancelMap[msg.jobId] = true;
    return;
  }

  if (msg.type === 'extract') {
    const { jobId, buffer } = msg;
    activeCancelMap[jobId] = false;
    const t0 = performance.now();

    try {
      ensurePDFJS();
      const loadingTask = pdfjsLib.getDocument({ data: buffer });
      const pdf = await loadingTask.promise;
      const totalPages = pdf.numPages;
      const pagesOutput = [];
      let twoColumnPages = 0;
      let pagesWithImages = 0;

      for (let pageNum = 1; pageNum <= totalPages; pageNum++) {
        if (activeCancelMap[jobId]) {
          delete activeCancelMap[jobId];
          self.postMessage({ type: 'cancelled', jobId });
          return;
        }

        const page = await pdf.getPage(pageNum);
        const viewport = page.getViewport({ scale: 1.0 });
        const textContent = await page.getTextContent();
        const reconstructed = reconstructPageText(textContent.items, viewport.width || 595);

        // Detect embedded raster/image XObjects on the page
        let hasImage = false;
        try {
          const ops = await page.getOperatorList();
          if (ops && ops.fnArray && typeof pdfjsLib.OPS !== 'undefined') {
            const imgOps = [pdfjsLib.OPS.paintImageXObject, pdfjsLib.OPS.paintInlineImageXObject, pdfjsLib.OPS.paintJpegXObject].filter(Boolean);
            hasImage = ops.fnArray.some(fn => imgOps.includes(fn));
          }
        } catch (_) {
          hasImage = false;
        }

        if (reconstructed.isTwoColumn) twoColumnPages++;
        if (hasImage) pagesWithImages++;

        pagesOutput.push({
          pageNumber: pageNum,
          text: reconstructed.text,
          isTwoColumn: reconstructed.isTwoColumn,
          hasImage
        });

        self.postMessage({
          type: 'progress',
          jobId,
          page: pageNum,
          totalPages,
          pct: Math.round((pageNum / totalPages) * 100)
        });
      }

      delete activeCancelMap[jobId];
      self.postMessage({
        type: 'done',
        jobId,
        totalPages,
        twoColumnPages,
        pagesWithImages,
        elapsedMs: Math.round(performance.now() - t0),
        pages: pagesOutput
      });
    } catch (err) {
      delete activeCancelMap[jobId];
      self.postMessage({
        type: 'error',
        jobId,
        error: err && err.message ? err.message : String(err)
      });
    }
  }
};
