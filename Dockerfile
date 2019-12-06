FROM python:3.7-alpine3.10

RUN apk add --update alpine-sdk libxml2-dev libxslt-dev linux-headers python3-dev libffi-dev musl-dev
RUN apk add --update openssl-dev postgresql-dev python-dev

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN pip3 install -r requirements.txt

COPY . /usr/src/app

#RUN alembic upgrade head

EXPOSE 8080

CMD uvicorn asgi:app --host 0.0.0.0 --port 8080
