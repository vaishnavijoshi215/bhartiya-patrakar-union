import sqlite3


DATABASE = "bpu.db"


def get_db_connection():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    return conn


def init_db():

    conn = get_db_connection()


    # =========================
    # MEMBERSHIPS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS memberships (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL,

            phone TEXT NOT NULL,

            city TEXT NOT NULL,

            profession TEXT,

            message TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # =========================
    # NEWS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            category TEXT NOT NULL,

            content TEXT NOT NULL,

            image TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # =========================
    # GALLERY TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gallery (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            image TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # =========================
    # EVENTS TABLE
    # =========================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            event_date TEXT NOT NULL,

            venue TEXT NOT NULL,

            description TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
    """)


    # =========================
    # CONTACT MESSAGES TABLE
    # =========================

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


    conn.commit()

    conn.close()


if __name__ == "__main__":

    init_db()

    print("Database initialized successfully!")