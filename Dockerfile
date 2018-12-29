FROM python:3.5

COPY . /opt/api
WORKDIR /opt/api

ENV DATABASE_URL "mysql+mysqlconnector://root:supersecure@mysql/piggydime"

RUN pip install -r requirements.txt

EXPOSE 5000