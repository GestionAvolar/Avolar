self.addEventListener('install', (e) => {
  console.log('[Service Worker] Installation en cours...');
});

self.addEventListener('fetch', (e) => {
  // Mode passe-plat par défaut pour récupérer les données du serveur Django
  e.respondWith(fetch(e.request));
});