document.addEventListener('DOMContentLoaded', function() {
    const bell = document.getElementById('notification-bell');
    const dot = document.querySelector('.notification-dot');
    const panel = document.getElementById('notification-panel');
    const userId = document.body.dataset.userId;

    if (!bell || !userId) return;

    const socket = io();

    socket.on('connect', () => {
        console.log('Socket.IO connected for notifications.');
    });

    socket.on('access_request', function(data) {
        console.log('Access request received:', data);
        dot.style.display = 'block';
        const requestUrl = `/admin/temp_codes?user_id=${data.user_id}`;
        const notificationHtml = `
            <div class="notification-item">
                <strong>Access Request</strong><br>
                User <strong>${data.user_name}</strong> (ID: ${data.user_id}) has requested access to a restricted page.
                <a href="${requestUrl}">Generate Code</a>
            </div>`;
        panel.insertAdjacentHTML('afterbegin', notificationHtml);
        showToast(`New access request from ${data.user_name}`, 'info');
    });

    // Toggle panel visibility
    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        panel.classList.toggle('show');
    });

    // Close panel if clicking outside
    document.addEventListener('click', function(e) {
        if (panel && !panel.contains(e.target) && !bell.contains(e.target)) {
            panel.classList.remove('show');
        }
    });
});
