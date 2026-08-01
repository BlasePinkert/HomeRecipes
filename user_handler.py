
from dataclasses import dataclass, field
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    role:str
    # TODO: add post_init validation
    # def __post_init__(self):


class UsernameTaken(Exception):
    pass

class InvalidCredentials(Exception):
    pass

class UserHandler:
    def __init__(self,db_path):
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
            conn.commit()
            return User(id=cursor.lastrowid,username=username, password_hash=hashed, role=role)
        except sqlite3.IntegrityError:
            conn.rollback()
            raise UsernameTaken(f"Username '{username}' is already taken")
        finally:
            conn.close()

    def verify_credentials(self, username, password):
        conn = sqlite3.connect(self.db_path)

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, password_hash, role FROM users WHERE username = ?",
                           (username,))
            row = cursor.fetchone()
            if row is None:
                raise InvalidCredentials(f"Invalid username or password.")
            user_id, uname, stored_hash, role = row

            if not check_password_hash(stored_hash, password):
                raise InvalidCredentials(f"Invalid username or password.")

            return User(id=user_id, username=uname, password_hash= stored_hash, role=role)

        finally:
            conn.close()



