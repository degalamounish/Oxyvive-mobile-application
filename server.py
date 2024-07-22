import os
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
                anvil.server.connect("server_MQU7VM2VS3ZSCQL3SRGX3EZA-J25NXHNSQOR7LIWH")
                self.anvil_connected = True
                print("Connected to anvil.server")
        except OSError:
            print("Internet is not connected or Anvil connection failed")

    def is_connected(self):
        return self.anvil_connected

    def get_database_connection(self):
        if self.is_connected():
            # Use Anvil's database connection
            return anvil.server.connect("server_MQU7VM2VS3ZSCQL3SRGX3EZA-J25NXHNSQOR7LIWH")
        else:
            # Use SQLite database connection
            return sqlite3.connect('users.db')

    def sqlite3_users_db(self):
        try:
            # Get the directory of the current script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the database path within the application folder
            db_path = os.path.join(script_dir, "users.db")
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    pincode TEXT NOT NULL,
                    pan_card_no TEXT NOT NULL,
                    profile BLOB NOT NULL
                )
            ''')
            conn.commit()
            print(f"Connected to sqlite3 and table created successfully at {db_path}")
            return conn
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None