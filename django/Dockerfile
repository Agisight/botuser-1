FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /botproject/
WORKDIR /botproject/
ADD requirements.txt /botproject/
RUN pip install -r requirements.txt
