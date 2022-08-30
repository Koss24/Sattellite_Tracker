from os import truncate
import socket
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SQLContext,SparkSession
from pyspark.sql import functions as  F
#from pyspark.sql.types import *

def read():
    file_header = ['/opt/airflow/dags/', '/home/L/Programming/dataEng/spaceApp/']

    conf = SparkConf()
    conf.set("spark.jars", f"{file_header[1]}jdbc_driver/postgresql-42.4.2.jar")

    spark = SparkSession \
        .builder \
        .config(conf=conf) \
        .getOrCreate()

    schema = spark.read.json(f"{file_header[1]}Streaming/StreamingFiles/json_data/SattelitePositions0.json")

    df = spark \
        .readStream \
        .schema(schema.schema) \
        .option("maxFilesPerTrigger",1) \
        .option("cleanSource","delete") \
        .json(f"{file_header[1]}/Streaming/StreamingFiles/json_data")

    #df.printSchema()


    newdf = df.select(
        F.array(F.expr("id.*")).alias("id"),
        F.array(F.expr("satname.*")).alias("satname"),
        F.array(F.expr("lat.*")).alias("lat"),
        F.array(F.expr("lon.*")).alias("lon")
    )

    newdf.printSchema()

    final_df = newdf.withColumn("collection", F.explode(F.arrays_zip("id", "satname","lat","lon")))\
        .select("collection.id","collection.satname","collection.lat","collection.lon")\

    # result_console = final_df.writeStream \
    #     .format("console") \
    #     .outputMode("update") \
    #     .start() \
    #     .awaitTermination()
    #.option("truncate","true") \

    def _write_streaming(df, epoch_id):         
        df.select('id','satname','lat','lon') \
            .write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://localhost:5432/spaceData") \
            .option("driver", "org.postgresql.Driver") \
            .option("dbtable", 'position') \
            .option("user", 'airflow') \
            .option("password", 'airflow') \
            .mode('append') \
            .save()

    result = final_df.writeStream \
        .foreachBatch(_write_streaming) \
        .start() \
        .awaitTermination()


