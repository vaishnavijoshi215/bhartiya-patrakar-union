import sqlite3
import os

# =========================================================
# DATABASE PATH
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "bpu.db")


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():

    conn = get_db_connection()

    # -----------------------------------------------------
    # MEMBERSHIPS TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            city TEXT,
            profession TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # NEWS TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # GALLERY TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # EVENTS TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            event_date TEXT NOT NULL,
            location TEXT,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # CONTACT MESSAGES TABLE
    # -----------------------------------------------------

    conn.execute("""
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Save changes
    conn.commit()

    # Close database
    conn.close()


# =========================================================
# LOCAL TEST
# =========================================================

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")