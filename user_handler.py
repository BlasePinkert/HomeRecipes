from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


class User:
    id: int
    username: str
    password_hash: str
    role:str

class UsernameTaken(Exception):
    pass

class UserHandler:
    def __init(self,db_path):
        self.db_path = db_path

    def create_user(self, username, password, role='user'):
        conn = sqlite3.connect(self.db_path)
        try:
            hashed = generate_password_hash(password)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users(username, password_hash, role) VALUES (?,?,?)",
                (username, hashed, role)
            )
        except Exception:
            conn.rollback()
            raise UsernameTaken
        finally:
            conn.close()


    def verify_credentials(self, username, password):
        conn = sqlite3.connect(self.db_path)
        hashed = generate_password_hash(password)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ? and password_hash = ?",
                           (username, hashed))
            #todo If user doesn't exist verification fails
            #if found true/false


