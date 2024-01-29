/* eslint-disable no-restricted-globals */
const cacheName = "odoo-sw-cache";

self.addEventListener("install", event => {
    event.waitUntil(caches.open(cacheName).then(cache => cache.addAll(["/"]))); //唯一?
});

const navigateOrFetch = async request => {
    try {
        return await fetch(request);
    } catch (error) {
        if (
            request.method === "GET" &&
            ["Failed to fetch", "Load failed"].includes(error.message)
        ) {
            const cache = await caches.open(cacheName);
            const cachedResponse = await cache.match(request);
            if (cachedResponse) {
                return cachedResponse;
            }
        }
        throw error;
    }
};

self.addEventListener("fetch", event => {
    if (
        (event.request.mode === "navigate" &&
            event.request.destination === "document") ||
        event.request.headers.get("accept").includes("text/html")
    ) {
        event.respondWith(navigateOrFetch(event.request));
    }
});
