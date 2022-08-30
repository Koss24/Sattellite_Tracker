
from skyfield.api import load, wgs84, EarthSatellite
import pandas as pd
import numpy as np
import time
from multiprocessing import Pool, cpu_count, Value
import math
import socket
import json
import os
from datetime import datetime
import re


# def DMS_TO_DD(dms_string):
#     new = dms_string.split()

#     wholenum = int(''.join(filter(lambda i: i.isdigit(), new[0])))
#     minute = float(''.join(filter(lambda i: i.isdigit(), new[1]))) / 60
#     second = float(new[2][0:len(new[2])-1]) / 3600
  
#     DD = wholenum + minute + second
#     return DD


file_header = ['/opt/airflow/dags/','/home/L/Programming/dataEng/spaceApp/']

data = pd.read_json(f'/home/L/Programming/dataEng/spaceApp/airflow/dags/tempSatelliteData.json')

# filter to gather TLE data
newData = data.filter(['tle_line0', 'tle_line1', 'tle_line2'])

index = -1
rows = len(newData.axes[0])
# used to efficently use the number of cores for multiprocessing (# of files generated for each process)
k = cpu_count()
size = int(rows) / int(k)
size = math.ceil(size)

files = []

for i in range(k):
    df = newData[size*i:size*(i+1)]
    df.to_csv(f'{file_header[1]}Streaming/StreamingFiles/tle_data/Test_{i+1}.txt', sep='\n', index=False, header=None)
    # store file names
    files.append(f'{file_header[1]}Streaming/StreamingFiles/tle_data/Test_{i+1}.txt')

data = {"satname": {},"id": {},"lat":{},"lon":{}}

counter = 0

def sat_lat_lon(TLE_filename):
    # calculate the lat and lon of all satellites found in a TLE file   
    ts = load.timescale()
    t = ts.now()
    global counter
    satellites = load.tle_file(TLE_filename)
    by_name = {sat.name: sat for sat in satellites}
    for satellite in satellites:

        geocentric = satellite.at(t)
        lat,lon = wgs84.latlon_of(geocentric)

        '''
        lat = str(lat)
        lon = str(lon)
        
        print(f'This is lat: {lat}')
        print(f'This is lat: {lon}')
        print('\n\n')
        DMS_lat = lat.split()

        if (DMS_lat[0] == '00' or DMS_lat[1] == '00 'or DMS_lat[2] == '00'):
            res = int(re.sub("\D", "", DMS_lat[0]))
            res1 = float(re.sub("\D", "", DMS_lat[1])) / 60 
            res2 = float(DMS_lat[2][:len(DMS_lat[2])-1]) / 3600 
        else:
            res = int(re.sub("\D", "", DMS_lat[0]).lstrip("0"))
            res1 = float(re.sub("\D", "", DMS_lat[1]).lstrip("0")) / 60
            res2 = float(DMS_lat[2][:len(DMS_lat[2])-1].lstrip("0")) / 3600
            
        DD_lat = res + res1 + res2

        DMS_lon = lon.split()

        if (DMS_lon[0] == '00' or DMS_lon[1] == '00 'or DMS_lon[2] == '00'):
            res = int(re.sub("\D", "", DMS_lon[0]))
            res1 = float(re.sub("\D", "", DMS_lon[1])) / 60
            res2 = float(DMS_lon[2][:len(DMS_lon[2])-1]) /3600
        else:
            res = int(re.sub("\D", "", DMS_lon[0]).lstrip("0"))
            res1 = float(re.sub("\D", "", DMS_lon[1]).lstrip("0")) / 60
            res2 = float(DMS_lon[2][:len(DMS_lon[2])-1].lstrip("0")) / 3600

        DD_lon = res + res1 + res2
        '''
        data["satname"].update({counter:satellite.name})
        data["id"].update({counter:satellite.model.satnum})
        data["lat"].update({counter:str(lat)})
        data["lon"].update({counter:str(lon)})
        counter += 1

    return data

c = 0
path = '/home/L/Programming/dataEng/spaceApp/Streaming/StreamingFiles/json_data'
dir_list = os.listdir(path)
print(f'The length is {len(dir_list)}')

while True:
    dir_list = os.listdir(path)
    if len(dir_list) <= 2:
        p = Pool()
        result = p.map(sat_lat_lon, files)
        p.close()
        p.join()
        result = result[0]

        with open(f'{file_header[1]}Streaming/StreamingFiles/json_data/SattelitePositions{c}.json', 'a') as f:
            json.dump(result, f)
    else:
        print('===================================')
        print("\n   Waiting on streaming Data\n")
        print('===================================\n')
        time.sleep(1)

    c += 1
    #time.sleep(3)

    










