FROM apache/airflow:2.3.3
COPY requirments.txt /requirments.txt


RUN apt-get update
RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /requirments.txt


