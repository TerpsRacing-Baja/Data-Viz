import psycopg2
from flask import Flask
import time

app = Flask(__name__)

def get_db_connection():
    db_params = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": "gettr0lledA!"
    }

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)
    return conn


@app.route('/')
def home():
    
    return "yeppers"

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
    

@app.route('/time')
def get_current_time():
    return {'time': time.time()}