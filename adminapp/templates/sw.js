'use strict';

self.addEventListener('push', function (event) {

    const title = 'Supplementer';
    const options = {
        body: ` "${event.data.text()}"`,
        icon: '../static/assets/images/logo.png',
        badge: '../static/assets/images/avatar.png'
    };

    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function (event) {
    console.log('[Service Worker] Notification click Received.');

    event.notification.close();

    event.waitUntil(
        clients.openWindow('http://127.0.0.1:8000/')
    );
});