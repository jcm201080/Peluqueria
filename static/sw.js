// static/sw.js
self.addEventListener('install', (e) => {
  console.log('Service Worker: Instalado');
});

self.addEventListener('fetch', (e) => {
  // Este código permite que la app funcione incluso con conexión inestable
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});