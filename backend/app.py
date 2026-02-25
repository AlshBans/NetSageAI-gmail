import os, threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from utils import wsmanager, email_to_dict
from models import init_db, SessionLocal, Email, Alert
from email_sniffer import poll_user_mail
from pydantic import BaseModel
from typing import List
import dotenv
from sqlalchemy import func
dotenv.load_dotenv()

# Ensure DB exists
init_db()

app = FastAPI(title='NetSageAI-MailGuard Backend', docs_url='/docs', redoc_url='/redoc', openapi_url='/openapi.json')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

# Per-user pollers (demo in-memory)
POLLERS = {}

class StartMonitorRequest(BaseModel):
    email: str
    password: str

@app.post('/login')
def auth_login(req: StartMonitorRequest):
    """
    Validate IMAP credentials and start a per-user poller thread (demo).
    """
    from imapclient import IMAPClient
    try:
        with IMAPClient(os.getenv('IMAP_HOST','imap.gmail.com'), port=int(os.getenv('IMAP_PORT',993)), ssl=True) as client:
            client.login(req.email, req.password)
            client.logout()
    except Exception as e:
        import traceback
        error_msg = f"IMAP login failed: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=401, detail=error_msg)

    if req.email not in POLLERS:
        stop = threading.Event()
        t = threading.Thread(target=poll_user_mail, args=(req.email, req.password, stop), daemon=True)
        POLLERS[req.email] = {'thread': t, 'stop': stop, 'password': req.password}
        t.start()
    return {'status':'ok','email':req.email}

@app.post('/api/monitor/start')
def start_monitor(req: StartMonitorRequest):
    if req.email in POLLERS:
        return {'status':'already_running'}
    stop = threading.Event()
    t = threading.Thread(target=poll_user_mail, args=(req.email, req.password, stop), daemon=True)
    POLLERS[req.email] = {'thread': t, 'stop': stop, 'password': req.password}
    t.start()
    return {'status':'started'}

@app.post('/api/monitor/stop')
def stop_monitor(email: str):
    if email not in POLLERS:
        raise HTTPException(status_code=404, detail='not found')
    POLLERS[email]['stop'].set()
    del POLLERS[email]
    return {'status':'stopping'}

@app.get('/api/emails', response_model=List[dict])
def get_emails(limit: int = 100):
    db = SessionLocal()
    rows = db.query(Email).order_by(Email.ts.desc()).limit(limit).all()
    out = [email_to_dict(r) for r in rows]
    db.close()
    return out

@app.get('/api/alerts', response_model=List[dict])
def get_alerts(limit: int = 100):
    db = SessionLocal()
    rows = db.query(Alert).order_by(Alert.ts.desc()).limit(limit).all()
    out = [{'id': r.id, 'ts': r.ts.isoformat(), 'message': r.message, 'severity': r.severity, 'email_uid': r.email_uid} for r in rows]
    db.close()
    return out

@app.get('/api/stats')
def api_stats():
    db = SessionLocal()
    total = db.query(Email).count() or 0
    anomalies = db.query(Email).filter(Email.anomaly_score >= 0.7).count() or 0
    avg_size = db.query(func.avg(Email.size)).scalar() or 0
    attach_count = db.query(Email).filter(Email.has_attachment == True).count() or 0
    top = db.query(Email.sender, func.count(Email.id).label('cnt')).group_by(Email.sender).order_by(func.count(Email.id).desc()).limit(5).all()
    top_senders = [{'sender': t[0], 'count': t[1]} for t in top]
    db.close()
    return {'total_emails': total, 'total_anomalies': anomalies, 'avg_email_size': avg_size, 'emails_with_attachments': attach_count, 'top_senders': top_senders}

@app.websocket('/ws/events')
async def ws_events(ws: WebSocket):
    await wsmanager.connect(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await wsmanager.disconnect(ws)
