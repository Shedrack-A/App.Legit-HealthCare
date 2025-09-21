from flask_login import current_user
from app.models import TemporaryAccessCode
from datetime import datetime, UTC

def inject_temp_code():
    if current_user.is_authenticated:
        active_code = TemporaryAccessCode.query.filter_by(
            user_id=current_user.id,
            is_active=True
        ).first()

        if active_code and active_code.expiry_time > datetime.now(UTC):
            return dict(active_temp_code=active_code)

    return dict(active_temp_code=None)
