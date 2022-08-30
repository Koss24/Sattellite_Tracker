##
## SLTrack.py
## (c) 2019 Andrew Stokes  All Rights Reserved
##
##
## Simple Python app to extract Starlink satellite history data from www.space-track.org into a spreadsheet
## (Note action for you in the code below, to set up a config file with your access and output details)
##
##
##  Copyright Notice:
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  For full licencing terms, please refer to the GNU General Public License
##  (gpl-3_0.txt) distributed with this release, or see
##  http://www.gnu.org/licenses/.
##

import requests
import json
import configparser
#import xlsxwriter
import time
from datetime import datetime
import pandas as pd
import sqlalchemy as db

class MyError(Exception):
    def __init___(self,args):
        Exception.__init__(self,"my exception was raised with arguments {0}".format(args))
        self.args = args

# use requests package to drive the RESTful session with space-track.org
def api_call():
    '''
    This function makes an api call to space-track.org to get the gp data of all orbiting objects
    '''
    uriBase                = "https://www.space-track.org"
    requestLogin           = "/ajaxauth/login"
    requestCmdAction       = "/basicspacedata/query" 
    requestData  = "/class/gp/decay_date/null-val/epoch/%3Enow-30/orderby/norad_cat_id/format/json "

    config = configparser.ConfigParser()
    config.read("/opt/airflow/dags/SLTrack.ini")
    configUsr = config.get("configuration","username")
    configPwd = config.get("configuration","password")
    configOut = config.get("configuration","output")
    siteCred = {'identity': configUsr, 'password': configPwd}

    with requests.Session() as session:
        # run the session in a with block to force session to close if we exit

        # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
        resp = session.post(uriBase + requestLogin, data = siteCred)
        if resp.status_code != 200:
            raise MyError(resp, "POST fail on login")

        # this query picks up all gp data from the catalog. Note - a 401 failure shows you have bad credentials 
        resp = session.get(uriBase + requestCmdAction + requestData)
        if resp.status_code != 200:
            print(resp)
            raise MyError(resp, "GET fail on request for satellites")

    
        data = pd.read_json(resp.text)
        session.close()
    print("Completed session") 

    
    return data


def transform_data(df: pd.DataFrame):
    for column in df.columns:
        df = df.rename(columns={f"{column}":f"{column.lower()}"})
        print(column.lower())
    return df

def load_satellite_data():
    data = api_call()
    data = transform_data(data)
    data.to_json('/opt/airflow/dags/tempSatelliteData.json')



    # # use localhost if youre not running docker container
    # DATABASE_LOCATION = "postgresql://airflow:airflow@host.docker.internal:5432/spaceData"
    # engine = db.create_engine(DATABASE_LOCATION)
    # data.to_sql('satellitedata', engine, index=False, if_exists='append')

    # remove_duplicates = ''' DELETE FROM satellitedata
    #                             WHERE ctid IN (SELECT min(ctid)
    #                                 FROM satellitedata
    #                                 GROUP BY object_id
    #                                 HAVING count(*) > 1
    #                                 )
    #                             RETURNING *;'''
    # engine.execute(remove_duplicates)

#UN COMMENT FOR API CALL
load_satellite_data()