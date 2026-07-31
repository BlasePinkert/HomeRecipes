import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data"/ "recipes.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

def init_db():
    #read schema file
    schema_sql = SCHEMA_PATH.read_text()

    #connect (creates .db file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.executescript(schema_sql)    #run all CREATE TABLE stmts
        conn.commit()                       #make the schema permanent
        print(f"Database Initialized at {DB_PATH}")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        print(cursor.fetchall())
    finally:
        conn.close()                        #always closes connection, even if something fails

if __name__ == "__main__":
    init_db()