import os
from datetime import timedelta
from models import Email, Alert, SessionLocal

# Configurable thresholds (env overrides)
BURST_COUNT = int(os.getenv('BURST_COUNT','8'))
BURST_WINDOW_SEC = int(os.getenv('BURST_WINDOW_SEC','30'))
RECONNECT_INACTIVITY = int(os.getenv('RECONNECT_INACTIVITY','300'))

def run_rules_and_score(email_obj, db):
    """
    Rule-based scoring:
      - Burst detection: N emails in last window -> high
      - Reconnect burst: long inactivity then many messages -> medium
      - Bulk recipients -> small bump
      - Attachment -> small bump
    Updates email_obj.anomaly_score and writes Alert rows when triggered.
    """
    score = 0.0

    # 1) Burst detection
    window_start = email_obj.ts - timedelta(seconds=BURST_WINDOW_SEC)
    burst_count = db.query(Email).filter(Email.ts >= window_start).count()
    if burst_count >= BURST_COUNT:
        score += 0.7
        msg = f'Burst detected: {burst_count} emails in last {BURST_WINDOW_SEC}s'
        db.add(Alert(email_uid=email_obj.uid, severity='high', message=msg))
        db.commit()

    # 2) Reconnect burst detection
    prev = db.query(Email).filter(Email.ts < email_obj.ts).order_by(Email.ts.desc()).first()
    if prev:
        gap = (email_obj.ts - prev.ts).total_seconds()
        if gap >= RECONNECT_INACTIVITY:
            after_end = email_obj.ts + timedelta(seconds=60)
            after_count = db.query(Email).filter(Email.ts >= email_obj.ts, Email.ts <= after_end).count()
            if after_count >= max(3, BURST_COUNT // 2):
                score += 0.6
                db.add(Alert(email_uid=email_obj.uid, severity='medium', message=f'Reconnect burst: {after_count} emails after inactivity {int(gap)}s'))
                db.commit()

    # 3) Bulk recipients
    if email_obj.recipients and email_obj.recipients.count(',') >= 10:
        score += 0.2

    # 4) Attachments
    if email_obj.has_attachment:
        score += 0.15

    if score > 1.0:
        score = 1.0

    email_obj.anomaly_score = score
    db.add(email_obj)
    db.commit()
    return score

def analyze_and_maybe_alert(email_obj):
    db = SessionLocal()
    try:
        return run_rules_and_score(email_obj, db)
    finally:
        db.close()
