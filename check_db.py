import sys
sys.path.insert(0, 'server')
from dotenv import load_dotenv
load_dotenv('server/.env')
from database import get_db
conn = get_db()
cur = conn.cursor()
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='users' ORDER BY ordinal_position")
cols = [r[0] for r in cur.fetchall()]
cur.close()
conn.close()
print('Users table columns:', cols)
assert 'avatar_url' in cols, 'avatar_url column MISSING!'
print('OK - avatar_url column exists in DB')
