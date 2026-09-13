---
layout: compress
permalink: '/sw.js'
# PWA service worker
---

self.importScripts('{{ "/assets/js/data/swcache.js" | relative_url }}');

const cacheName = 'chirpy-{{ "now" | date: "%Y%m%d.%H%M%S" }}';

function verifyDomain(url) {
    for (const domain of allowedDomains) {
        const regex = RegExp(`^http(s)?:\/\/${domain}\/`);
        if (regex.test(url)) {
            return true;
        }
    }

    return false;
}

function isExcluded(url) {
    for (const item of denyUrls) {
        if (url === item) {
            return true;
        }
    }

    return false;
}

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(cacheName)
            .then(cache => cache.addAll(resource))
            // Do not leave a newer site shell waiting behind a stale cached page.
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys()
            .then(keyList => {
                return Promise.all(
                    keyList.map(key => {
                        if (key !== cacheName) {
                            return caches.delete(key);
                        }
                    })
                );
            })
            // Take control immediately so tabs receive the current navigation.
            .then(() => self.clients.claim())
    );
});

self.addEventListener('message', (event) => {
    if (event.data === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

self.addEventListener('fetch', event => {
    // HTML navigation must prefer the network. A cache-first homepage can hide
    // newly added tabs until a user performs a hard refresh.
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    const responseToCache = response.clone();
                    caches.open(cacheName).then(cache => {
                        cache.put(event.request, responseToCache);
                    });
                    return response;
                })
                .catch(() => caches.match(event.request))
        );
        return;
    }

    event.respondWith(
        caches.match(event.request).then(response => {
            if (response) {
                return response;
            }

            return fetch(event.request).then(response => {
                const url = event.request.url;

                if (event.request.method !== 'GET' ||
                    !verifyDomain(url) ||
                    isExcluded(url)) {
                    return response;
                }

                /*
                  see: <https://developers.google.com/web/fundamentals/primers/service-workers#cache_and_return_requests>
                */
                let responseToCache = response.clone();

                caches.open(cacheName).then(cache => {
                    /* console.log('[sw] Caching new resource: ' + event.request.url); */
                    cache.put(event.request, responseToCache);
                });

                return response;
            });
        })
    );
});
