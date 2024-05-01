import json
import sqlite3


DATABASE_PATH = '/home/fresnogo/Desktop/mininet_ocpp/charging/db.sqlite3'


_db = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
_db.execute('PRAGMA foreign_keys=ON;')

# Create DB and schema if it doesn't exist already
_db.execute("""
CREATE TABLE IF NOT EXISTS Events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT current_timestamp,
    target VARCHAR(255) NOT NULL DEFAULT '*',
    data text NOT NULL
);
""")

_db.execute("""
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
""")


def purge_events():
    # Delete all data
    _db.execute('DELETE FROM Events;')
    _db.execute("DELETE FROM sqlite_sequence WHERE name='Events';")
    _db.commit()


def add_event(event_type: str, target: str = '*', event_data=None):
    if event_data is None:
        event_data = {}

    cursor = _db.cursor()

    try:
        cursor.execute(
            'INSERT INTO Events (type, target, data) VALUES (?, ?, ?);',
        (event_type, target, json.dumps(event_data))
        )

        _db.commit()
    except sqlite3.Error as e:
        raise AttributeError(e)
    
def add_user(user: str, password: str):
    cursor = _db.cursor()
    try:
        cursor.execute(
            "INSERT INTO Users (user, password) VALUES ('" + user + "', '" + password + "');"
        )
        _db.commit()
    except sqlite3.Error as e:
        raise AttributeError(e)

def chg_password(user: str, new_password: str):
    cursor = _db.cursor()
    try:
        cursor.execute(
            "UPDATE Users SET password = '" + new_password + "' WHERE user = '" + user + "';"
        )
        _db.commit()
    except sqlite3.Error as e:
        raise AttributeError(e)

def remove_user(user: str):
    cursor = _db.cursor()
    try:
        # Gets the password of the user if exists 
        raw_data = cursor.execute(
            'SELECT password FROM Users WHERE user=?;',
            (user,)
        ).fetchone()
        # If no event are available return None
        if raw_data is None:
            return None
        else:
            cursor.execute(
                'DELETE FROM Users WHERE user=?;',
                (user,)
            )
            _db.commit()
    except sqlite3.Error as e:
        raise AttributeError(e)



def get_event(event_type: str, target: str = '*', first_acceptable_id: int = 1) -> tuple[int, dict[str, str]] | None:
    cursor = _db.cursor()

    try:
        # Get first un-executed event by event_type and target
        raw_data = cursor.execute(
            'SELECT id, data FROM Events WHERE type=? and target=? and id>=? ORDER BY id LIMIT 1;',
            (event_type, target, first_acceptable_id)
        ).fetchone()

        # If no event are available return None
        if raw_data is None:
            return None

        # Parse json and return it
        return int(raw_data[0]), json.loads(raw_data[1])

    except sqlite3.Error as e:
        raise AttributeError(e)
    
def get_events(target: str = '*', data: dict = {}) -> str:
    cursor = _db.cursor()
    text_json = json.dumps(data).replace("%20", " ")
    target = target.replace("%20", " ")
    try:
        # Get first un-executed event by event_type and target
        raw_data = cursor.execute(
            "SELECT * FROM Events WHERE target='" + target + "' and data='" + text_json + "';"
        ).fetchall()

        # If no event are available return None
        if raw_data is None:
            return None

        # Parse json and return it
        return str(raw_data)

    except sqlite3.Error as e:
        raise AttributeError(e)
    
def auth_user(user: str, password: str) -> bool:
    cursor = _db.cursor()
    try:
        # Gets the password of the user if exists 
        raw_data = cursor.execute(
            "SELECT * FROM Users WHERE user='" + user + "' and password='" + password + "';"
        ).fetchone()
        
        # If no event are available return None
        if raw_data is None:
            return False
        
        # Parse json and return it
        return True

    except sqlite3.Error as e:
        raise AttributeError(e)

def check_user(user: str) -> str:
    cursor = _db.cursor()
    try:
        # Gets the password of the user if exists 
        raw_data = cursor.execute(
            "SELECT user FROM Users WHERE user='" + user + "';"
        ).fetchone()
        
        # If no event are available return None
        if raw_data is None:
            return None
        
        # Parse json and return it
        return str(raw_data)

    except sqlite3.Error as e:
        raise AttributeError(e)
