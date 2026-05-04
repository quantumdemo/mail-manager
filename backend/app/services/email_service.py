import os
import json
import datetime
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

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
    def fetch_metadata(creds_dict, socketio, sid, max_results=1000, months=6):
        # Enforce max_results to 1000 as requested
        max_results = min(max_results, 1000)
        print(f"Fetching Gmail metadata for sid: {sid}, max_results: {max_results}")
        creds = Credentials.from_authorized_user_info(creds_dict)
        service = build('gmail', 'v1', credentials=creds)

        # Calculate date threshold
        date_threshold = (datetime.datetime.now() - datetime.timedelta(days=months*30)).strftime('%Y/%m/%d')
        query = f'after:{date_threshold}'

        emails = []
        next_page_token = None
        count = 0
        batch_size = 50 # Reduced batch size for better responsiveness

        while count < max_results:
            limit = min(batch_size, max_results - count)
            print(f"Listing messages with limit {limit}, count so far: {count}")
            results = service.users().messages().list(
                userId='me', q=query, pageToken=next_page_token, maxResults=limit
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                print("No more messages found.")
                break

            # Use batch requests to speed up metadata fetching
            def callback(request_id, response, exception):
                nonlocal count
                if exception is not None:
                    print(f"Gmail batch callback error: {exception}")
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

                    if count % 10 == 0:
                        # Since we don't know total, we use a relative progress or just the count
                        # For now, let's keep progress relative to max_results but ensure it updates
                        progress = min(int((count / max_results) * 100), 99)
                        socketio.emit('scan_progress', {'progress': progress, 'count': count}, room=sid)

            batch = service.new_batch_http_request(callback=callback)
            for msg in messages:
                batch.add(service.users().messages().get(userId='me', id=msg['id'], format='metadata'))

            try:
                batch.execute()
            except Exception as e:
                print(f"Error executing Gmail batch: {e}")

            next_page_token = results.get('nextPageToken')
            if not next_page_token:
                break

        return emails

    @staticmethod
    def delete_messages(creds_dict, message_ids):
        creds = Credentials.from_authorized_user_info(creds_dict)
        service = build('gmail', 'v1', credentials=creds)

        # Batch move to trash (limit 1000 per request)
        for i in range(0, len(message_ids), 1000):
            batch = message_ids[i:i+1000]
            service.users().messages().batchModify(
                userId='me',
                body={
                    'ids': batch,
                    'addLabelIds': ['TRASH'],
                    'removeLabelIds': ['INBOX', 'UNREAD', 'SPAM']
                }
            ).execute()
        return True

