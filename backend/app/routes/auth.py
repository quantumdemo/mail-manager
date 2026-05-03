from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
import os
from ..services.email_service import GmailService

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/status')
def status():
    return jsonify({
        'gmail_authenticated': 'gmail_token' in session
    })

@bp.route('/gmail/login')
def gmail_login():
    try:
        flow = GmailService.get_flow()
        auth_url, state = flow.authorization_url(prompt='consent')
        session['gmail_state'] = state
        return jsonify({'url': auth_url})
    except Exception as e:
        current_app.logger.error(f"Gmail login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/gmail/callback')
def gmail_callback():
    state = session.get('gmail_state')
    flow = GmailService.get_flow(state=state)

    # Fix for oauthlib which sometimes strictly requires https
    # even if OAUTHLIB_INSECURE_TRANSPORT is set, depending on the environment.
    # Or more importantly, ensuring the callback URL matches what Google expects.
    callback_url = request.url
    if callback_url.startswith('http://') and not os.getenv('DEVELOPMENT'):
         # In production we should always be using https
         pass

    flow.fetch_token(authorization_response=callback_url)

    creds = flow.credentials
    session['gmail_token'] = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    return redirect(os.getenv('FRONTEND_URL', 'http://localhost:5173') + '/dashboard')


@bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'success'})
