import pandas as pd
import sqlalchemy as db
import os

def load_into_database():
    # use localhost if youre not running docker container

    data = pd.read_json('/opt/airflow/dags/tempSatelliteData.json')
    
    DATABASE_LOCATION = "postgresql://airflow:airflow@host.docker.internal:5432/spaceData"
    engine = db.create_engine(DATABASE_LOCATION)
    data.to_sql('satellitedata', engine, index=False, if_exists='append')
    os.remove('/opt/airflow/dags/tempSatelliteData.json')
    remove_duplicates = ''' DELETE FROM satellitedata
                                WHERE ctid IN (SELECT min(ctid)
                                    FROM satellitedata
                                    GROUP BY object_id
                                    HAVING count(*) > 1
                                    )
                                RETURNING *;'''
    engine.execute(remove_duplicates)
