import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(dotenv_path='server/.env')

url = os.environ.get('DATABASE_URL')
print(f"Testing connection to: {url}")

try:
    conn = psycopg2.connect(url, connect_timeout=10)
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
