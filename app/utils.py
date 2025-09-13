from app import db
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
