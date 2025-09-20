from flask import request, jsonify, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from flask import session
from app import db, socketio
from app.requests import requests_bp
from app.models import AccessRequest, Permission, TemporaryAccessCode
from app.decorators import permission_required
from datetime import datetime, UTC, timedelta
import secrets

@requests_bp.route('/request_access', methods=['POST'])
@login_required
def request_access():
    data = request.get_json()
    permission_name = data.get('permission')

    if not permission_name:
        return jsonify({'error': 'Permission name is required'}), 400

    permission = Permission.query.filter_by(name=permission_name).first()
    if not permission:
        return jsonify({'error': 'Permission not found'}), 404

    # Check if a pending request already exists
    existing_request = AccessRequest.query.filter_by(
        user_id=current_user.id,
        permission_id=permission.id,
        status='pending'
    ).first()

    if existing_request:
        return jsonify({'message': 'You have already requested access for this permission.'}), 200

    new_request = AccessRequest(
        user_id=current_user.id,
        permission_id=permission.id
    )
    db.session.add(new_request)
    db.session.commit()

    socketio.emit('new_access_request', {
        'request_id': new_request.id,
        'requester': new_request.user.username,
        'permission': new_request.permission.name,
        'timestamp': new_request.request_timestamp.isoformat()
    }, namespace='/')

    return jsonify({'message': 'Access request submitted successfully.'}), 201

@requests_bp.route('/manage', methods=['GET'])
@login_required
@permission_required('manage_access_requests')
def manage_requests():
    requests = AccessRequest.query.filter_by(status='pending').order_by(AccessRequest.request_timestamp.desc()).all()
    return render_template('requests/manage.html', requests=requests)

@requests_bp.route('/manage/<int:request_id>/<action>', methods=['POST'])
@login_required
@permission_required('manage_access_requests')
def action_request(request_id, action):
    req = AccessRequest.query.get_or_404(request_id)

    if action == 'approve':
        req.status = 'approved'
        req.approved_by_id = current_user.id
        req.approved_timestamp = datetime.now(UTC)

        expiry_time = datetime.now(UTC) + timedelta(hours=1)
        temp_code = TemporaryAccessCode(
            code=secrets.token_urlsafe(16),
            permission_id=req.permission_id,
            user_id=req.user_id,
            expiry_time=expiry_time,
            is_single_use=False
        )
        db.session.add(temp_code)

        if 'temp_permissions' not in session:
            session['temp_permissions'] = {}
        session['temp_permissions'][req.permission.name] = expiry_time.isoformat()
        session.modified = True
    elif action == 'deny':
        req.status = 'denied'
    else:
        flash('Invalid action.', 'danger')
        return redirect(url_for('requests.manage_requests'))

    db.session.commit()

    socketio.emit('access_request_status_changed', {
        'request_id': req.id,
        'status': req.status,
        'permission': req.permission.name,
        'approver': req.approved_by.username if req.approved_by else None
    }, room=str(req.user_id))

    flash(f'Request has been {req.status}.', 'success')
    return redirect(url_for('requests.manage_requests'))
