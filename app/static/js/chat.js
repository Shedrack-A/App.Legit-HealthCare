document.addEventListener('DOMContentLoaded', function() {
    const socket = io();

    let currentRecipientId = null;
    const chatHeader = document.getElementById('chat-header');
    const chatMessages = document.getElementById('chat-messages');
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatInputArea = document.getElementById('chat-input-area');
    const userListItems = document.querySelectorAll('.user-item');

    // Get current user ID from a hidden element if available, or another method
    // For this example, let's assume it's available in a global JS variable or a data attribute
    // This needs to be set in the template, e.g., <body data-user-id="{{ current_user.id }}">
    const currentUserId = parseInt(document.body.dataset.userId, 10);

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('status', (data) => {
        console.log('Status: ' + data.msg);
    });

    // Handle user selection
    userListItems.forEach(item => {
        item.addEventListener('click', function() {
            // UI state update
            userListItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            currentRecipientId = parseInt(this.dataset.userId, 10);
            const userName = this.dataset.userName;

            chatHeader.textContent = `Chat with ${userName}`;
            chatMessages.innerHTML = ''; // Clear previous messages
            chatInputArea.style.display = 'block';
            messageInput.focus();

            // Here you would typically fetch message history via an API call
        });
    });

    // Handle message sending
    messageForm.addEventListener('submit', function(e) {
        e.preventDefault();
        if (messageInput.value && currentRecipientId) {
            socket.emit('send_message', {
                recipient_id: currentRecipientId,
                body: messageInput.value
            });
            messageInput.value = '';
        }
    });

    // Handle incoming messages
    socket.on('new_message', function(msg) {
        // Only display the message if it's part of the current conversation
        const isChattingWithSender = msg.sender_id === currentRecipientId;
        const isMyOwnMessage = msg.sender_id === currentUserId && msg.recipient_id === currentRecipientId;

        if (isChattingWithSender || isMyOwnMessage) {
            const item = document.createElement('div');
            item.classList.add('message');
            item.textContent = msg.body;

            if (msg.sender_id === currentUserId) {
                item.classList.add('sent');
            } else {
                item.classList.add('received');
            }
            chatMessages.appendChild(item);
            chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
        }
    });
});
