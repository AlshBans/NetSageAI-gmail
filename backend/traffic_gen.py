# Simple traffic generator for testing: generates sample payloads for local testing
import time, random, json
SENDERS = ['alice@example.com','bob@example.com','mallory@bad.com','service@company.com']
SUBJECTS = ['Hello','Invoice','Important','Meeting','Urgent - Action Required','Fwd: Check this out']

def gen_one():
    s = random.choice(SENDERS)
    subj = random.choice(SUBJECTS) + ' ' + str(random.randint(1,999))
    payload = {
        'uid': 'sim-'+str(int(time.time()*1000))+'-'+str(random.randint(0,9999)),
        'ts': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'sender': s,
        'recipients': 'you@example.com',
        'subject': subj,
        'size': random.randint(500,20000),
        'attachments': random.choice([False, False, True]),
        'anomaly_score': random.choice([0.0, 0.0, 0.9])
    }
    print('Generated (for debug):', json.dumps(payload))

if __name__ == '__main__':
    for i in range(10):
        gen_one()
        time.sleep(0.2)
