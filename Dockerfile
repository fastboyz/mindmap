FROM python:3.10-slim

WORKDIR /api

COPY requirements.txt requirements.txt

RUN pip install  --no-cache-dir -r  requirements.txt

COPY ./api .

CMD uvicorn main:app --host  0.0.0.0 --port $PORT


