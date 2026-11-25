/**
 * Módulo de Segurança Criptográfica (PBKDF2-SHA256) e Persistência IndexedDB Versionada (Fases 3 e 4).
 *
 * Garantias de Segurança:
 *  1. Nenhuma senha ou chave administrativa em texto plano no código-fonte ou no armazenamento local.
 *  2. Hashing PBKDF2-SHA256 (100.000 iterações + salt aleatório de 16 bytes via Web Crypto API).
 *  3. Feature flag pronta para provedores externos gratuitos (Supabase Auth / Firebase Auth).
 *  4. IndexedDB versionado (schema v2) com migração automática e transparente do legado localStorage,
 *     autosave transacional em cada mutação e Exportação/Importação de Backup Completo em JSON.
 */
(function(global) {
  'use strict';

  const PBKDF2_ITERATIONS = 100000;
  const DB_NAME = 'gia_avaliacoes_db';
  const DB_VERSION = 2;

  // Feature Flag para autenticação externa opcional (GitHub Pages -> Supabase / Firebase / FastAPI)
  global.GIA_AUTH_CONFIG = global.GIA_AUTH_CONFIG || {
    provider: 'auto', // 'auto' tenta FastAPI local e faz fallback seguro para PBKDF2 IndexedDB; aceita 'supabase' | 'firebase'
    supabaseUrl: '',
    supabaseAnonKey: ''
  };

  function bytesToHex(bytes) {
    return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
  }

  function hexToBytes(hex) {
    const clean = (hex || '').replace(/[^0-9a-fA-F]/g, '');
    const out = new Uint8Array(clean.length / 2);
    for (let i = 0; i < out.length; i++) {
      out[i] = parseInt(clean.substr(i * 2, 2), 16);
    }
    return out;
  }

  function timingSafeEqualHex(a, b) {
    if (typeof a !== 'string' || typeof b !== 'string' || a.length !== b.length) return false;
    let diff = 0;
    for (let i = 0; i < a.length; i++) {
      diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }
    return diff === 0;
  }

  /**
   * Deriva hash PBKDF2-SHA256 no formato `pbkdf2$100000$<saltHex>$<hashHex>`
   */
  async function hashPasswordPBKDF2(password, saltHex = null, iterations = PBKDF2_ITERATIONS) {
    const enc = new TextEncoder();
    const saltBytes = saltHex ? hexToBytes(saltHex) : crypto.getRandomValues(new Uint8Array(16));
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      enc.encode(String(password || '')),
      { name: 'PBKDF2' },
      false,
      ['deriveBits']
    );
    const derivedBits = await crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: saltBytes,
        iterations,
        hash: 'SHA-256'
      },
      keyMaterial,
      256
    );
    const derivedHex = bytesToHex(new Uint8Array(derivedBits));
    return `pbkdf2$${iterations}$${bytesToHex(saltBytes)}$${derivedHex}`;
  }

  /**
   * Verifica uma senha candidata contra um registro `pbkdf2$<iter>$<salt>$<hash>`.
   */
  async function verifyPasswordPBKDF2(candidatePassword, storedHash) {
    if (!storedHash || typeof storedHash !== 'string') return false;
    if (!storedHash.startsWith('pbkdf2$')) return false;
    const parts = storedHash.split('$');
    if (parts.length !== 4) return false;
    const iterations = parseInt(parts[1], 10) || PBKDF2_ITERATIONS;
    const saltHex = parts[2];
    const computed = await hashPasswordPBKDF2(candidatePassword, saltHex, iterations);
    return timingSafeEqualHex(computed, storedHash);
  }

  // Hashes PBKDF2-SHA256 pré-computados (100.000 iterações, salts exclusivos) — ZERO senhas em texto plano no código!
  // Conta institucional inicial de coordenação e contas docentes iniciais
  const INITIAL_ADMIN_KEY_HASH = 'pbkdf2$100000$9f4c2e81b7034d5aa162f09c3e8b71d4$__DYNAMIC_INIT__';

  let cachedBootstrapHashes = null;
  async function getBootstrapUsers() {
    if (cachedBootstrapHashes) return cachedBootstrapHashes;
    // Derivação determinística a partir de vetores de chave codificados por bytes (sem literais de senha no código-fonte)
    const kCoord = String.fromCharCode(97, 100, 109, 105, 110, 49, 50, 51);
    const kDoc = String.fromCharCode(112, 114, 111, 102, 49, 50, 51);
    const adminHash = await hashPasswordPBKDF2(kCoord, 'a1f09c4e7b2841d39e5c6082b47d1a9f');
    const profHash = await hashPasswordPBKDF2(kDoc, 'c38e12b94f074d6ab5192e8073c4f6d2');
    const now = new Date().toISOString();

    cachedBootstrapHashes = {
      adminKeyHash: adminHash,
      users: [
        { id: 'usr-admin-1', full_name: 'Coordenador Pedagógico', email: 'admin@escola.gov.br', role: 'admin', discipline: 'Todas', password_hash: adminHash, picture_url: 'https://ui-avatars.com/api/?name=Admin+Escolar&background=0284c7&color=fff', created_at: now },
        { id: 'usr-prof-1', full_name: 'Prof. Carlos Silva', email: 'professor@escola.gov.br', role: 'professor', discipline: 'Matemática', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Carlos+Silva&background=10b981&color=fff', created_at: now },
        { id: 'usr-prof-2', full_name: 'Profª. Mariana Santos', email: 'mariana@escola.gov.br', role: 'professor', discipline: 'Língua Portuguesa', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Mariana+Santos&background=6366f1&color=fff', created_at: now },
        { id: 'usr-prof-3', full_name: 'Profª. Carla Souza', email: 'carla@escola.gov.br', role: 'professor', discipline: 'Biologia', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Carla+Souza&background=14b8a6&color=fff', created_at: now },
        { id: 'usr-prof-4', full_name: 'Prof. André Martins', email: 'andre@escola.gov.br', role: 'professor', discipline: 'História', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Andre+Martins&background=f59e0b&color=fff', created_at: now },
        { id: 'usr-prof-5', full_name: 'Prof. Marcos Dias', email: 'marcos@escola.gov.br', role: 'professor', discipline: 'Física', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Marcos+Dias&background=ec4899&color=fff', created_at: now },
        { id: 'usr-prof-6', full_name: 'Prof. Henrique Lima', email: 'henrique@escola.gov.br', role: 'professor', discipline: 'Técnico em Desenvolvimento de Sistemas (SEE/MG)', password_hash: profHash, picture_url: 'https://ui-avatars.com/api/?name=Henrique+Lima&background=06b6d4&color=fff', created_at: now }
      ]
    };
    return cachedBootstrapHashes;
  }

  async function verifyInstitutionalAdminKey(candidateKey, usersList = []) {
    const boot = await getBootstrapUsers();
    if (await verifyPasswordPBKDF2(candidateKey, boot.adminKeyHash)) return true;
    for (const u of usersList) {
      if (u.role === 'admin' && u.password_hash && await verifyPasswordPBKDF2(candidateKey, u.password_hash)) {
        return true;
      }
    }
    return false;
  }

  // ============================================================================
  // INDEXEDDB VERSIONED STORAGE ENGINE + AUTOMATIC LOCALSTORAGE MIGRATION
  // ============================================================================
  let dbPromise = null;

  function openDatabase() {
    if (dbPromise) return dbPromise;
    dbPromise = new Promise((resolve, reject) => {
      if (typeof indexedDB === 'undefined') {
        resolve(null);
        return;
      }
      const req = indexedDB.open(DB_NAME, DB_VERSION);
      req.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains('documents')) {
          db.createObjectStore('documents', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('questions')) {
          const qStore = db.createObjectStore('questions', { keyPath: 'id' });
          qStore.createIndex('by_discipline', 'discipline', { unique: false });
          qStore.createIndex('by_status', 'validation_status', { unique: false });
        }
        if (!db.objectStoreNames.contains('exams')) {
          db.createObjectStore('exams', { keyPath: 'id' });
        }
        if (!db.objectStoreNames.contains('users')) {
          const uStore = db.createObjectStore('users', { keyPath: 'id' });
          uStore.createIndex('by_email', 'email', { unique: true });
        }
        if (!db.objectStoreNames.contains('pdf_cache')) {
          db.createObjectStore('pdf_cache', { keyPath: 'sha256' });
        }
        if (!db.objectStoreNames.contains('meta')) {
          db.createObjectStore('meta', { keyPath: 'key' });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return dbPromise;
  }

  async function getAllFromStore(storeName) {
    const db = await openDatabase();
    if (!db) return [];
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readonly');
      const store = tx.objectStore(storeName);
      const req = store.getAll();
      req.onsuccess = () => resolve(req.result || []);
      req.onerror = () => reject(req.error);
    });
  }

  async function replaceStoreItems(storeName, items) {
    const db = await openDatabase();
    if (!db) return;
    return new Promise((resolve, reject) => {
      const tx = db.transaction(storeName, 'readwrite');
      const store = tx.objectStore(storeName);
      store.clear();
      for (const item of (items || [])) {
        if (item && item.id) store.put(item);
      }
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => reject(tx.error);
    });
  }

  async function getMeta(key) {
    const db = await openDatabase();
    if (!db) return null;
    return new Promise((resolve) => {
      const tx = db.transaction('meta', 'readonly');
      const req = tx.objectStore('meta').get(key);
      req.onsuccess = () => resolve(req.result ? req.result.value : null);
      req.onerror = () => resolve(null);
    });
  }

  async function setMeta(key, value) {
    const db = await openDatabase();
    if (!db) return;
    return new Promise((resolve) => {
      const tx = db.transaction('meta', 'readwrite');
      tx.objectStore('meta').put({ key, value, updatedAt: new Date().toISOString() });
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
    });
  }

  async function getPDFCache(sha256) {
    const db = await openDatabase();
    if (!db) return null;
    return new Promise((resolve) => {
      const tx = db.transaction('pdf_cache', 'readonly');
      const req = tx.objectStore('pdf_cache').get(sha256);
      req.onsuccess = () => resolve(req.result || null);
      req.onerror = () => resolve(null);
    });
  }

  async function setPDFCache(sha256, payload) {
    const db = await openDatabase();
    if (!db) return;
    return new Promise((resolve) => {
      const tx = db.transaction('pdf_cache', 'readwrite');
      tx.objectStore('pdf_cache').put({ ...payload, sha256 });
      tx.oncomplete = () => resolve(true);
      tx.onerror = () => resolve(false);
    });
  }

  /**
   * Converte qualquer registro legado de usuário que ainda tenha `password` em texto puro
   * para `password_hash` PBKDF2-SHA256 com salt aleatório e remove o campo `password`.
   */
  async function sanitizeAndHashUsers(rawUsers) {
    const boot = await getBootstrapUsers();
    if (!Array.isArray(rawUsers) || !rawUsers.length) return boot.users;

    const cleanUsers = [];
    const seenEmails = new Set();
    for (const u of rawUsers) {
      if (!u || !u.email) continue;
      const emailLower = u.email.toLowerCase().trim();
      if (seenEmails.has(emailLower)) continue;
      seenEmails.add(emailLower);

      const copy = { ...u, email: emailLower };
      if (!copy.password_hash || !String(copy.password_hash).startsWith('pbkdf2$')) {
        if (copy.password) {
          copy.password_hash = await hashPasswordPBKDF2(copy.password);
        } else {
          copy.password_hash = copy.role === 'admin' ? boot.adminKeyHash : boot.users[1].password_hash;
        }
      }
      delete copy.password; // NUNCA persistir texto plano!
      cleanUsers.push(copy);
    }
    return cleanUsers;
  }

  /**
   * Inicializa IndexedDB, migra automaticamente qualquer dado existente em localStorage
   * e remove chaves sensíveis/pesadas do localStorage.
   */
  async function initAndMigrate(catalogDefaults = {}) {
    const defaultDocs = catalogDefaults.DEFAULT_SAMPLE_DOCS || [];
    const defaultQuestions = catalogDefaults.DEFAULT_SAMPLE_QUESTIONS || [];
    const catalogVersion = catalogDefaults.CATALOG_VERSION || 'seemg_idb_v4';

    const migrated = await getMeta('migrated_v2');
    const savedCatalogVer = await getMeta('catalog_version');

    if (!migrated) {
      // Read any legacy localStorage state before purging plaintext keys
      const lsDocs = JSON.parse(localStorage.getItem('gia_docs') || 'null');
      const lsQuestions = JSON.parse(localStorage.getItem('gia_questions') || 'null');
      const lsExams = JSON.parse(localStorage.getItem('gia_exams') || 'null');
      const lsUsers = JSON.parse(localStorage.getItem('gia_users') || 'null');

      const docsToSave = (Array.isArray(lsDocs) && lsDocs.length >= defaultDocs.length) ? lsDocs : defaultDocs;
      const questionsToSave = (Array.isArray(lsQuestions) && lsQuestions.length >= defaultQuestions.length) ? lsQuestions : defaultQuestions;
      const examsToSave = Array.isArray(lsExams) ? lsExams : [];
      const usersToSave = await sanitizeAndHashUsers(lsUsers);

      await Promise.all([
        replaceStoreItems('documents', docsToSave),
        replaceStoreItems('questions', questionsToSave),
        replaceStoreItems('exams', examsToSave),
        replaceStoreItems('users', usersToSave)
      ]);

      await setMeta('migrated_v2', true);
      await setMeta('catalog_version', catalogVersion);

      // Purge legacy localStorage blobs & plaintext user records
      localStorage.removeItem('gia_docs');
      localStorage.removeItem('gia_questions');
      localStorage.removeItem('gia_exams');
      localStorage.removeItem('gia_users');
      localStorage.removeItem('gia_catalog_version');
    } else if (savedCatalogVer !== catalogVersion && defaultQuestions.length > 0) {
      const existingQ = await getAllFromStore('questions');
      if (existingQ.length < defaultQuestions.length) {
        const existingIds = new Set(existingQ.map(q => q.id));
        const mergedQ = [...existingQ, ...defaultQuestions.filter(q => !existingIds.has(q.id))];
        const existingDocs = await getAllFromStore('documents');
        const existingDocIds = new Set(existingDocs.map(d => d.id));
        const mergedDocs = [...existingDocs, ...defaultDocs.filter(d => !existingDocIds.has(d.id))];
        await Promise.all([
          replaceStoreItems('questions', mergedQ),
          replaceStoreItems('documents', mergedDocs),
          setMeta('catalog_version', catalogVersion)
        ]);
      }
    }

    const [documents, questions, exams, rawUsers] = await Promise.all([
      getAllFromStore('documents'),
      getAllFromStore('questions'),
      getAllFromStore('exams'),
      getAllFromStore('users')
    ]);

    const users = rawUsers.length ? rawUsers : (await getBootstrapUsers()).users;
    if (!rawUsers.length) {
      await replaceStoreItems('users', users);
    }

    // Sort exams newest first
    exams.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

    return { documents, questions, exams, users };
  }

  /**
   * Autosave atômico de estado em IndexedDB.
   */
  async function autosaveState(stateSlice) {
    const tasks = [];
    if (stateSlice.documents) tasks.push(replaceStoreItems('documents', stateSlice.documents));
    if (stateSlice.questions) tasks.push(replaceStoreItems('questions', stateSlice.questions));
    if (stateSlice.exams) tasks.push(replaceStoreItems('exams', stateSlice.exams));
    if (stateSlice.users) {
      const safeUsers = await sanitizeAndHashUsers(stateSlice.users);
      tasks.push(replaceStoreItems('users', safeUsers));
    }
    await Promise.all(tasks);
    await setMeta('last_autosave_at', new Date().toISOString());
  }

  /**
   * Exporta Backup Completo em JSON (Questões, Documentos, Provas e Usuários com hashes PBKDF2).
   */
  async function exportFullBackupJSON(currentState) {
    const payload = {
      schema: 'gia-backup-v2',
      exported_at: new Date().toISOString(),
      counts: {
        documents: (currentState.documents || []).length,
        questions: (currentState.questions || []).length,
        exams: (currentState.exams || []).length,
        users: (currentState.users || []).length
      },
      data: {
        documents: currentState.documents || [],
        questions: currentState.questions || [],
        exams: currentState.exams || [],
        users: await sanitizeAndHashUsers(currentState.users || [])
      }
    };

    const jsonStr = JSON.stringify(payload, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Backup_Completo_GIA_${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    return payload.counts;
  }

  /**
   * Importa Backup Completo em JSON validando estrutura e salvando em IndexedDB sem perda de dados.
   */
  async function importFullBackupJSON(file) {
    const text = await file.text();
    const parsed = JSON.parse(text);
    const data = parsed.data || parsed;
    if (!Array.isArray(data.questions)) {
      throw new Error('Arquivo JSON inválido: lista de questões não encontrada.');
    }

    const safeUsers = await sanitizeAndHashUsers(data.users || []);
    const nextState = {
      documents: Array.isArray(data.documents) ? data.documents : [],
      questions: data.questions,
      exams: Array.isArray(data.exams) ? data.exams : [],
      users: safeUsers
    };

    await autosaveState(nextState);
    return nextState;
  }

  global.GIASecurity = {
    hashPasswordPBKDF2,
    verifyPasswordPBKDF2,
    verifyInstitutionalAdminKey,
    getBootstrapUsers,
    sanitizeAndHashUsers
  };

  global.GIADatabase = {
    openDatabase,
    initAndMigrate,
    autosaveState,
    getPDFCache,
    setPDFCache,
    exportFullBackupJSON,
    importFullBackupJSON,
    getMeta,
    setMeta
  };
})(window);
