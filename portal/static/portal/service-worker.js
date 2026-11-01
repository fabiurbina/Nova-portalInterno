
const CACHE_NAME = "portal-rpa-v1";

// Instala o Service Worker sem armazenar páginas ou dados privados.
self.addEventListener("install", (event) => {
    self.skipWaiting();
});

// Ativa a versão atual do Service Worker.
self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            const cachesExistentes = await caches.keys();

            await Promise.all(
                cachesExistentes
                    .filter((nome) => nome.startsWith("portal-rpa-") && nome !== CACHE_NAME)
                    .map((nome) => caches.delete(nome))
            );

            await self.clients.claim();
        })()
    );
});

// Não intercepta requisições: o Django continua responsável
// pelo login, pelas permissões e pelos dados do dashboard.
