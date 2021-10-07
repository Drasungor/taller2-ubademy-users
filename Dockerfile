FROM node:14

WORKDIR /app
RUN apt-get update
#RUN apt-get -y install postgresql-client
RUN apt-get -y update
RUN apt-get -y install python3
RUN sudo apt-get install --reinstall libpq-dev
RUN pip3 install psycopg2
RUN pip3 install sqlalchemy

COPY package* /app/

#RUN npm ci

#COPY index.js /app/

CMD python3 main
