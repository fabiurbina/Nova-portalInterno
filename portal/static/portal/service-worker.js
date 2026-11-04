    const CACHE_NAME = "portal-rpa-v3";

    // Instala o Service Worker
    self.addEventListener("install", (event) => {
        event.waitUntil(
            (async () => {
                await self.skipWaiting();
            })()
        );
    });

    // Ativa a versão atual e limpa caches antigos
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

    // Mantém as requisições funcionando normalmente
    self.addEventListener("fetch", (event) => {
        event.respondWith(
            fetch(event.request).catch(() => {
                return new Response("Sem conexão", {
                    status: 503
                });
            })
        );
    });