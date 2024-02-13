from flask import Flask
from flask import Flask, request
import time
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)

app.config.from_object(__name__)

CORS(app, resources={r"/*":{'origins':"*"}})


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
    #df = pd.read_csv("C:/Users/Frank/Documents/GitHub/Data-Viz/senor_data/test_sensor.csv")
    
    print(set_path("C:/Users/Frank/Documents/GitHub/Data-Viz/react-flask-app/flask/senor_data/test_sensor.csv"))
    print("step1")
    print(csv_directory)
    print("step2")
    print(start_read_csv())
    print()
    print(get_next_time())
    
    
    
    return "yeppers"

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

## csv/ reprsents commands that will read from a csv in the "csv_directory"
csv_directory = ""
unix_time = 0
df = None

time_label = "Unix time"

#sets the path of the csv used
@app.route('/csv/set_path/<path:directory>' , methods=['POST'])
def set_path(directory):
    global csv_directory
    csv_directory = directory
    return csv_directory

#must be ran before trying to read from csv
@app.route('/csv/start_read_csv')
def start_read_csv():
    global df
    df = pd.read_csv(csv_directory)
    return df

#sets unix time
@app.route('/csv/set_time')
def set_time():
    global unix_time
    return unix_time

#gets unix time
@app.route('/csv/get_time/<new_time>')
def get_time(new_time):
    global unix_time
    unix_time = new_time
    return unix_time

#increments unix time
@app.route('/csv/increment_time/<new_time>')
def increment_time(new_time):
    global unix_time
    unix_time = new_time+get_time()
    return unix_time


#returns the next used time
@app.route('/csv/get_next_time/')
def get_next_time_with_params():
    increments_time = request.args.get('increments_time', False)
    returns_error = request.args.get('returns_error', True)
    
    return get_next_time(increments_time, returns_error)


def get_next_time(increments_time = False, returns_error = True):
    global unix_time
    
    next_time = df[df[time_label] > unix_time][time_label].min()
   
    if next_time is None and returns_error:
        raise ValueError("There are no more possible times avaliable")
        return -1
    
    if (increments_time):
        set_time(next_time)
        
    return next_time

#gets all the indexes that have the same "unix time" value as unix_time 
@app.route('/csv/get_current/<desired_time>')
def get_current_with_params(desired_time):
    increments_time = request.args.get('increments_time', False)
    
    return get_current(desired_time, increments_time)
    

def get_current(desired_time, increments_time = False):
    filtered_data = df[df[time_label] == desired_time]
    
    if(increments_time):
        get_next_time(increments_time = True)
        
    return filtered_data

#returns all the data from a time frame that is unix_time to unix_time+window. Will also increment the time
@app.route('/csv/get_window/<window>')
def get_window_with_params(window):
    increments_time = request.args.get('increments_time', False)
    return get_current(window, increments_time)

def get_window(window, increments_time = False):
    
    filtered_data = df[(df[time_label] >= unix_time) & (df[time_label] <= unix_time+window)]
    
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
    

#@app.route('/filter_data')
#def filter_data(data, desired_filter, column = "Sensor"):
#    final_filtered_data = data[data['sensor'] == desired_filter]
#    return final_filtered_data
    

@app.route('/shark', methods=['GET'])
def shark():
    print("I have been called")
    return("Shark!")
