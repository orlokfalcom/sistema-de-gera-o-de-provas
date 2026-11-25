/**
 * Módulo de UX, Acessibilidade (WCAG AA), Toasts com Undo, Virtualização de Listas e Isolamento de Gabarito (Fases 2, 4 e 5).
 */
(function(global) {
  'use strict';

  // ============================================================================
  // 1. SISTEMA DE TOASTS ACESSÍVEIS (ARIA-LIVE) COM SUPORTE A UNDO (DESFAZER)
  // ============================================================================
  function ensureToastContainer() {
    let container = document.getElementById('gia-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'gia-toast-container';
      container.setAttribute('role', 'region');
      container.setAttribute('aria-label', 'Notificações do sistema');
      container.setAttribute('aria-live', 'polite');
      container.className = 'fixed bottom-4 right-4 z-[80] flex flex-col gap-2.5 max-w-md w-[calc(100vw-2rem)] pointer-events-none';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * Exibe toast não-bloqueante em substituição a `alert()`.
   * @param {string} message Texto da mensagem
   * @param {'info'|'success'|'warning'|'error'} type Estilo semântico
   * @param {{ duration?: number, undoLabel?: string, onUndo?: Function }} opts Opções extras
   */
  function showToast(message, type = 'info', opts = {}) {
    const container = ensureToastContainer();
    const duration = opts.duration || (opts.onUndo ? 7000 : 4200);

    // Auto-detect semantic type from leading emoji if caller used default 'info'
    if (type === 'info' && typeof message === 'string') {
      if (/^(✅|✓|🔓)/.test(message.trim())) type = 'success';
      else if (/^(❌|Erro)/i.test(message.trim())) type = 'error';
      else if (/^(⚠️|🗑️)/.test(message.trim())) type = 'warning';
    }

    const palette = {
      success: 'bg-emerald-950/95 text-emerald-50 border-emerald-600/60',
      error: 'bg-rose-950/95 text-rose-50 border-rose-600/60',
      warning: 'bg-amber-950/95 text-amber-50 border-amber-500/60',
      info: 'bg-slate-900/95 text-slate-50 border-sky-500/60'
    };
    const icons = { success: '✓', error: '✕', warning: '⚠', info: 'ℹ' };

    const toast = document.createElement('div');
    toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
    toast.className = `pointer-events-auto flex items-center justify-between gap-3 px-4 py-3 rounded-2xl border shadow-2xl backdrop-blur-md text-xs font-medium transition-all duration-300 translate-y-2 opacity-0 ${palette[type] || palette.info}`;

    const msgWrap = document.createElement('div');
    msgWrap.className = 'flex items-start gap-2.5 leading-relaxed';
    const badge = document.createElement('span');
    badge.className = 'w-5 h-5 rounded-full bg-white/15 flex items-center justify-center font-bold shrink-0 text-[11px]';
    badge.textContent = icons[type] || 'ℹ';
    const textSpan = document.createElement('span');
    textSpan.textContent = String(message || '').replace(/^(✅|❌|⚠️)\s*/, '');
    msgWrap.appendChild(badge);
    msgWrap.appendChild(textSpan);
    toast.appendChild(msgWrap);

    const actionsWrap = document.createElement('div');
    actionsWrap.className = 'flex items-center gap-1.5 shrink-0';

    if (typeof opts.onUndo === 'function') {
      const undoBtn = document.createElement('button');
      undoBtn.type = 'button';
      undoBtn.className = 'px-2.5 py-1 rounded-lg bg-white/20 hover:bg-white/30 text-white font-bold text-[11px] transition focus:outline-none focus:ring-2 focus:ring-white';
      undoBtn.textContent = opts.undoLabel || 'Desfazer';
      undoBtn.onclick = () => {
        try { opts.onUndo(); } finally { dismiss(); }
      };
      actionsWrap.appendChild(undoBtn);
    }

    const closeBtn = document.createElement('button');
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', 'Fechar notificação');
    closeBtn.className = 'p-1 rounded-lg text-white/70 hover:text-white hover:bg-white/10 transition focus:outline-none focus:ring-2 focus:ring-white';
    closeBtn.textContent = '✕';
    closeBtn.onclick = () => dismiss();
    actionsWrap.appendChild(closeBtn);
    toast.appendChild(actionsWrap);

    container.appendChild(toast);
    requestAnimationFrame(() => {
      toast.classList.remove('translate-y-2', 'opacity-0');
    });

    let timer = setTimeout(dismiss, duration);
    function dismiss() {
      clearTimeout(timer);
      toast.classList.add('opacity-0', 'translate-y-2');
      setTimeout(() => {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 220);
    }
  }

  // ============================================================================
  // 2. MODAL ACESSÍVEL DE CONFIRMAÇÃO PARA AÇÕES DESTRUTIVAS (TECLADO + ARIA)
  // ============================================================================
  function confirmDialog({ title = 'Confirmar ação', message = '', confirmLabel = 'Confirmar', cancelLabel = 'Cancelar', danger = false } = {}) {
    return new Promise((resolve) => {
      let modal = document.getElementById('gia-confirm-modal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'gia-confirm-modal';
        modal.setAttribute('role', 'dialog');
        modal.setAttribute('aria-modal', 'true');
        modal.setAttribute('aria-labelledby', 'gia-confirm-title');
        document.body.appendChild(modal);
      }

      const previouslyFocused = document.activeElement;
      modal.className = 'fixed inset-0 z-[75] bg-black/60 backdrop-blur-xs flex items-center justify-center p-4';
      modal.innerHTML = `
        <div class="bg-white dark:bg-slate-900 w-full max-w-md rounded-3xl shadow-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-2xl ${danger ? 'bg-rose-100 text-rose-600 dark:bg-rose-950 dark:text-rose-400' : 'bg-sky-100 text-sky-600 dark:bg-sky-950 dark:text-sky-400'} flex items-center justify-center text-lg shrink-0 font-bold">
              ${danger ? '⚠️' : '🛡️'}
            </div>
            <div>
              <h3 id="gia-confirm-title" class="text-sm font-extrabold text-slate-900 dark:text-white">${escapeHTML(title)}</h3>
              <p class="text-xs text-slate-600 dark:text-slate-300 mt-1 whitespace-pre-line leading-relaxed">${escapeHTML(message)}</p>
            </div>
          </div>
          <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-100 dark:border-slate-800">
            <button type="button" id="gia-confirm-cancel" class="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-bold transition focus:outline-none focus:ring-2 focus:ring-sky-500">
              ${escapeHTML(cancelLabel)}
            </button>
            <button type="button" id="gia-confirm-accept" class="px-4 py-2 rounded-xl ${danger ? 'bg-rose-600 hover:bg-rose-700 focus:ring-rose-500' : 'bg-sky-600 hover:bg-sky-700 focus:ring-sky-500'} text-white text-xs font-bold transition shadow-xs focus:outline-none focus:ring-2">
              ${escapeHTML(confirmLabel)}
            </button>
          </div>
        </div>
      `;

      const btnCancel = document.getElementById('gia-confirm-cancel');
      const btnAccept = document.getElementById('gia-confirm-accept');

      function close(result) {
        document.removeEventListener('keydown', onKey);
        modal.classList.add('hidden');
        if (previouslyFocused && typeof previouslyFocused.focus === 'function') {
          previouslyFocused.focus();
        }
        resolve(result);
      }

      function onKey(e) {
        if (e.key === 'Escape') { e.preventDefault(); close(false); }
      }

      btnCancel.onclick = () => close(false);
      btnAccept.onclick = () => close(true);
      document.addEventListener('keydown', onKey);
      setTimeout(() => btnAccept.focus(), 30);
    });
  }

  function escapeHTML(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  // ============================================================================
  // 3. ISOLAMENTO ESTRITO DE GABARITO NA DOM DA PROVA DO ESTUDANTE (FASE 4.3)
  // ============================================================================
  /**
   * Retorna uma cópia profunda da prova com TODOS os campos de gabarito (`correct_answer`,
   * `inline_answer`, `validation_notes`) removidos antes de qualquer renderização de DOM do aluno.
   */
  function sanitizeExamForStudentDOM(exam) {
    if (!exam) return null;
    return {
      id: exam.id,
      title: exam.title,
      institution_name: exam.institution_name,
      academic_period: exam.academic_period,
      school_modality: exam.school_modality,
      target_grade: exam.target_grade,
      organization_mode: exam.organization_mode,
      show_discipline_header: exam.show_discipline_header,
      total_questions: exam.total_questions,
      created_at: exam.created_at,
      items: (exam.items || []).map(it => {
        const q = it.question || {};
        return {
          order_number: it.order_number,
          question: {
            id: q.id,
            discipline: q.discipline,
            question_type: q.question_type,
            statement: q.statement,
            options_json: q.options_json ? { ...q.options_json } : null
            // NENHUM campo `correct_answer` é copiado para a árvore de objetos do estudante!
          }
        };
      })
    };
  }

  // ============================================================================
  // 4. VIRTUALIZAÇÃO / RENDERIZAÇÃO EM JANELA (WINDOWED VIRTUAL RENDERER)
  // ============================================================================
  /**
   * Renderiza listas grandes em janelas incrementais usando IntersectionObserver,
   * mantendo o custo inicial de DOM em O(pageSize) (~20 nós) mesmo para 1.000+ itens!
   */
  const activeObservers = new WeakMap();

  function renderVirtualizedList(container, items, renderItemFn, options = {}) {
    if (!container) return;
    const pageSize = options.pageSize || 24;
    const emptyHTML = options.emptyHTML || '<div class="p-8 text-center text-xs text-slate-400">Nenhum registro encontrado.</div>';
    const headerHTML = options.headerHTML || '';
    const isTableBody = container.tagName === 'TBODY';

    const prevObs = activeObservers.get(container);
    if (prevObs) {
      prevObs.disconnect();
      activeObservers.delete(container);
    }

    if (!items || items.length === 0) {
      container.innerHTML = headerHTML + emptyHTML;
      return;
    }

    let renderedCount = Math.min(pageSize, items.length);
    const initialSlice = items.slice(0, renderedCount).map(renderItemFn).join('');
    container.innerHTML = headerHTML + initialSlice;

    if (renderedCount >= items.length) return;

    const sentinel = document.createElement(isTableBody ? 'tr' : 'div');
    if (isTableBody) {
      sentinel.innerHTML = `<td colspan="8" class="p-3 text-center text-[11px] text-sky-600 dark:text-sky-400 font-semibold">Carregando mais registros (${renderedCount}/${items.length})...</td>`;
    } else {
      sentinel.className = 'py-3 text-center text-[11px] text-sky-600 dark:text-sky-400 font-semibold col-span-full';
      sentinel.textContent = `Exibindo ${renderedCount} de ${items.length} — role para carregar mais...`;
    }
    container.appendChild(sentinel);

    if (typeof IntersectionObserver !== 'undefined') {
      const obs = new IntersectionObserver((entries) => {
        if (!entries.some(e => e.isIntersecting)) return;
        const nextEnd = Math.min(renderedCount + pageSize, items.length);
        const fragmentHTML = items.slice(renderedCount, nextEnd).map(renderItemFn).join('');
        sentinel.insertAdjacentHTML('beforebegin', fragmentHTML);
        renderedCount = nextEnd;

        if (renderedCount >= items.length) {
          obs.disconnect();
          activeObservers.delete(container);
          if (sentinel.parentNode) sentinel.parentNode.removeChild(sentinel);
        } else if (isTableBody) {
          sentinel.innerHTML = `<td colspan="8" class="p-3 text-center text-[11px] text-sky-600 dark:text-sky-400 font-semibold">Carregando mais registros (${renderedCount}/${items.length})...</td>`;
        } else {
          sentinel.textContent = `Exibindo ${renderedCount} de ${items.length} — role para carregar mais...`;
        }
      }, { rootMargin: '220px' });

      obs.observe(sentinel);
      activeObservers.set(container, obs);
    }
  }

  global.GIAUI = {
    showToast,
    confirmDialog,
    escapeHTML,
    sanitizeExamForStudentDOM,
    renderVirtualizedList
  };
})(window);
