document.addEventListener('DOMContentLoaded', function() {
    const bell = document.getElementById('notification-bell');
    const dot = document.querySelector('.notification-dot');
    const panel = document.getElementById('notification-panel');

    if (!bell) return;

    // Function to fetch notifications
    function fetchNotifications() {
        fetch('/admin/api/notifications')
            .then(response => response.json())
            .then(data => {
                if (data.length > 0) {
                    dot.style.display = 'block';
                    updateNotificationPanel(data);
                } else {
                    dot.style.display = 'none';
                }
            })
            .catch(error => console.error('Error fetching notifications:', error));
    }

    // Function to update the panel content
    function updateNotificationPanel(notifications) {
        panel.innerHTML = ''; // Clear existing
        notifications.forEach(n => {
            const item = document.createElement('div');
            item.classList.add('notification-item');
            item.dataset.id = n.id;
            item.innerHTML = `<strong>${n.action}</strong><br>${n.details}<br><small>${new Date(n.timestamp).toLocaleString()}</small>`;
            panel.appendChild(item);
        });
    }

    // Function to mark notifications as read
    function markAsRead() {
        const unreadItems = panel.querySelectorAll('.notification-item');
        const ids = Array.from(unreadItems).map(item => item.dataset.id).filter(id => id);

        if (ids.length > 0) {
            fetch('/admin/api/notifications/mark_read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ids: ids }),
            })
            .then(() => {
                dot.style.display = 'none'; // Hide dot immediately
            })
            .catch(error => console.error('Error marking notifications as read:', error));
        }
    }

    // Toggle panel visibility
    bell.addEventListener('click', function(e) {
        e.stopPropagation();
        const isVisible = panel.classList.toggle('show');
        if (isVisible) {
            // Mark as read when panel is opened
            markAsRead();
        }
    });

    // Close panel if clicking outside
    document.addEventListener('click', function(e) {
        if (!panel.contains(e.target) && !bell.contains(e.target)) {
            panel.classList.remove('show');
        }
    });

    // Initial fetch and polling
    fetchNotifications();
    setInterval(fetchNotifications, 30000); // Poll every 30 seconds
});
