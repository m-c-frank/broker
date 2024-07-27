FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./notes ./notes
COPY app.py .
COPY models.py .
COPY dbstuff.py .

CMD ["python", "app.py"]