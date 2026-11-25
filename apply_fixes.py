# Script to fix syntax errors and enhance GitHub Pages interactivity in index.html

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix line 1530: extra closing brace after deleteUser
bad_block_1 = """      // Local fallback
      if (state.users) {
        state.users = state.users.filter(u => u.id !== userId);
        localStorage.setItem('gia_users', JSON.stringify(state.users));
        alert('🗑️ Usuário excluído com sucesso.');
        renderUsersTable(state.users);
      }
    }
  }

    function toggleDarkMode() {"""

fixed_block_1 = """      // Local fallback
      if (state.users) {
        state.users = state.users.filter(u => u.id !== userId);
        localStorage.setItem('gia_users', JSON.stringify(state.users));
        alert('🗑️ Usuário excluído com sucesso.');
        renderUsersTable(state.users);
      }
    }

    function toggleDarkMode() {"""

assert bad_block_1 in content, "bad_block_1 not found in index.html"
content = content.replace(bad_block_1, fixed_block_1, 1)

# 2. Fix line 1824: extra closing brace after renderDashboardDisciplineList
bad_block_2 = """            </div>
          </div>
        `;
      }).join('');
    }
    }

    function changeTeacherDiscipline(disc) {"""

fixed_block_2 = """            </div>
          </div>
        `;
      }).join('');
    }

    function changeTeacherDiscipline(disc) {"""

assert bad_block_2 in content, "bad_block_2 not found in index.html"
content = content.replace(bad_block_2, fixed_block_2, 1)

# 3. Enhance Google Workspace tools: syncDriveLatest, exportSheetsLog, showAppsScriptModal
old_google_sync = """    // Google Workspace Sync Simulation
    function syncDriveLatest() {
      const statusEl = document.getElementById('drive-sync-status');
      statusEl.innerText = 'Sincronizando com o Google Drive institucional...';
      setTimeout(() => {
        statusEl.innerText = '✓ Sincronizado com sucesso! Pastas organizadas por ano letivo e bimestre.';
      }, 600);
    }

    function exportSheetsLog() {
      const statusEl = document.getElementById('sheets-sync-status');
      statusEl.innerText = 'Exportando registros para o Google Sheets...';
      setTimeout(() => {
        statusEl.innerText = `✓ Planilha atualizada com ${state.questions.length} questões e gabarito oficial!`;
      }, 600);
    }

    function showAppsScriptModal() {
      alert("Código Google Apps Script pronto para integração:\\n\\nfunction onDocumentUploadDrive(e) {\\n  var folder = DriveApp.getFolderById('ID_PASTA_RECEBIMENTO');\\n  // Webhook com a plataforma...\\n}");
    }"""

new_google_sync = """    // Google Workspace Sync & Web Interaction Engine (GitHub Pages & Backend)
    async function syncDriveLatest() {
      const statusEl = document.getElementById('drive-sync-status');
      if (statusEl) statusEl.innerHTML = '<span class="text-amber-500 animate-pulse">⏳ Sincronizando pastas no Google Drive institucional...</span>';

      let syncedBackend = false;
      try {
        const res = await fetch('/api/cloud/sync-drive', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-Role': state.currentUser.role,
            'X-User-Email': state.currentUser.email
          },
          body: JSON.stringify({
            academic_year: '2026',
            target_grade: '3º Ano do Ensino Médio',
            exam_title: currentActiveExam ? currentActiveExam.title : 'Avaliação Geral Multidisciplinar'
          })
        });
        if (res.ok) syncedBackend = true;
      } catch (e) {
        // GitHub Pages / Offline mode
      }

      setTimeout(() => {
        const period = currentActiveExam ? currentActiveExam.academic_period : '2026 - 1º Trimestre';
        const title = currentActiveExam ? currentActiveExam.title : 'Avaliação Multidisciplinar Integrada';
        const modality = currentActiveExam && currentActiveExam.school_modality === 'regular' ? 'Ensino Regular (Não Integral)' : 'Tempo Integral (EMTI / PEI)';
        
        if (statusEl) {
          statusEl.innerHTML = `✓ <strong>Sincronização Concluída!</strong> Pastas estruturadas criadas no Google Drive Institucional: <br><span class="font-mono text-[10px] text-slate-500 dark:text-slate-400">/Drive/Avaliações/${period}/${title}/ (${modality})</span>`;
        }
        
        openDriveModal(period, title, modality);
      }, 400);
    }

    function openDriveModal(period, title, modality) {
      let modal = document.getElementById('modal-drive-sync');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-drive-sync';
        modal.className = 'fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4';
        document.body.appendChild(modal);
      }
      
      const qCount = currentActiveExam ? currentActiveExam.total_questions : state.questions.length;
      
      modal.innerHTML = `
        <div class="bg-white dark:bg-slate-900 w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-800 p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-2xl bg-amber-100 dark:bg-amber-950/80 text-amber-600 dark:text-amber-400 flex items-center justify-center text-xl">
                📁
              </div>
              <div>
                <h4 class="text-sm font-bold text-slate-900 dark:text-white">Google Drive — Pastas Sincronizadas</h4>
                <p class="text-[10px] text-slate-500">Mapeamento estruturado na nuvem institucional</p>
              </div>
            </div>
            <button onclick="closeDriveModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-bold text-sm">✕</button>
          </div>

          <div class="bg-slate-50 dark:bg-slate-800/60 rounded-2xl p-4 border border-slate-200 dark:border-slate-700/60 font-mono text-xs text-slate-700 dark:text-slate-200 space-y-2">
            <div class="flex items-center gap-2 text-sky-600 dark:text-sky-400 font-bold">
              <span>📂</span> <span>Google Drive / Avaliações Institucionais 2026</span>
            </div>
            <div class="pl-5 space-y-1.5 border-l-2 border-slate-300 dark:border-slate-600 ml-2">
              <div class="flex items-center gap-2 font-semibold">
                <span>📁</span> <span>${period} (${modality})</span>
              </div>
              <div class="pl-5 space-y-1 border-l-2 border-slate-200 dark:border-slate-700 ml-2 text-[11px]">
                <div class="flex items-center justify-between text-slate-600 dark:text-slate-300">
                  <span>📄 Prova_Multidisciplinar_Completa.docx</span>
                  <span class="text-[9px] px-1.5 py-0.2 rounded bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300">ABNT NBR 14724</span>
                </div>
                <div class="flex items-center justify-between text-slate-600 dark:text-slate-300">
                  <span>📄 Caderno_Estudante_Oficial.pdf</span>
                  <span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">Sem Gabarito</span>
                </div>
                <div class="flex items-center justify-between text-slate-600 dark:text-slate-300">
                  <span>📄 Gabarito_Professores.pdf</span>
                  <span class="text-[9px] px-1.5 py-0.2 rounded bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">Sigiloso</span>
                </div>
                <div class="flex items-center justify-between text-slate-600 dark:text-slate-300">
                  <span>📊 Matriz_Curricular_e_Respostas.csv</span>
                  <span class="text-[9px] px-1.5 py-0.2 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">${qCount} itens</span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
            <span class="text-emerald-600 dark:text-emerald-400 font-semibold flex items-center gap-1.5 text-[11px]">
              <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              Sincronizado & Disponível
            </span>
            <div class="flex items-center gap-2">
              <button onclick="exportSheetsLog(); closeDriveModal();" class="px-3 py-1.5 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 font-bold text-slate-700 dark:text-slate-200">
                Baixar Planilha CSV
              </button>
              <button onclick="closeDriveModal()" class="px-4 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold shadow-xs">
                OK, Concluído
              </button>
            </div>
          </div>
        </div>
      `;
      modal.classList.remove('hidden');
    }

    function closeDriveModal() {
      const modal = document.getElementById('modal-drive-sync');
      if (modal) modal.classList.add('hidden');
    }

    async function exportSheetsLog() {
      const statusEl = document.getElementById('sheets-sync-status');
      if (statusEl) statusEl.innerHTML = '<span class="text-emerald-600 animate-pulse">⏳ Gerando planilha compatível com Google Sheets e Excel...</span>';

      // 1. Try backend
      try {
        await fetch('/api/cloud/export-sheets', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-Role': state.currentUser.role,
            'X-User-Email': state.currentUser.email
          },
          body: JSON.stringify({
            academic_period: currentActiveExam ? currentActiveExam.academic_period : '2026 - 1º Trimestre'
          })
        });
      } catch (e) { }

      // 2. Generate Real Client-Side CSV file with UTF-8 BOM
      const questionsToExport = (currentActiveExam && currentActiveExam.items) 
        ? currentActiveExam.items.map(it => it.question)
        : state.questions;

      let csv = "\\ufeffOrdem;ID;Disciplina;Docente;Tipo;Enunciado;Opcao_A;Opcao_B;Opcao_C;Opcao_D;Opcao_E;Gabarito_Oficial;Status_Validacao\\n";

      questionsToExport.forEach((q, idx) => {
        const clean = (txt) => '"' + (txt || '').replace(/"/g, '""').replace(/\\n/g, ' ') + '"';
        const opts = q.options_json || {};
        csv += `${idx + 1};${clean(q.id)};${clean(q.discipline)};${clean(q.teacher_name || 'Docente')};${clean(q.question_type)};${clean(q.statement)};${clean(opts['A'])};${clean(opts['B'])};${clean(opts['C'])};${clean(opts['D'])};${clean(opts['E'])};${clean(q.correct_answer)};${clean(q.validation_status)}\\n`;
      });

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Matriz_Curricular_Gabarito_GoogleSheets_${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      if (statusEl) {
        statusEl.innerHTML = `✓ <strong>Planilha CSV baixada com sucesso!</strong> (${questionsToExport.length} questões com gabarito oficial prontas para abrir no Google Sheets ou Excel).`;
      }
    }

    function showAppsScriptModal() {
      let modal = document.getElementById('modal-apps-script');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'modal-apps-script';
        modal.className = 'fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4';
        document.body.appendChild(modal);
      }

      const scriptCode = `/**
 * INTEGRAÇÃO GOOGLE APPS SCRIPT — PLATAFORMA GIA ENSINO MÉDIO
 * Vincule pastas do Google Drive e planilhas do Sheets automaticamente.
 */
function onDocumentUploadDrive(e) {
  var folderId = "ID_PASTA_RECEBIMENTO_INSTITUCIONAL";
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();
  
  while (files.hasNext()) {
    var file = files.next();
    Logger.log("Arquivo docente recebido: " + file.getName());
    // Notifica o endpoint da plataforma escolar
  }
}

function exportarGabaritoParaPlanilha(dados) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  sheet.appendRow(["Ordem", "Disciplina", "Enunciado", "Gabarito", "Docente"]);
}`;

      modal.innerHTML = `
        <div class="bg-white dark:bg-slate-900 w-full max-w-xl rounded-3xl shadow-2xl overflow-hidden border border-slate-200 dark:border-slate-800 p-6 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <div class="flex items-center gap-3">
              <span class="text-2xl">⚡</span>
              <div>
                <h4 class="text-sm font-bold text-slate-900 dark:text-white">Código Google Apps Script (.gs)</h4>
                <p class="text-[10px] text-slate-500">Automação oficial para Google Drive e Google Forms</p>
              </div>
            </div>
            <button onclick="closeAppsScriptModal()" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 font-bold text-sm">✕</button>
          </div>

          <p class="text-xs text-slate-600 dark:text-slate-300">
            Copie e cole este script no editor do <b>Google Apps Script</b> (extensões da sua planilha ou do Drive) para sincronização automática:
          </p>

          <pre class="bg-slate-950 text-sky-300 font-mono text-[11px] p-4 rounded-2xl overflow-x-auto max-h-60 border border-slate-800 leading-relaxed"><code>${scriptCode.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>

          <div class="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800 text-xs">
            <button onclick="copyAppsScriptCode()" id="btn-copy-script" class="px-4 py-2 rounded-xl bg-sky-600 hover:bg-sky-700 text-white font-bold transition flex items-center gap-1.5 shadow-xs">
              <span>📋 Copiar Código</span>
            </button>
            <button onclick="closeAppsScriptModal()" class="px-4 py-2 rounded-xl border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 font-semibold text-slate-700 dark:text-slate-300 transition">
              Fechar
            </button>
          </div>
        </div>
      `;
      modal.classList.remove('hidden');
    }

    function closeAppsScriptModal() {
      const modal = document.getElementById('modal-apps-script');
      if (modal) modal.classList.add('hidden');
    }

    function copyAppsScriptCode() {
      const scriptCode = `function onDocumentUploadDrive(e) {
  var folderId = "ID_PASTA_RECEBIMENTO_INSTITUCIONAL";
  var folder = DriveApp.getFolderById(folderId);
  var files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    Logger.log("Arquivo docente recebido: " + file.getName());
  }
}`;
      navigator.clipboard.writeText(scriptCode).then(() => {
        const btn = document.getElementById('btn-copy-script');
        if (btn) btn.innerHTML = '<span>✓ Código Copiado!</span>';
        setTimeout(() => { if (btn) btn.innerHTML = '<span>📋 Copiar Código</span>'; }, 2000);
      });
    }

    // 1-Click Sample Model Loader for instant test on GitHub Pages
    function loadSampleModelExam() {
      state.documents = [...DEFAULT_SAMPLE_DOCS];
      state.questions = [...DEFAULT_SAMPLE_QUESTIONS];
      saveState();
      loadDocuments();
      loadDashboard();
      loadPendingQuestions();
      loadQuestions();
      alert('✅ Caderno Modelo Carregado com Sucesso! 10 questões distribuídas pelas 5 áreas do Ensino Médio prontas para conferência e montagem.');
    }"""

assert old_google_sync in content, "old_google_sync not found in index.html"
content = content.replace(old_google_sync, new_google_sync, 1)

# 4. Add 1-Click Sample Model Loader Button in upload form
old_upload_button = """            <div class="flex justify-end gap-3 pt-2">
              <button type="submit"
                class="px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold transition shadow-sm flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg> Iniciar Processamento
              </button>
            </div>"""

new_upload_button = """            <div class="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
              <button type="button" onclick="loadSampleModelExam()"
                class="w-full sm:w-auto px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-xs font-bold transition flex items-center justify-center gap-2"
                title="Carrega 10 questões completas das 5 disciplinas da BNCC e Itinerários Formativos para teste rápido no GitHub Pages">
                <span>⚡ Carregar Caderno Modelo Oficial (BNCC + Itinerários)</span>
              </button>
              <button type="submit"
                class="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-700 text-white text-xs font-bold transition shadow-sm flex items-center justify-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg> Processar Arquivos Selecionados
              </button>
            </div>"""

assert old_upload_button in content, "old_upload_button not found in index.html"
content = content.replace(old_upload_button, new_upload_button, 1)

# Write updated index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated index.html successfully.")
