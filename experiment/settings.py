from os import environ
import sqlite3
from pathlib import Path
import random

environ.setdefault('OTREE_DATABASE_URL', 'sqlite:///db.sqlite3?timeout=60')


def _init_sqlite_wal_mode():
    db_url = environ.get('OTREE_DATABASE_URL', '')
    if not db_url.startswith('sqlite:///'):
        return

    db_path = db_url.replace('sqlite:///', '', 1).split('?', 1)[0]
    if not db_path:
        return

    abs_db_path = Path(__file__).resolve().parent / db_path
    try:
        conn = sqlite3.connect(str(abs_db_path), timeout=60)
        conn.execute('PRAGMA journal_mode=WAL;')
        conn.execute('PRAGMA synchronous=NORMAL;')
        conn.execute('PRAGMA busy_timeout=60000;')
        conn.close()
    except Exception as exc:
        print(f"[DB_INIT_WARN] Failed to enable SQLite WAL mode: {exc}")


_init_sqlite_wal_mode()

app_sequence = [
    'instruction',
    'manager_y1',
    'svo_investor',
    'investor_y1',
    'manager_y2',
    'investor_y2',
    'manager_y3',
    'investor_y3',
    'svo_manager',
    'questionnaire'
]


SESSION_CONFIG_DEFAULTS = dict(real_world_currency_per_point=0.25, participation_fee=5)
SESSION_CONFIGS = [dict(name='games', num_demo_participants=2, app_sequence=app_sequence)]
LANGUAGE_CODE = 'zh-hans'
REAL_WORLD_CURRENCY_CODE = 'CNY'
USE_POINTS = True
DEMO_PAGE_INTRO_HTML = ''
PARTICIPANT_FIELDS = ['role','treatment','manager_task','investpayoff','svopayoff']
DEBUG = False
ROOMS = [
    dict(
        name='HumanwithGPT',
        display_name='HumanwithGPT',
        #use_secure_url = True
        participant_label_file='_rooms/jointhegame.example.txt',  #if you don't want to assign a particular number to participants and more security, this can be neglected #if you want everyone to enter a label, just use the url
    ),
    dict(
        name='econ_lab',
        display_name='Experimental Economics Lab'
    ),  #another room name, no true meaning
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

SECRET_KEY = environ.get('OTREE_SECRET_KEY', 'development-only-change-me')

# if an app is included in SESSION_CONFIGS, you don't need to list it here
INSTALLED_APPS = ['otree']


#['general_instruction','ug1','tg1','pd1','ug2','tg2','pd2','ug3','tg3','pd3','ug4','tg4','pd4','ug5','tg5','pd5','ug6','tg6','pd6','after_survey']