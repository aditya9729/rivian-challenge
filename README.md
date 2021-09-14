# Rivian Digital Manufacturing Engineering DevOps Challenge                                                                                                                        
Your mission, should you choose to accept it, is to help us find a solution to move data off of a system that was provided to us by one of our many vendors. Unfortunately, we can't change that system's code, but we can partially bring it into the future by running it in Kubernetes ☸.

Created by - Aditya Gudal

<!-- toc -->

- [Directory structure](#directory-structure)
- [Instructions](#instructions)
- [Running the S3 Uploader](#running-the-s3-uploader)
  * [Configurations](#configurations)
  * [Local Dev Setup](#local-dev-setup)
- [Running the Tests](#running-the-tests)
- [Capacity Planning](#capacity-planning)
- [Monitoring](#monitoring)
- [Idealized Architecture](#idealized-architecture)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── app 
│
├── base/                             <- Common volume data storage
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── config.py                     <- Configuration of AWS credentials taken up from environment variable calls
│   ├── config.yaml	              <- Some folder path - /var/file-writer/data, URL endpoint, S3 bucket name, capacity planning configurations 
│   ├── config.env	              <- Environment variables AWS credentials
|
│
├── src/                              <- Source data,python scripts for the project - file_writer_s3.py and file_writer_test.py
│
├── file_writer.py                    <- Run file_writer_s3.py or testing code from /var/file-writer/data to tmp2 folder 
├── docker-compose.yaml               <- Composes two services - one service has the rivian file writer instance and the other is the s3 uploading app
├── dockerfile                        <- Docker file to build image
├── README.md                         <- Detailed instructions to run pipeline, app and tests
├── requirements.txt                  <- Python package dependencies 
├── file-writer-deploy.yaml           <- file writer spec trivial definition
├── Instructions.md                   <- Instructions on completing the assignment
```
## Instructions

Pika, one of our feline data scientists is also bit of a jack of all trades and started putting a few things together for you but, being a data scientist (and a cat) wasn't sure how to continue making progress. Pika has put together a skeletal Kubernetes deployment and figured out that when the `file-writer` container runs, it writes seems to periodically write data files to `/var/file-writer/data`. Pika really wishes those files would be available in an S3 bucket so they can be analyzed. Pika, being a wise cat, is also worried that if this `file-writer` keeps running forever, it might run out of storage. After 1 day (we have 2x 12-hour production shifts in the factory) and assuming the files are securely in s3, there's really no need for them locally on the container.

Pika wasn't sure what to do next and so relieved you're able to help.

## Running the S3 Uploader

**Configurations**
There are certain configurations to be set before running the app. Go to the config directory and use the config.env file to set the AWS credentials and regions. Make sure that if you are using a VPN or a specific IP config please set up the necessary rules and endpoints for access to the s3 bucket where we want to send the data. Refer the AWS documentation: https://docs.aws.amazon.com/AmazonS3/latest/userguide/setting-up-s3.html. For proxies fill in the config from botocore under `src/file_writer_s3.py` within `write_to_s3` function as a dictionary.

After saving config.env file, go to config.yaml in the config directory and set the s3 bucket name - `bucket_name` and leave the folder name as base. This is the directory which has the shared volume, here the Rivian `file-writer` writes to. Our goal is to stream the data from this base directory to the s3 bucket. 

Save the config.yaml and move to config.py where you can set the `s3_folder` which is the directory or object within the bucket we want to save in. For now its default is None, assuming we are saving into the bucket directly.

Dockerfile uses Ubuntu 18.04 as base and gets gcc compiler, pip and python. The S3 uploader uses AWS' python sdk boto3.

This app runs with `Docker` using docker-compose.

**Local Dev Setup**
To run the app make sure to clone this repo with the git clone command followed by the following command for local development set up(check config file first) using:

    docker-compose --env-file ./config/config.env config

To run app if configuration is fine run (if not fine - then export the variables into .awsconfig and source into bashrc):

    docker-compose --env-file ./config/config.env up

This should show you the file_writer container streaming data in. The logic developed is, we fill a buffer for 12 hours,as workers on shifts can take a look (this is customizable, you can change it to 6 mins too by setting timing = 6 and time_type='m' in config.py(m=minutes,h=hours,s=seconds). The app waits for 12 hours while filling the buffer, once 12 hours are done, we check whether the file exists in the bucket if it doesn't we upload it to the s3. Once the buffer is emptied, we remove the uploaded files(the ones already present in s3 and the ones uploaded) from the base volume and continue the process.

This planning helps reduce local disk space usage. 12 hours are picked for the workers to atleast peak at the data before it goes into S3. A better way would be storing data into a lightweight database for sometime before deleting. For s3 transfer we use TranserConfig api to set maximum concurrency(10), multipart thresholding(5GB), and using the threads which can be set within config.yaml.

If you look at the `docker-compose.yaml` file  you will find two services one is the `file-writer` instance by Rivian and the other is the uploader app. Both share a mounted volume called `base` from which we can share the data coming in from the file-writer instance and a network connector.

***Important***: within `docker-compose.yaml` file services under app you can comment out one of the commands. One command uses python3 and runs the file_writer_s3.py, then other runs the test.

## Running the tests
Comment out the s3 python3 command within `docker-compose.yaml` file and comment in the file_writer_test.py python command. Use the following command

    docker-compose up
  
This should stream the files into a destination tmp2 folder on local disk every 1 minute, using the same logic as s3 uploader app.

## Capacity Planning
I have explained some capacity planning for the operators above. Furthermore I have seen the data coming in are on average 12 files per second of size 1KB each - which is literally 12KB of data per second or 43 MB per hour or 516 MB per 12 hours. Keeping a cap of 1 GB for local disk since every 12 hours, this gets cleaned up would be great. Bandwidth of 1 Mbps would be great for data coming in - assuming seamless transfer and no jitter.

## Monitoring

I have used python's logging to take in dlog statements for the production environment(although my file is for the dev environment). The metrics logged are Number of files, Time in UTC and size in bytes. Take a look at the logs within config/logging .log files. Files written to S3 have filenames prefixed with the local time. Also, we track the files deleted and those are already written to S3.

## Idealized Architecture
* I haven't created a yaml file for production environment that would have been required.
* Using a k8 deployment we can scale it out to a better infrastructure if the data gets bigger, for now I have used docker-compose due to time constraints. 
* Multi-threads or Asynchronous operations to send data to S3 would be a great option.
* Healthchecks and standby hot services are required for backup.
* Deleting data shouldn't be an option, a data warehouse or database architecture should be used.
* Streaming analytics should be performed to understand if the files are really useful information.


