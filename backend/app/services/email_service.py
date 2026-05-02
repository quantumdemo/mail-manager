import os
import json
import datetime
import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import msal

class GmailService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]

    @staticmethod
    def get_flow(state=None):
        client_config = {
            "web": {
                "client_id": os.getenv("GMAIL_CLIENT_ID"),
                "client_secret": os.getenv("GMAIL_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [os.getenv("REDIRECT_URI")]
            }
        }
        return Flow.from_client_config(
            client_config,
            scopes=GmailService.SCOPES,
            redirect_uri=os.getenv("REDIRECT_URI"),
            state=state
        )

    @staticmethod
    def fetch_metadata(creds_dict, socketio, sid, max_results=10000, months=6):
        creds = Credentials.from_authorized_user_info(creds_dict)
        service = build('gmail', 'v1', credentials=creds)

        # Calculate date threshold
        date_threshold = (datetime.datetime.now() - datetime.timedelta(days=months*30)).strftime('%Y/%m/%d')
        query = f'after:{date_threshold}'

        emails = []
        next_page_token = None
        count = 0

        while count < max_results:
            results = service.users().messages().list(
                userId='me', q=query, pageToken=next_page_token, maxResults=min(500, max_results - count)
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                break

            # Use batch requests to speed up metadata fetching
            def callback(request_id, response, exception):
                nonlocal count
                if exception is not None:
                    # Handle error
                    pass
                else:
                    headers = response.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

                    emails.append({
                        'id': response['id'],
                        'threadId': response['threadId'],
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'size': response.get('sizeEstimate', 0),
                        'provider': 'gmail'
                    })
                    count += 1

                    if count % 20 == 0:
                        progress = int((count / max_results) * 100)
                        socketio.emit('scan_progress', {'progress': progress, 'count': count}, room=sid)

            batch = service.new_batch_http_request(callback=callback)
            for msg in messages:
                batch.add(service.users().messages().get(userId='me', id=msg['id'], format='metadata'))

            batch.execute()

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        return emails

    @staticmethod
    def delete_messages(creds_dict, message_ids):
        creds = Credentials.from_authorized_user_info(creds_dict)
        service = build('gmail', 'v1', credentials=creds)
        for msg_id in message_ids:
            service.users().messages().trash(userId='me', id=msg_id).execute()
        return True

class OutlookService:
    SCOPES = ['Mail.Read', 'Mail.ReadWrite', 'Mail.Send']
    AUTHORITY = "https://login.microsoftonline.com/common"

    @staticmethod
    def get_msal_app():
        return msal.ConfidentialClientApplication(
            os.getenv("OUTLOOK_CLIENT_ID"),
            authority=OutlookService.AUTHORITY,
            client_credential=os.getenv("OUTLOOK_CLIENT_SECRET")
        )

    @staticmethod
    def fetch_metadata(token, socketio, sid, max_results=10000, months=6):
        # Implementation using requests to Microsoft Graph API
        headers = {'Authorization': f'Bearer {token}'}
        date_threshold = (datetime.datetime.now() - datetime.timedelta(days=months*30)).isoformat() + "Z"

        url = f"https://graph.microsoft.com/v1.0/me/messages?$filter=receivedDateTime ge {date_threshold}&$select=id,subject,from,receivedDateTime,size&$top=500"

        emails = []
        count = 0

        while url and count < max_results:
            response = requests.get(url, headers=headers).json()
            messages = response.get('value', [])

            for msg in messages:
                sender = msg.get('from', {}).get('emailAddress', {}).get('address', 'Unknown')
                emails.append({
                    'id': msg['id'],
                    'subject': msg.get('subject', 'No Subject'),
                    'sender': sender,
                    'date': msg.get('receivedDateTime', ''),
                    'size': msg.get('size', 0),
                    'provider': 'outlook'
                })
                count += 1

                if count % 20 == 0:
                    progress = int((count / max_results) * 100)
                    socketio.emit('scan_progress', {'progress': progress, 'count': count}, room=sid)

            url = response.get('@odata.nextLink')
            if not url:
                break

        return emails

    @staticmethod
    def delete_messages(token, message_ids):
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        for msg_id in message_ids:
            requests.post(f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}/trash", headers=headers)
        return True
