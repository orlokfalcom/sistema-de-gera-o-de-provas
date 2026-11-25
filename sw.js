const CACHE_NAME = 'gerador-provas-ghpages-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Let network handle or fallback
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});
