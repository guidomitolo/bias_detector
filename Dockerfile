FROM ubuntu:latest

RUN apt-get update && apt-get install -y --no-install-recommends gcc

### Java
RUN apt-get install default-jdk -y

### Python
RUN apt-get install -y python

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set work directory
WORKDIR /bias_detector

RUN apt-get install python3-pip -y

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . .

