import os
import psycopg2
import sqlalchemy as db
import time

def clean():
    '''
    This Function is used to clean up if the program is cancelled unexpedetly,
    and while program is running since the data becomes very old quickly so the table is truncated
    every 5 minutes
    '''
    path = '/home/L/Programming/dataEng/spaceApp/Streaming/StreamingFiles/json_data'
    DATABASE_LOCATION = "postgresql://airflow:airflow@localhost:5432/spaceData"
    dir_list = os.listdir(path)
    os.chdir(path)
    keep = dir_list[0]
    remove = dir_list[1:]

    for i in remove:
        os.remove(i)
    os.rename(keep,'SattelitePositions0.json')

    while True:
        engine = db.create_engine(DATABASE_LOCATION)
        truncate = ''' TRUNCATE TABLE position;'''
        engine.execute(truncate)
        print('\n\nTable truncated\n\n')
        time.sleep(300)

