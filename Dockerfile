FROM python:3-alpine

COPY . /app 
WORKDIR /app

RUN apk update && apk add --no-cache git
RUN pip install -r requirements.txt

ENV PYTHONPATH /app 
CMD ["python","/app/main.py"]