FROM python

WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r requirements.txt
RUN pip3 install psycopg2
RUN pip3 install sqlalchemy
RUN pip3 install newrelic

#ENV DATABASE_URL="postgres://pwmutypretbutp:e74306821a303bd574c10c1444dc22cd053edcc139d06b53fd5f457b1df725eb@ec2-34-199-15-136.compute-1.amazonaws.com:5432/df3a67v8n8bo9b"
#ENV DATABASE_URL="sqlite:///./sql_app.db"
ENV DATABASE_URL="postgres://postgres:123456@postgres:5432/postgres"
ENV PORT=8001
EXPOSE $PORT
COPY main.py /app/
COPY database_models /app/database_models
COPY configuration /app/configuration
COPY config_files /app/config_files
COPY models /app/models
COPY database /app/database
COPY newrelic.ini /app/
COPY server_exceptions /app/server_exceptions
COPY server_exceptions /app/server_exceptions
COPY wait-for-postgres.sh /app/wait-for-postgres.sh

#CMD python3 main.py
#CMD sh wait-for-postgres.sh $DATABASE_URL NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python3 main.py
CMD NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program python3 main.py
