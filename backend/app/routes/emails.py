from flask import Blueprint, request, jsonify, session, current_app
from .. import socketio
from ..services.email_service import GmailService
from ..services.ai_engine import AIRecommendationEngine
from ..utils.store import scan_store
import threading

bp = Blueprint('emails', __name__, url_prefix='/api/emails')

active_scans = set()

@bp.route('/scan', methods=['POST'])
def start_scan():
    sid = request.args.get('sid') # SocketIO session ID
    if not sid:
        return jsonify({'error': 'Missing SocketIO session ID'}), 400

    months = request.json.get('months', 6)

    # Use session ID as key for scan_store
    session_id = session.sid if hasattr(session, 'sid') else sid

    if session_id in active_scans:
        return jsonify({'error': 'Scan already in progress'}), 409

    def background_scan(app_context, session_data, socket_sid, s_id, scan_months):
        print(f"Starting background scan for SID: {socket_sid}")
        try:
            with app_context:
                all_emails = []

                # Gmail Scan
                if 'gmail_token' in session_data:
                    print(f"Fetching Gmail metadata for {socket_sid}")
                    try:
                        gmail_emails = GmailService.fetch_metadata(
                            session_data['gmail_token'], socketio, socket_sid, months=scan_months
                        )
                        all_emails.extend(gmail_emails)
                        print(f"Fetched {len(gmail_emails)} emails from Gmail")
                    except Exception as e:
                        print(f"Gmail fetch error: {e}")
                        socketio.emit('scan_error', {'provider': 'gmail', 'error': str(e)}, room=socket_sid)

                # Analysis
                print(f"Analyzing {len(all_emails)} total emails")
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
        except Exception as e:
            print(f"Global background scan error: {e}")
            socketio.emit('scan_error', {'provider': 'system', 'error': str(e)}, room=socket_sid)
        finally:
            if s_id in active_scans:
                active_scans.remove(s_id)

    active_scans.add(session_id)
    socketio.start_background_task(background_scan,
        current_app.app_context(), dict(session), sid, session_id, months
    )

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
    else:
        return jsonify({'error': 'Not authenticated for provider or unsupported provider'}), 401

    return jsonify({'status': 'success', 'deleted_count': len(email_ids)})
