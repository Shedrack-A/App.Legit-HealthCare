from flask import render_template
from flask_login import login_required, current_user
from app.messaging import messaging
from app.models import User

@messaging.route('/')
@login_required
def index():
    # Exclude current user from the list of users to chat with
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('messaging/chat.html', users=users)
