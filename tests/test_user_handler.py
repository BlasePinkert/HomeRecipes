from user_handler import User, InvalidCredentials, UsernameTaken, UserHandler
from pathlib import Path
import pytest
import sqlite3

SCHEMA = Path(__file__).parent.parent / "schema.sql"

@pytest.fixture
def empty_users(tmp_path):
    db_path = tmp_path / "test.db"

    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA.read_text())
    conn.commit()
    conn.close()
    user_handler = UserHandler(str(db_path))

    return user_handler

def test_create_user(empty_users):
    new_username="NewUser"
    new_pw =")OKM9ijn"
    new = empty_users.create_user(new_username,new_pw)

    assert new.id == 1
    assert new.username == "NewUser"
    assert new.role =="user"


def test_dup_username(empty_users):
    empty_users.create_user("testUser", "1234")
    with pytest.raises(UsernameTaken):
        empty_users.create_user("testUser","1234")

def test_validate_creds(empty_users):
    empty_users.create_user("testUser1", "123456")
    empty_users.create_user("testUser2", "12345")
    empty_users.create_user("testUser3", "1234")
    validated = empty_users.verify_credentials("testUser3","1234")
    assert validated.id == 3
    assert validated.username == "testUser3"
    assert validated.role == "user"

def test_invalid_creds_username(empty_users):
    empty_users.create_user("testUser1", "123456")
    empty_users.create_user("testUser2", "12345")
    empty_users.create_user("testUser3", "1234")
    with pytest.raises(InvalidCredentials):
        empty_users.verify_credentials("testUser4","4321")

def test_invalid_creds_pw(empty_users):
    empty_users.create_user("testUser1", "123456")
    empty_users.create_user("testUser2", "12345")
    empty_users.create_user("testUser3", "1234")
    with pytest.raises(InvalidCredentials):
        empty_users.verify_credentials("testUser3","4321")

# @pytest.fixture
# def seeded_users(tmp_path):
#     db_path = tmp_path / "test.db"
#
#     conn = sqlite3.connect(db_path)
#     conn.executescript(SCHEMA.read_text())
#     conn.commit()
#     conn.close()
#     user_handler = UserHandler(str(db_path))
#     users = [
#         user_handler.create_user("testUser","!QAZ2wsx","user"),
#         #user_handler.create_user("testAdmin","admin","admin")
#     ]
#
#     return user_handler, users