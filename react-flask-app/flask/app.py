import psycopg2
from flask import Flask
import time
import pandas as pd

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
unix_time = 0
df = None



#sets the path of the csv used
@app.route('/csv/set_path')
def set_time(path):
    csv_directory = path
    return csv_directory

#must be ran before trying to read from csv
@app.rount('csv/start_read_csv')
def start_read_csv():
    df = pd.read_csv(csv_directory)

#sets unix time
@app.route('/csv/set_time')
def set_time():
    return unix_time

#gets unix time
@app.route('/csv/get_time')
def get_time(new_time):
    unix_time = new_time
    return unix_time

#increments unix time
@app.route('/csv/increment_time')
def increment_time(new_time):
    unix_time = new_time+unix_time
    return unix_time

#returns the next used time
@app.route('/csv/get_next_time')
def get_next_time(increments_time = False, returns_error = True):
    next_time = df[df['unix time'] > unix_time]['unix time'].min()
    
    if not pd.isna(next_time) and returns_error:
        raise ValueError("There are no more possible times avaliable")
        return -1
    
    if (increments_time):
        set_time(next_time)
        
    return next_time

#gets all the indexes that have the same "unix time" value as unix_time 
@app.route('/csv/get_current')
def get_current(desired_time, increments_time = False):
    filtered_data = df[df['unix time'] == desired_time]
    
    if(increments_time):
        get_next_time(increments_time = True)
        
    return filtered_data

#returns all the data from a time frame that is unix_time to unix_time+window. Will also increment the time
@app.route('/csv/get_window')
def get_window(window, increments_time = False):
    
    filtered_data = df[(df['unix time'] >= unix_time) & (df['unix time'] <= unix_time+window)]
    
    if increments_time:
        set_time(unix_time+window)
        get_next_time(increments_time = True)
    return filtered_data

## database/ represents commands that take from the SQL database
@app.route('/database/latest')
def get_last():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT MAX(session_number) FROM sessions")
    max_session_number = cur.fetchone()[0]
    print(max_session_number)
    
    return {'latest': max_session_number}
    

@app.route('/filter_data')
def filter_data(data, desired_filter, column = "Sensor"):
    final_filtered_data = data[data['sensor'] == desired_filter]
    return final_filtered_data
    


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