FROM python:3.7-slim

RUN mkdir /triage-o-matic
RUN mkdir /triage-o-matic/config

WORKDIR /triage-o-matic

COPY requirements.txt .

RUN pip install -r requirements.txt
COPY vectra.py .

COPY README.md .
COPY vectra.py .
COPY triage-o-matic.py .

LABEL maintainer="Craig Simon <csimon@vectra.ai>" version="1.0"

CMD python triage-o-matic.py
