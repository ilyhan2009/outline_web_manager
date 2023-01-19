FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED=1

WORKDIR /outline_web_manager

COPY . /outline_web_manager

RUN python3 -m venv env
RUN . env/bin/activate
RUN ls -n
RUN pip install -r requirements.txt

EXPOSE 8000

