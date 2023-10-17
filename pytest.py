import datetime
from queue import Queue
#import serial
import time
import os
import csv
import psycopg2



# AS STANDS: currently extracts data from serial -> dictionary, then,
# once done, adds it to database 
# Nonfunctional until either:
    # We get the names of the sensors & I can create corresponding tables in DB
    # Functionality to create tables internally is implemented into the code
# To get it to become live-updating:
    # 1. Adds to dictionary, simulataneously adding it to DB
        # - Can be done by simply moving code from below into the parse() function
    # 2. Just adds to DB, forgoing dictionary 

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

## pass string in form (“LABEL|NAME|UNIT|TIMESTAMP|DATA”) and a dictionary 
#ie, TEST|TEST SENSOR|Testies|1696177714958|59.000000
#will fill dictionary with keys corasponding to the sensor name
#Will fill queue in dictionary with key "sensor_name" with Data objects created from "string"
#TODO: Ensure that everything that enters the dictionary is all lowercase as it will be stored in DB 
def parse(string, dictionary):
    string_split = string.split("|")

    sensor_name = string_split[1]
    unix = int(string_split[3])
    data = float(string_split[4])
    
    my_data = Data(string_split[2],unix ,data)
    
    if(sensor_name in dictionary):
        dictionary[sensor_name].put(my_data)
        
    else:
        queue = Queue()
        dictionary[sensor_name] = queue
        dictionary[sensor_name].put(my_data)
        
   #print(my_data)
    return sensor_name, my_data

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
        
    
    
dictionary = {}
##arduino = serial.Serial(port='COM3',  baudrate=9600, timeout=.1)##Probably needs to change
running = True
dump_everything_to_csv = True

cnt = 0
while running:
    ##time.sleep(0.05)
    line = "TEST|test_sensor|Testies|1696177714958|59.000000"##arduino.readline()
    ##TODO: check what arduino reads out and make it nicer to parse
    ##TODO: Set running to false somehow if you want to dump everything to a csv
    ##line = arduino.readline()
    ##line = str(line) 
    ##if "|" in line:
    ##    line = line[2:]
    ##    line = line[:-5]
    parse(line, dictionary)

    
    cnt+=1
    print("Parse: " + str(cnt))
    if cnt>10:
        running = False


# Commits the queues of data in each sensor in dictionary to the database.
    # Note: Can be made live-updating by simply working this into the parse() function
try:
    for sensor, data_queue in dictionary.items():
    # SQL query, needs to be tested
    # Note: This assumes that the tables have been set-up, with each sensor being a table and 
    #       columns UNIX, UNIT, VALUE
    #           - This can be done by creating the tables from within code, though this would 
    #             constantly overwrite previous data as we would need to delete everything every run 
         # Data is inserted into rows of table as Unix | Unit | Value in the table corresponding to the sensor 
        #data_to_insert = [(data.getUnix(), data.getValue()) for data in data_queue.queue]

        for data in data_queue.queue:
         data_unix = data.getUnix()
         data_value = data.getValue()
         insert_query = "INSERT INTO test_sensor (UNIX, VALUE) VALUES (\'" + str(data_unix) + "\', \'" + str(data_value) + "\')"
         print(insert_query)
         cursor.execute(insert_query)
         conn.commit()

except Exception as e:
    print(f"Error: {str(e)}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()


       
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
