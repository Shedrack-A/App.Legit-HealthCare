import re
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import db, mail
from app.models import AuditLog
from flask_login import current_user

def log_audit(action, details=None):
    """
    Helper function to create and save an audit log record.
    """
    try:
        user_id = current_user.id if current_user.is_authenticated else None
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # In a real application, you'd want more robust error handling,
        # perhaps logging the error to a file instead of just printing.
        print(f"Error logging audit trail: {e}")
        db.session.rollback()

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

def is_password_strong(password):
    """
    Checks if a password meets the strength requirements.
    - At least 10 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special symbol
    """
    if len(password) < 10:
        return False, "Password must be at least 10 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*()\[\]{};:,./<>?~`_+=|-]", password):
        return False, "Password must contain at least one special symbol."
    return True, ""
