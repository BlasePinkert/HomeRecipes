from pathlib import Path
from user_handler import UserHandler, UsernameTaken
import getpass

password = getpass.getpass("Admin Password: ")
username = input("Admin Username: ")

DB_PATH = Path(__file__).parent / "data"/ "recipes.db"
handler = UserHandler(str(DB_PATH))
try:
    handler.create_user(username, password, role="admin")
    print("Admin user created")
except UsernameTaken:
    print("Admin user already exists")
