import os, time, json
from imapclient import IMAPClient
from email import message_from_bytes
from models import SessionLocal, Email
from detector import analyze_and_maybe_alert
from utils import wsmanager, email_to_dict
from datetime import datetime

IMAP_HOST = os.getenv('IMAP_HOST','imap.gmail.com')
IMAP_PORT = int(os.getenv('IMAP_PORT','993'))
POLL_SEC = int(os.getenv('IMAP_POLL_SECONDS','8'))
MAX_LOOKBACK = int(os.getenv('IMAP_MAX_LOOKBACK','300'))

def safe_decode(header_val):
    if not header_val:
        return ''
    try:
        from email.header import decode_header
        parts = decode_header(header_val)
        return ' '.join([ (p.decode(enc or 'utf-8') if isinstance(p, bytes) else p) for p,enc in parts ])
    except Exception:
        return str(header_val)

def poll_user_mail(email_addr: str, password: str, stop_event):
    """
    Long-running poller. For demo it logs in with IMAP app password,
    fetches header-only data and inserts into SQLite DB.
    """
    while not stop_event.is_set():
        try:
            with IMAPClient(IMAP_HOST, port=IMAP_PORT, ssl=True) as client:
                client.login(email_addr, password)
                client.select_folder('INBOX')
                uids = client.search(['ALL'])
                recent = uids[-MAX_LOOKBACK:]
                db = SessionLocal()
                for uid in recent:
                    exists = db.query(Email).filter(Email.uid == str(uid)).first()
                    if exists:
                        continue
                    resp = client.fetch([uid], ['RFC822.SIZE', 'RFC822.HEADER'])
                    data = resp.get(uid)
                    raw_header = data.get(b'RFC822.HEADER') or data.get('RFC822.HEADER') or b''
                    if not raw_header:
                        continue
                    if isinstance(raw_header, str):
                        raw_header = raw_header.encode('utf-8', errors='ignore')
                    msg = message_from_bytes(raw_header)
                    sender = safe_decode(msg.get('From'))
                    to = safe_decode(msg.get('To'))
                    subject = safe_decode(msg.get('Subject'))
                    date_hdr = msg.get('Date')
                    try:
                        from email.utils import parsedate_to_datetime
                        ts = parsedate_to_datetime(date_hdr)
                    except Exception:
                        ts = datetime.utcnow()
                    has_attachment = 'multipart' in str(msg.get_content_type()).lower()
                    size = int(data.get(b'RFC822.SIZE', 0) or data.get('RFC822.SIZE', 0) or 0)
                    new_email = Email(uid=str(uid), ts=ts, sender=sender, recipients=to or '', subject=subject or '', size=size, has_attachment=bool(has_attachment), meta=json.dumps({'fetched_by':'imap'}))
                    db.add(new_email)
                    db.commit()
                    db.refresh(new_email)
                    analyze_and_maybe_alert(new_email)
                    try:
                        import asyncio
                        asyncio.get_event_loop().create_task(wsmanager.broadcast({'type':'email', 'email': email_to_dict(new_email)}))
                    except Exception:
                        pass
                db.close()
                client.logout()
        except Exception as e:
            print('imap poll error:', e)
        time.sleep(POLL_SEC)
