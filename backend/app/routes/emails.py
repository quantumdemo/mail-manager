from flask import Blueprint, request, jsonify, session, current_app
from .. import socketio
from ..services.email_service import GmailService, OutlookService
from ..services.ai_engine import AIRecommendationEngine
from ..utils.store import scan_store
import threading

bp = Blueprint('emails', __name__, url_prefix='/api/emails')

@bp.route('/scan', methods=['POST'])
def start_scan():
    sid = request.args.get('sid') # SocketIO session ID
    if not sid:
        return jsonify({'error': 'Missing SocketIO session ID'}), 400

    months = request.json.get('months', 6)

    # Use session ID as key for scan_store
    session_id = session.sid if hasattr(session, 'sid') else sid

    def background_scan(app_context, session_data, socket_sid, s_id):
        with app_context:
            all_emails = []

            # Gmail Scan
            if 'gmail_token' in session_data:
                try:
                    gmail_emails = GmailService.fetch_metadata(
                        session_data['gmail_token'], socketio, socket_sid, months=months
                    )
                    all_emails.extend(gmail_emails)
                except Exception as e:
                    socketio.emit('scan_error', {'provider': 'gmail', 'error': str(e)}, room=socket_sid)

            # Outlook Scan
            if 'outlook_token' in session_data:
                try:
                    outlook_emails = OutlookService.fetch_metadata(
                        session_data['outlook_token'], socketio, socket_sid, months=months
                    )
                    all_emails.extend(outlook_emails)
                except Exception as e:
                    socketio.emit('scan_error', {'provider': 'outlook', 'error': str(e)}, room=socket_sid)

            # Analysis
            recommendations = AIRecommendationEngine.analyze_emails(all_emails)
            groups = AIRecommendationEngine.group_emails(all_emails)

            # Store results in the custom store instead of thread-unsafe session
            scan_store.set(s_id, {
                'emails': all_emails,
                'recommendations': recommendations,
                'groups': groups
            })

            socketio.emit('scan_complete', {
                'total_count': len(all_emails),
                'total_size': sum(e['size'] for e in all_emails)
            }, room=socket_sid)

    thread = threading.Thread(target=background_scan, args=(
        current_app.app_context(), dict(session), sid, session_id
    ))
    thread.start()

    return jsonify({'status': 'scan_started'})

@bp.route('/data')
def get_data():
    session_id = session.sid if hasattr(session, 'sid') else None
    data = scan_store.get(session_id) if session_id else None

    if not data:
        return jsonify({'emails': [], 'groups': [], 'recommendations': {}})

    return jsonify(data)

@bp.route('/delete', methods=['POST'])
def delete_emails():
    email_ids = request.json.get('ids', [])
    provider = request.json.get('provider')

    if not email_ids:
        return jsonify({'error': 'No IDs provided'}), 400

    if provider == 'gmail' and 'gmail_token' in session:
        GmailService.delete_messages(session['gmail_token'], email_ids)
    elif provider == 'outlook' and 'outlook_token' in session:
        OutlookService.delete_messages(session['outlook_token'], email_ids)
    else:
        return jsonify({'error': 'Not authenticated for provider'}), 401

    return jsonify({'status': 'success', 'deleted_count': len(email_ids)})
