python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
python init_db.py
set PYTHONPATH=.
uvicorn app:app --reload --host 0.0.0.0 --port 8000
