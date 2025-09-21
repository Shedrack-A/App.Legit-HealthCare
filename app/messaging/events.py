from flask_socketio import emit, join_room
from flask_login import current_user
from .. import socketio, db
from ..models import Message

@socketio.on('connect')
def connect():
    if current_user.is_authenticated:
        join_room(current_user.id)
        print(f"Client connected: {current_user.first_name}, joined room: {current_user.id}")

        # If the user is an admin, also add them to the 'admins' room for notifications
        if current_user.has_permission('manage_roles'):
            join_room('admins')
            print(f"Admin user {current_user.first_name} joined 'admins' room.")

        emit('status', {'msg': f'Connected and joined room {current_user.id}'})
    else:
        # For guest users or patient portal users not handled by Flask-Login
        print("Anonymous client connected")
        emit('status', {'msg': 'Connected as guest'})


@socketio.on('disconnect')
def disconnect():
    if current_user.is_authenticated:
        print(f"Client disconnected: {current_user.first_name}")
    else:
        print("Anonymous client disconnected")

@socketio.on('send_message')
def send_message(data):
    if not current_user.is_authenticated:
        return

    recipient_id = data['recipient_id']
    body = data['body']

    msg = Message(sender_id=current_user.id, recipient_id=recipient_id, body=body)
    db.session.add(msg)
    db.session.commit()

    # Prepare message data to be sent to clients
    message_data = {
        'body': msg.body,
        'sender_id': msg.sender_id,
        'recipient_id': msg.recipient_id,
        'timestamp': msg.timestamp.isoformat() + 'Z'
    }

    # Emit to recipient's room and sender's room (so they see their own message)
    emit('new_message', message_data, room=recipient_id)
    emit('new_message', message_data, room=current_user.id)
