import psycopg2
import psycopg2.extras
import os
import time
import bcrypt
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required. Set it to your PostgreSQL connection string.")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    return conn

def execute_query(conn, query, params=None, fetch=False, fetchone=False):
    """Helper to execute a query and return results as dicts."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(query, params or ())
    if fetchone:
        result = cur.fetchone()
        cur.close()
        return result
    if fetch:
        results = cur.fetchall()
        cur.close()
        return results
    cur.close()
    return None

def init_db():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_db()
            cur = conn.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
                    avatar_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Migrate: add avatar_url column if it doesn't exist yet
            cur.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url TEXT
            """)

            cur.execute('''
                CREATE TABLE IF NOT EXISTS content (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    author TEXT DEFAULT 'Unknown',
                    category TEXT DEFAULT 'article' CHECK(category IN ('book', 'guide', 'article', 'document')),
                    description TEXT,
                    preview_text TEXT,
                    cover_image TEXT,
                    file_path TEXT,
                    full_text TEXT,
                    page_count INTEGER DEFAULT 0,
                    price REAL DEFAULT 5000,
                    is_featured BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    phone_number TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT DEFAULT 'UGX',
                    transaction_id TEXT UNIQUE,
                    otp_code TEXT,
                    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'confirmed', 'failed')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS user_content_access (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, content_id)
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, content_id)
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS reading_progress (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    content_id INTEGER NOT NULL REFERENCES content(id),
                    progress_percent REAL DEFAULT 0,
                    last_page INTEGER DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, content_id)
                )
            ''')

            # Seed default admin
            admin_email = 'admin@lydistories.com'
            cur.execute('SELECT id FROM users WHERE email = %s', (admin_email,))
            existing = cur.fetchone()
            if not existing:
                pw_hash = bcrypt.hashpw('Lydistories2026!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute(
                    'INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)',
                    ('Admin', admin_email, pw_hash, 'admin')
                )

            # Seed sample content
            cur.execute('SELECT COUNT(*) FROM content')
            count = cur.fetchone()[0]
            if count == 0:
                samples = [
                    ("The Art of Programming", "John Smith", "book",
                     "A comprehensive guide to modern programming paradigms and best practices.",
                     "Chapter 1: Introduction to Programming\n\nProgramming is the art of telling a computer what to do...",
                     "Chapter 1: Introduction to Programming\n\nProgramming is the art of telling a computer what to do. In this comprehensive guide, we'll explore the fundamental concepts that every programmer should know.\n\nChapter 2: Variables and Data Types\n\nEvery program needs to store and manipulate data.\n\nChapter 3: Control Flow\n\nControl flow determines the order in which statements are executed.",
                     250, 15000, True),
                    ("Study Guide: Data Science Fundamentals", "Jane Doe", "guide",
                     "Master the basics of data science with this comprehensive study guide.",
                     "Module 1: Introduction to Data Science\n\nData science is a multidisciplinary field...",
                     "Module 1: Introduction to Data Science\n\nData science is a multidisciplinary field that uses scientific methods to extract knowledge from data.\n\nModule 2: Statistics for Data Science\n\nKey concepts include mean, median, mode, standard deviation.\n\nModule 3: Machine Learning\n\nTypes: Supervised, Unsupervised, Reinforcement Learning.",
                     180, 12000, True),
                    ("Understanding Cloud Computing", "Tech Weekly", "article",
                     "An in-depth article exploring the evolution and future of cloud computing technologies.",
                     "Cloud computing has revolutionized the way businesses use technology...",
                     "Cloud computing has revolutionized the way businesses use technology.\n\nTypes: IaaS, PaaS, SaaS.\n\nBenefits: Scalability, Cost efficiency, Global accessibility.",
                     30, 5000, False),
                    ("API Design Best Practices", "Developer Docs", "document",
                     "Official documentation on designing clean, maintainable, and scalable APIs.",
                     "API Design Principles\n\nA well-designed API is the cornerstone of any successful software platform...",
                     "API Design Principles\n\n1. Use RESTful Conventions\n2. Authentication & Authorization\n3. Versioning\n4. Error Handling\n5. Documentation",
                     45, 8000, False),
                    ("The History of African Literature", "Amara Okafor", "book",
                     "A journey through centuries of African literary traditions.",
                     "Part I: The Roots of African Storytelling\n\nLong before the written word reached Africa...",
                     "Part I: The Roots of African Storytelling\n\nLong before the written word reached Africa, communities passed down their histories through oral traditions.\n\nPart II: Colonial Period Literature\n\nPart III: Post-Independence Voices\n\nPart IV: Contemporary African Literature",
                     320, 18000, True),
                ]

                for title, author, category, desc, preview, full_text, pages, price, featured in samples:
                    cur.execute('''
                        INSERT INTO content (title, author, category, description, preview_text, full_text, page_count, price, is_featured)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (title, author, category, desc, preview, full_text, pages, price, featured))

            conn.commit()
            cur.close()
            conn.close()
            print("Database initialized successfully!")
            return

        except Exception as e:
            print(f"Database init attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
            else:
                print("WARNING: Could not initialize database. App will start but may not function correctly.")
                print("Make sure DATABASE_URL is correct and the database allows connections from this IP.")

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
