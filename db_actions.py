import sqlite3
import uuid

# Create db and initialize tables
def create_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    # Create topics table with id, category, topic, and created_at, published columns
    c.execute('''
        CREATE TABLE topics (
            id TEXT PRIMARY KEY,
            category TEXT NOT NULL,
            topic TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            published BOOLEAN DEFAULT FALSE
        )
    ''')

# Check if db exists
def db_exists():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        SELECT name FROM sqlite_master WHERE type='table' AND name='topics'
    ''')

    return c.fetchone() is not None

# Add a topic to the db. id is uuid, category is string, topic is string, creaetd_at is timestamp, published is boolean
def add_topic(category, topic):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    topic_id = str(uuid.uuid4())
    c.execute('''
        INSERT INTO topics (id, category, topic) VALUES (?, ?, ?)
    ''', (topic_id, category, topic))

    conn.commit()

# Get one unpublished topic from the db
def get_unpublished_topic():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        SELECT id, category, topic FROM topics WHERE published=FALSE LIMIT 1
    ''')

    return c.fetchone()


# Get all unpublished topics from the db
def get_all_unpublished_topics():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        SELECT id, category, topic FROM topics WHERE published=FALSE
    ''')

    return c.fetchall()

# Get all existing topics from the db
def get_all_topics():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        SELECT id, category, topic FROM topics
    ''')

    return c.fetchall()

# Set a topic as published
def set_topic_published(topic_id):
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()

    c.execute('''
        UPDATE topics SET published=TRUE WHERE id=?
    ''', (topic_id,))

    conn.commit()


def db_init():
    # Initialize db if it doesn't exist
    if not db_exists():
        print("Database does not exist. Initializing...")
        create_db()
        print('Database initialized')
    else:
        print('Database already exists, continuing...')