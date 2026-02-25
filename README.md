# NetSageAI-MailGuard 

Real-time Gmail metadata monitoring (IMAP header-only). This  shows:
- IMAP polling (header-only)
- Rule-based detection for burst/reconnect/bulk recipients/attachments
- FastAPI backend with WebSocket events (/ws/events)
- React + Tailwind dashboard (real-time table, alerts, charts)

## Quickstart (local)

1. Backend
cd backend
python -m venv .venv
source .venv/bin/activate # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python init_db.py
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
2. Frontend
cd frontend
npm install
npm run dev

3. Open http://localhost:3000 and login with Gmail address + App Password.

Security: demo stores IMAP app password in memory for the poller. For production, implement OAuth2 and secure encrypted storage; do NOT store plaintext passwords.
