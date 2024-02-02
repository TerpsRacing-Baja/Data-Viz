import time
from flask import Flask
import psycopg2

app = Flask(__name__)

def get_db_connection():
    db_params = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": ""
    }

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)
    return conn

@app.route('/time')
def get_current_time():
    print("yeah")
    return {'time': time.time()}

@app.route('/books')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sessions;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    return books


@app.route('/latest')
def get_last():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(session_number) FROM sessions")
    max_session_number = cur.fetchone()[0]
    
    
    print(max_session_number)
    
    return {'latest': max_session_number}