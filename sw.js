// Service worker тренажёра ключей — офлайн-кэш и установка (PWA)
const CACHE = 'radicals-v3';

// HTML — всегда свежий с сети; аудио/шрифты/картинки — из кэша (cache-first)
const isHTML = (req) => req.mode === 'navigate' || /\.(html)(\?|$)/.test(new URL(req.url).pathname);
const isAsset = (req) => /\.(mp3|woff2|png|ico|jpg|webp)(\?|$)/.test(new URL(req.url).pathname);

self.addEventListener('install', (e) => {
  e.waitUntil(self.skipWaiting());
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  if (isHTML(req)) {
    // Network-first для HTML: всегда актуальная версия, кэш — только если офлайн
    e.respondWith(
      fetch(req)
        .then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() => caches.match(req).then((hit) => hit || caches.match('./index.html')))
    );
    return;
  }

  if (isAsset(req)) {
    // Cache-first для медиа и шрифтов: быстрая загрузка, кэшируется при первом запросе
    e.respondWith(
      caches.match(req, { ignoreSearch: true }).then((hit) => {
        if (hit) return hit;
        return fetch(req).then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        });
      })
    );
    return;
  }

  // Остальное (manifest.json, иконки) — network-first
  e.respondWith(
    fetch(req).catch(() => caches.match(req))
  );
});
