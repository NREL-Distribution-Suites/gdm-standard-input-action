FROM python:3.12-slim

COPY . /app 
WORKDIR /app

RUN apt-get update && apt-get install -y git
RUN pip install -r requirements.txt

ENV PYTHONPATH /app 
CMD ["python","/app/main.py"]