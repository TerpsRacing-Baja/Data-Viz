import psycopg2
from flask import Flask
import time

app = Flask(__name__)

def get_db_connection():
    db_params = {
        "host": "localhost",
        "database": "postgres",
        "user": "postgres",
        "password": "INSERT_YOUR_SQL_PASSWORD_HERE"
    }

    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)
    return conn


@app.route('/')
def home():
    return "yeppers"

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

## csv/ reprsents commands that will read from read from a csv in the "csv_directory"
csv_directory = ""

## database/ represents commands that take from the SQL database
@app.route('/database/latest')
def get_last():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(session_number) FROM sessions")
    max_session_number = cur.fetchone()[0]
    print(max_session_number)
    
    return {'latest': max_session_number}
    





#Test code. Taken from https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application
@app.route('/books')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM sessions;')
    books = cur.fetchall()
    cur.close()
    conn.close()
    return books