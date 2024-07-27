FROM python:3.9-slim

RUN apt-get update
RUN apt-get -y install libpq-dev gcc

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./notes ./notes
COPY app.py .
COPY models.py .
COPY ingest.py .
COPY dbstuff.py .
COPY init.sh .

CMD ["sh", "init.sh"]