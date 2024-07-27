FROM node as builder

WORKDIR /app

COPY ./app/src ./src
COPY ./app/index.html .
COPY ./app/package.json .
COPY ./app/package-lock.json .

RUN npm install
RUN npx vite build

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY ./notes ./notes
COPY app.py .
COPY models.py .
COPY dbstuff.py .
COPY ingest.py .

COPY --from=builder /app/dist /app/static

RUN python ingest.py
CMD ["python", "app.py"]