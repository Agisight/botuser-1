FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /aiohttp/
WORKDIR /aiohttp/
ADD requirements.txt /aiohttp/
RUN pip install -r requirements.txt
