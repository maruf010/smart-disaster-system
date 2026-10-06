import sqlite3
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS disasters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        area TEXT NOT NULL,
        severity TEXT NOT NULL,
        affected_people INTEGER DEFAULT 0,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS emergency_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disaster_id INTEGER,
        requester_name TEXT,
        location TEXT NOT NULL,
        emergency_type TEXT NOT NULL,
        people_affected INTEGER DEFAULT 0,
        injured INTEGER DEFAULT 0,
        children_elderly INTEGER DEFAULT 0,
        life_threat INTEGER DEFAULT 0,
        resource_shortage INTEGER DEFAULT 0,
        priority_score INTEGER DEFAULT 0,
        priority_level TEXT,
        status TEXT DEFAULT 'PENDING',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(disaster_id) REFERENCES disasters(id)
    );

    CREATE TABLE IF NOT EXISTS shelters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        occupied INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        quantity REAL DEFAULT 0,
        unit TEXT NOT NULL,
        minimum_stock REAL DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS rescue_teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        specialization TEXT NOT NULL,
        members INTEGER DEFAULT 0,
        current_location TEXT NOT NULL,
        status TEXT DEFAULT 'AVAILABLE',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS volunteers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        skill TEXT NOT NULL,
        location TEXT NOT NULL,
        contact TEXT,
        availability TEXT DEFAULT 'YES',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS roads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        from_location TEXT NOT NULL,
        to_location TEXT NOT NULL,
        distance REAL NOT NULL,
        status TEXT DEFAULT 'OPEN'
    );

    CREATE TABLE IF NOT EXISTS resource_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resource_id INTEGER,
        area TEXT NOT NULL,
        population INTEGER NOT NULL,
        allocated_quantity REAL NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(resource_id) REFERENCES resources(id)
    );
    """)

    # default admin
    cur.execute("SELECT COUNT(*) AS c FROM users")
    if cur.fetchone()["c"] == 0:
        cur.execute(
            "INSERT INTO users (username,password,role) VALUES (?,?,?)",
            ("admin", "admin123", "ADMIN")
        )

    # sample roads
    cur.execute("SELECT COUNT(*) AS c FROM roads")
    if cur.fetchone()["c"] == 0:
        roads = [
            ("A", "B", 4, "OPEN"),
            ("A", "C", 2, "OPEN"),
            ("B", "D", 3, "OPEN"),
            ("C", "D", 2, "OPEN"),
            ("B", "C", 2, "OPEN"),
        ]
        cur.executemany(
            "INSERT INTO roads(from_location,to_location,distance,status) VALUES (?,?,?,?)",
            roads
        )

    # Safe migrations for existing databases
    def ensure_column(table_name, col_name, col_def, fill_timestamp=False):
        cols = [c[1] for c in cur.execute(f"PRAGMA table_info({table_name})").fetchall()]
        if col_name not in cols:
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}")
            if fill_timestamp:
                cur.execute(f"UPDATE {table_name} SET {col_name} = CURRENT_TIMESTAMP WHERE {col_name} IS NULL OR {col_name} = ''")

    ensure_column("users", "full_name", "TEXT DEFAULT ''")
    ensure_column("users", "phone", "TEXT DEFAULT ''")
    ensure_column("emergency_requests", "user_id", "INTEGER DEFAULT NULL")
    ensure_column("emergency_requests", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("disasters", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("shelters", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("resources", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("rescue_teams", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("volunteers", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)
    ensure_column("resource_allocations", "created_at", "TEXT DEFAULT ''", fill_timestamp=True)

    conn.commit()
    conn.close()
