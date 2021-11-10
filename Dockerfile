FROM python:3.10-slim

WORKDIR /api

COPY /api/requirements.txt requirements.txt

RUN pip install  --no-cache-dir -r  requirements.txt

COPY ./api .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
# CMD ["ls",  "-la"]


