
const CACHE_NAME = "portal-rpa-v2";

// Instala o Service Worker.
self.addEventListener("install", (event) => {
    event.waitUntil(
        (async () => {
            await self.skipWaiting();
        })()
    );
});

// Ativa a versão atual e limpa caches antigos.
self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            try {
                const cachesExistentes = await caches.keys();

                await Promise.all(
                    cachesExistentes
                        .filter(
                            (nome) =>
                                nome.startsWith("portal-rpa-") &&
                                nome !== CACHE_NAME
                        )
                        .map((nome) => caches.delete(nome))
                );

                await self.clients.claim();

            } catch (erro) {
                console.error(
                    "Erro ao ativar Service Worker:",
                    erro
                );
            }
        })()
    );
});

// Não intercepta requisições.
// O Django continua responsável pelo login,
// permissões e informações do dashboard.
