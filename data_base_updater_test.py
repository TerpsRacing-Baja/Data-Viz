import datetime
from queue import Queue
#import serial
import time
import os
import csv
import psycopg2

# This code takes input serial data from our sensors, processes it, and stores it in an 
# internal dictionary & an external local PostgreSQL database.

# TODO: rewrite cursors so they open and close directly before and after each execution 

#stores value, unit, and the unix time
class Data:
    def __init__(self, unit, unix, value):
        self.unit = unit
        self.unix = unix
        self.value = value
        
    def getUnix(self):
        return self.unix
    
    def getTime(self):
        return datetime.datetime.fromtimestamp(self.unix/1000)
    
    def getValue(self):
        return self.value
    
    def getUnit(self):
        return self.unit
    
    def __str__(self):
        return str(self.getTime()) + "|" + str(self.value) +"|"+ str(self.unit)
    
# Parameters of the database, local to my machine
db_params = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": ""
}

# Establish a connection to the database
conn = psycopg2.connect(**db_params)

# Create a cursor object to interact with the database
cursor = conn.cursor()

def checkTableExists(cursor, tablename):
    cursor.execute("""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{0}'
        """.format(tablename.replace('\'', '\'\'')))
    if cursor.fetchone()[0] == 1:
        #cursor.close()
        return True

# gets the next available session name
def get_next_session_name():
    print("huh")
    
    if(checkTableExists(cursor, "sessions") == None):
        print("missing table")
        table_name = "sessions"
        create_table_query = f"CREATE TABLE {table_name} (session_number integer)"
        cursor.execute(create_table_query)
    
    print("woahahaha")
    
    
    cursor.execute("SELECT MAX(session_number) FROM sessions")
    max_session_number = cursor.fetchone()[0]
    if max_session_number is not None:
        return f"session_{max_session_number + 1}"
    else:
        return "session_1"
    
# creates a new table corresponding to the session #
def create_session_table(table_name):
        print("Creating table " + str(table_name) + "...")
        # Creates table in the database named 'table_name' with appropriate columns/datatypes
        create_table_query = f"CREATE TABLE {table_name} (sensor_name text, value double precision, unix bigint)"
        cursor.execute(create_table_query)
        # Adds the table that was just created into the 'sessions' table
        session_number = int(table_name[-1])
        print("Adding table number " + str(session_number) + " to 'sessions'...")
        insert_into_sessions_query=f"INSERT INTO sessions (session_number) VALUES (\'{session_number}\')"
        cursor.execute(insert_into_sessions_query)
        conn.commit()
   
# inputs 'data' into 'sensor_name' table in database
def input_to_database(table_name, sensor_name, data):
    try:
        data_unix = data.getUnix()
        data_value = data.getValue()
        # Data is inserted into rows of table as sensor_name | unix | value in the table corresponding to the sensor 
        insert_query = "INSERT INTO " + str(table_name) + " (SENSOR_NAME, UNIX, VALUE) VALUES (\'" + str(sensor_name) + "\',\'"+ str(data_unix) + "\', \'" + str(data_value) + "\')"
        #print(insert_query)
        cursor.execute(insert_query)
        conn.commit()
        print("Successfully input " + str(data_value) + " into table " + table_name + ".")
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()


# pass string in form (“LABEL|NAME|UNIT|TIMESTAMP|DATA”) and a dictionary 
# ie, TEST|TEST SENSOR|Testies|1696177714958|59.000000
# will fill dictionary with keys corresponding to the sensor name
# Will fill queue in dictionary with key "sensor_name" with Data objects created from "string"

def parse(table_name, string, dictionary):
    string_split = string.split("|")
    # Extracts necessary data from the string arg & puts to lower case into Data object
    sensor_name = string_split[1].lower()
    unix = int(string_split[3])
    data = float(string_split[4])
    
    my_data = Data(string_split[2],unix ,data)
    # Stores in appropriate dictionary
    if(sensor_name in dictionary):
        dictionary[sensor_name].put(my_data)
    else:
        queue = Queue()
        dictionary[sensor_name] = queue
        dictionary[sensor_name].put(my_data)
    # Places parsed data into database
    input_to_database(table_name, sensor_name, my_data)  
    return sensor_name, my_data
        
#designed to get data from the key at dictionary. Count is the number of Data objects dequed from the queue at key of dictionary
#returns Data.__str__() of each Data object dequed. Goal is to send the strings from one computer to another
def getData(dictionary, key, count):
    list = []
    for x in range (0, count):
        if(not dictionary[key].empty()):
            list.append(dictionary[key].get().__str__())
        else:
            return list
    return list
        
# Stores name of the current table being operated on
table_name = get_next_session_name()

# Creates new table for each session 
create_session_table(table_name)
    
dictionary = {}
##arduino = serial.Serial(port='COM3',  baudrate=9600, timeout=.1)##Probably needs to change
running = True
dump_everything_to_csv = False
cnt = 0

# Grabs data from sensor and parses it.
while running:
    # Modify this value to change frequency at which we process sensor data 
    ##time.sleep(0.05)

    # Set to a test string, can change to be the serial data read from sensor (which needs formatting)
    line = "TEST|test_sensor|Testies|1696177714958|59.364234"##arduino.readline()
    ##TODO: check what arduino reads out and make it nicer to parse
    ##TODO: Set running to false somehow if you want to dump everything to a csv
    ##line = arduino.readline()
    ##line = str(line) 
    ##if "|" in line:
    ##    line = line[2:]
    ##    line = line[:-5]

    parse(table_name, line, dictionary)
    # Arbitrary test count to simulate some data being entered to the program w/ our test string
    cnt+=1
    if cnt>5:
        running = False


#
if(dump_everything_to_csv):
    #creating a folder named 'sensor_data' to store data if it does not exist
    print("wowzer")
    path = os.getcwd()
    print(path)
    new_folder_name = "senor_data"
    folder_path = os.path.join(path, new_folder_name)
    
    print(folder_path)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    #Calls parse(string)
    #creates a folder in folder_path named 'label' returned from parse(string)
    #creates a csv file in said folder if it does not exist. The file is named 'sensor_name' returned from parse(string). csv will have fields = ['Unix time', 'Data', 'unit']
    #writes to said csv file with unix, data, unit from parse(string)
    #if in_unix_time is set to false, it will convert unix to datetime when writing. Not recomended or supported tbh i still need to work on it
    def write_data_to_file(dictionary, folder_path, in_unix_time = True):
        print("wowzer2")
        print(folder_path)
        for key, value in dictionary.items():
            print("wowzer3")
            
            file_name = key + ".csv"
            data_path = os.path.join(folder_path, file_name)
            
            print(data_path)
                
            fields = ['Unix time', 'Data', 'unit']
            if(not in_unix_time):
                fields[0] = 'Time'
            
            check_file = os.path.isfile(data_path)
            if(not check_file):
                print("file does not exist")
                with open(data_path, 'w') as csvfile:
                    # creating a csv writer object
                    writer = csv.DictWriter(csvfile, fieldnames = fields)
                    writer.writeheader()
                    
                    csvfile.close()
            
                
            with open(data_path, 'a') as csvfile:
                # creating a csv writer object
                writer = csv.DictWriter(csvfile, fieldnames = fields)
                
                for data in value.queue: ##iterate through Queue object at Key
                    print(data)
                    if (in_unix_time):
                        dict = {'Unix time': data.getUnix(), 'Data': data.getValue(), 'unit':data.getUnit()}
                    else:
                        dict = {'Time': data.getTime(), 'Data': data.getValue(), 'unit':data.getUnit()}
                        
                    writer.writerow(dict)
                csvfile.close()
        
    write_data_to_file(dictionary, folder_path)

# Close data leaks - might need to move to another part of code
cursor.close()
conn.close()
