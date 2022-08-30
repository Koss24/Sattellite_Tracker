
from flask import Flask, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from graphviz import render
import sys
import psycopg2
import subprocess
from multiprocessing import Process
import time


app=Flask(__name__)
app.secret_key = "27eduCBA09"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://frontend:airflow@localhost/spaceData'
db = SQLAlchemy(app)




tracker = []
markers={}
def DMS_TO_DD(dms_string):
    new = dms_string.split()

    wholenum = int(''.join(filter(lambda i: i.isdigit(), new[0])))
    minute = float(''.join(filter(lambda i: i.isdigit(), new[1]))) / 60
    second = float(new[2][0:len(new[2])-1]) / 3600
  
    DD = wholenum + minute + second
    return DD


@app.route('/')
def root():
    session['tracking_list'] =  tracker
    conn = psycopg2.connect(
        database="spaceData", user='frontend', password='airflow', host='localhost', port= '5432'
    )
    cursor = conn.cursor()
    
    #print("Connection established to: ",data)
    for i in tracker:
        markerdata = {}
        print('\n\n')
        print(i)
        print('\n\n')
        cursor.execute(f"""SELECT satname, lat, lon FROM position WHERE id = {i} ORDER BY created_at DESC""")
        data = cursor.fetchone()
        #data = data[0]
        print('\n\n')
        print(data)
        print('\n\n')
        
        lat = DMS_TO_DD(data[1])
        lon = DMS_TO_DD(data[2])

        # lat = data[1]
        # lon = data[2]

        markerdata["lat"] = lat
        markerdata["lon"] = lon
        markerdata["popup"] = data[0]

        markers[i] = markerdata
    

    conn.close()
   
    return render_template('index.html', markers=markers)

@app.route('/record')
def rec():
    conn = psycopg2.connect(
        database="spaceData", user='frontend', password='airflow', host='localhost', port= '5432'
    )
    cursor = conn.cursor()
    cursor.execute("""SELECT norad_cat_id, object_name  FROM satellitedata ORDER BY norad_cat_id""")
    # gives a tuple we can index it in audit.html
    data = cursor.fetchall()
    #print("Connection established to: ",data)
    print(data[0])
    conn.close()
    return render_template('record.html', data=data)


@app.route('/test')
def recsss():
    conn = psycopg2.connect(
        database="spaceData", user='frontend', password='airflow', host='localhost', port= '5432'
    )
    cursor = conn.cursor()
    cursor.execute("""SELECT id, satname FROM position ORDER BY id""")
    # gives a tuple we can index it in audit.html
    data = cursor.fetchall()
    #print("Connection established to: ",data)
    print(data[0])
    conn.close()
    return render_template('record.html', data=data)

@app.route('/ss')
def ss():
    x = session.get('tracking_list')
    return render_template('session.html', x=x)

@app.route('/tracking/<int:id>')
def appendTracking(id):
    tracker.append(id)
    session['tracking_list'] = tracker
    return redirect(url_for('rec'))

@app.route('/untrack/<int:id>')
def removeTracking(id):
    tracker.remove(id)
    session['tracking_list'] =  tracker
    return redirect(url_for('rec'))

if __name__ == '__main__':
    
    import cleaner
    sys.path.insert(0, '/home/L/Programming/dataEng/spaceApp/Streaming')

    from read_data import read

    p = Process(target=app.run)
    p.start()
    p1 = Process(target=cleaner.clean)
    p1.start()
    p2 = Process(target=read)
    p2.start()


    # subprocess.Popen(['python3', 'cleaner.py'])
    # subprocess.Popen(['python3', '/home/L/Programming/dataEng/spaceApp/Streaming/read_data.py'])
    # subprocess.Popen(['python3', '/home/L/Programming/dataEng/spaceApp/Streaming/streamGenerator.py'])


