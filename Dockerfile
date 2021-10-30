FROM ubuntu

WORKDIR /app
RUN apt-get update
RUN apt-get -y update
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get install -y --reinstall libpq-dev
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install psycopg2
RUN pip3 install sqlalchemy
RUN pip3 install newrelic

ENV DATABASE_URL="postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b"
ENV PORT=8001
EXPOSE $PORT
COPY main.py /app/
COPY database_models /app/database_models
COPY configuration /app/configuration
COPY config_files /app/config_files
COPY models /app/models
COPY newrelic.ini /app/

#CMD python3 main.py
CMD NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python3 main.py
