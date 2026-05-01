from flask import Blueprint, request, jsonify, session, redirect, url_for, current_app
import os
from ..services.email_service import GmailService, OutlookService

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/status')
def status():
    return jsonify({
        'gmail_authenticated': 'gmail_token' in session,
        'outlook_authenticated': 'outlook_token' in session
    })

@bp.route('/gmail/login')
def gmail_login():
    flow = GmailService.get_flow()
    auth_url, state = flow.authorization_url(prompt='consent')
    session['gmail_state'] = state
    return jsonify({'url': auth_url})

@bp.route('/gmail/callback')
def gmail_callback():
    state = session.get('gmail_state')
    flow = GmailService.get_flow()
    flow.fetch_token(authorization_response=request.url)

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

@bp.route('/outlook/login')
def outlook_login():
    msal_app = OutlookService.get_msal_app()
    auth_url = msal_app.get_authorization_request_url(OutlookService.SCOPES)
    return jsonify({'url': auth_url})

@bp.route('/outlook/callback')
def outlook_callback():
    code = request.args.get('code')
    if not code:
        return "No code provided", 400

    msal_app = OutlookService.get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(code, scopes=OutlookService.SCOPES)

    if "error" in result:
        return f"Error: {result.get('error_description')}", 400

    session['outlook_token'] = result['access_token']
    return redirect(os.getenv('FRONTEND_URL', 'http://localhost:5173') + '/dashboard')

@bp.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'success'})
