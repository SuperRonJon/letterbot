import sqlite3

class Connection:
    _conn = None

    def __init__(self, db_path='letterbot.db'):
        self._path = db_path
        if Connection._conn is None:
            self._connect_to_db()

    def _connect_to_db(self):
        Connection._conn = sqlite3.connect(self._path)

    def get_cursor(self):
        if Connection._conn is not None:
            return Connection._conn.cursor()
        else:
            self._connect_to_db()
            return Connection._conn.cursor()

    def close_connection(self):
        if Connection._conn is not None:
            Connection._conn.close() 
            Connection._conn = None
    
    def commit(self):
        if Connection._conn is not None:
            Connection._conn.commit()