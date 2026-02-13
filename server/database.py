import psycopg2
import psycopg2.extras
import os
import bcrypt

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
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user' CHECK(role IN ('user', 'admin')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

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
             "Chapter 1: Introduction to Programming\n\nProgramming is the art of telling a computer what to do. In this comprehensive guide, we'll explore the fundamental concepts that every programmer should know...\n\nFrom variables and data types to complex algorithms and design patterns, this book covers it all in an accessible and engaging way.",
             "Chapter 1: Introduction to Programming\n\nProgramming is the art of telling a computer what to do. In this comprehensive guide, we'll explore the fundamental concepts that every programmer should know.\n\nFrom variables and data types to complex algorithms and design patterns, this book covers it all in an accessible and engaging way.\n\nChapter 2: Variables and Data Types\n\nEvery program needs to store and manipulate data. Variables are the containers that hold this data, and understanding data types is crucial for writing efficient code.\n\nPrimitive Types:\n- Integers: whole numbers like 1, 42, -7\n- Floats: decimal numbers like 3.14, 2.718\n- Strings: text like 'Hello, World!'\n- Booleans: true or false values\n\nChapter 3: Control Flow\n\nControl flow determines the order in which statements are executed. The three main control flow structures are:\n\n1. Sequential: statements execute one after another\n2. Conditional: if-else statements that branch based on conditions\n3. Loops: repeating blocks of code\n\nChapter 4: Functions\n\nFunctions are reusable blocks of code that perform a specific task. They help organize code and reduce repetition.\n\nChapter 5: Object-Oriented Programming\n\nOOP is a programming paradigm that organizes code into objects that contain data and behavior.",
             250, 15000, True),
            ("Study Guide: Data Science Fundamentals", "Jane Doe", "guide",
             "Master the basics of data science with this comprehensive study guide covering statistics, machine learning, and data visualization.",
             "Module 1: Introduction to Data Science\n\nData science is a multidisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge from data...\n\nThis study guide will take you from beginner to competent in the core areas of data science.",
             "Module 1: Introduction to Data Science\n\nData science is a multidisciplinary field that uses scientific methods, processes, algorithms, and systems to extract knowledge from data.\n\nThis study guide covers:\n- Statistical foundations\n- Data cleaning and preprocessing\n- Machine learning basics\n- Data visualization techniques\n\nModule 2: Statistics for Data Science\n\nUnderstanding statistics is fundamental to data science. Key concepts include:\n\nDescriptive Statistics:\n- Mean, median, mode\n- Standard deviation and variance\n- Percentiles and quartiles\n\nInferential Statistics:\n- Hypothesis testing\n- Confidence intervals\n- Regression analysis\n\nModule 3: Machine Learning\n\nMachine learning is a subset of AI that enables systems to learn from data.\n\nTypes of ML:\n1. Supervised Learning\n2. Unsupervised Learning\n3. Reinforcement Learning",
             180, 12000, True),
            ("Understanding Cloud Computing", "Tech Weekly", "article",
             "An in-depth article exploring the evolution and future of cloud computing technologies.",
             "Cloud computing has revolutionized the way businesses and individuals use technology. From simple file storage to complex AI workloads...\n\nThis article explores the history, current state, and future of cloud computing.",
             "Cloud computing has revolutionized the way businesses and individuals use technology.\n\nThe Evolution of Cloud Computing:\n\n1960s-1990s: The concept of utility computing emerged, where computing resources would be provided as a metered service.\n\n2000s: Amazon Web Services launched, marking the beginning of modern cloud computing.\n\n2010s: Cloud adoption exploded with services like Google Cloud, Microsoft Azure, and countless SaaS applications.\n\n2020s: Edge computing, serverless architectures, and AI-powered cloud services became mainstream.\n\nTypes of Cloud Services:\n\n1. IaaS (Infrastructure as a Service)\n2. PaaS (Platform as a Service)\n3. SaaS (Software as a Service)\n\nBenefits of Cloud Computing:\n- Scalability\n- Cost efficiency\n- Global accessibility\n- Automatic updates",
             30, 5000, False),
            ("API Design Best Practices", "Developer Docs", "document",
             "Official documentation on designing clean, maintainable, and scalable APIs for modern applications.",
             "API Design Principles\n\nA well-designed API is the cornerstone of any successful software platform...\n\nThis document covers RESTful design, authentication patterns, and versioning strategies.",
             "API Design Principles\n\nA well-designed API is the cornerstone of any successful software platform.\n\n1. Use RESTful Conventions\n- Use nouns for resources: /users, /products\n- Use HTTP methods: GET, POST, PUT, DELETE\n- Return appropriate status codes\n\n2. Authentication & Authorization\n- Use OAuth 2.0 or JWT tokens\n- Implement role-based access control\n- Always use HTTPS\n\n3. Versioning\n- Use URL versioning: /api/v1/users\n- Maintain backward compatibility\n- Deprecate old versions gracefully\n\n4. Error Handling\n- Return consistent error formats\n- Include error codes and messages\n- Provide helpful debugging information\n\n5. Documentation\n- Use OpenAPI/Swagger specifications\n- Include request/response examples\n- Document all query parameters",
             45, 8000, False),
            ("The History of African Literature", "Amara Okafor", "book",
             "A journey through centuries of African literary traditions, from oral storytelling to modern novels.",
             "Part I: The Roots of African Storytelling\n\nLong before the written word reached the African continent, communities passed down their histories, values, and wisdom through oral traditions...\n\nThis book celebrates the richness and diversity of African literary heritage.",
             "Part I: The Roots of African Storytelling\n\nLong before the written word reached the African continent, communities passed down their histories, values, and wisdom through oral traditions.\n\nThe griots of West Africa, the storytellers of East Africa, and the praise singers of Southern Africa all played crucial roles in preserving cultural memory.\n\nPart II: Colonial Period Literature\n\nThe introduction of European languages and education systems created a new form of African literature. Writers like Chinua Achebe, Ngugi wa Thiong'o, and Wole Soyinka used the colonizer's language to tell African stories.\n\nPart III: Post-Independence Voices\n\nAfter independence, African writers grappled with themes of identity, nation-building, and the legacy of colonialism.\n\nPart IV: Contemporary African Literature\n\nToday, African literature thrives globally with authors like Chimamanda Ngozi Adichie, Yaa Gyasi, and Petina Gappah reaching worldwide audiences.",
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

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
