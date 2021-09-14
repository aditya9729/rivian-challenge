# use the ubuntu base image
FROM ubuntu:18.04

# install necessary packages
# first update package index using apt
RUN apt-get update -y && apt-get install -y python3-pip python3-dev git gcc g++

#make app the working directory
WORKDIR /app

#transfer requirements.txt to app directory
COPY requirements.txt /app/requirements.txt

#upgrade pip
RUN pip3 install --upgrade pip
#install necessary packages using pip, requirements.txt
RUN pip3 install -r requirements.txt --use-deprecated=legacy-resolver

#copy all the files in host working directory to app directory of container
COPY . /app/
