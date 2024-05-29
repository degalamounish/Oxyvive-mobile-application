import threading
import socket
import sqlite3
import anvil.server

class Server:
    def __init__(self):
        self.anvil_connected = False
        self.anvil_connection_lock = threading.Lock()

        # Connect to Anvil in a separate thread
        threading.Thread(target=self.connect_to_anvil, daemon=True).start()

    def connect_to_anvil(self):
        try:
            # Attempt to create a socket connection to google.com
            socket.create_connection(("www.google.com", 80))

            # Connect to Anvil
            with self.anvil_connection_lock:
                anvil.server.connect("server_PTWCSFLNB4SATW3RVY3IRUSN-RMBAH6GYMLLHSP7F")
                self.anvil_connected = True
                print("Connected to anvil.server")
        except OSError:
            print("Internet is not connected or Anvil connection failed")

    def is_connected(self):
        return self.anvil_connected

    def get_database_connection(self):
        if self.is_connected():
            # Use Anvil's database connection
            return anvil.server.connect("server_PTWCSFLNB4SATW3RVY3IRUSN-RMBAH6GYMLLHSP7F")
        else:
            # Use SQLite database connection
            return sqlite3.connect('users.db')

    def sqlite3_users_db(self):
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                phone TEXT NOT NULL,
                pincode TEXT NOT NULL,
                pan_card_no TEXT NOT NULL
            )
        ''')
        conn.commit()
        print("Connected to sqlite3")
        return conn
