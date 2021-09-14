import boto3
from tqdm import tqdm
import logging
import os
import sys
from botocore.config import Config
from datetime import datetime, timezone


logging.basicConfig(filename=os.path.join(os.getcwd(),'config','logging','file_writer_s3.log'),level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
# WRITE DATA TO S3


def write_to_s3(bucket_name, access_key, secret_key, sink, folder,config, region_name,s3_folder=None):
	"""Writes data to the s3 bucket or stores in s3
	:param bucket_name `str`: AWS s3 bucket name
	:param access_key `str`: AWS access key id
	:param secret_key `str`: AWS secret key
	:param sink `set`: file names
	:param folder `str`:Folder name containing files
	:param region_name `str`: AWS region
	:param s3_folder `str`: Object folder
	:return: file name list and number of files
	"""
	try:
		my_config = Config(region_name=region_name)
		s3 = boto3.client('s3', aws_access_key_id=access_key,aws_secret_access_key=secret_key, config=my_config)
		bucket = s3.create_bucket(Bucket=str(bucket_name))
		logger.debug('Successfully connected to boto client')
	except Exception as error1:
		logger.error("Couldn't find the credentials, check aws credentials and try again", error1)
		sys.exit(1)

	file_size, count,file_names= 0, 0 , []
	# upload files to s3
	try:
		for file in tqdm(sink):
			file_path = os.path.join(folder, file)
			file_names.append(file)
			if 'Contents' in s3.list_objects(Bucket=bucket_name, Prefix=file): ## checks if file is  present inside bucket
				logger.debug("%s already present in S3 bucket of size %s bytes",file,str(os.path.getsize(file_path)))
			else:
				utc_dt = datetime.now(timezone.utc)  # UTC time
				dt = utc_dt.astimezone()  # local time
				s3_object = os.path.join(s3_folder,dt.strftime("%m/%d/%Y %I:%M:%S %p %Z")+"-"+str(file)) if s3_folder else dt.strftime("%m/%d/%Y %I:%M:%S %p %Z")+"-"+str(file)
				s3.upload_file(os.path.join(folder, file),bucket_name,s3_object, Config=config)
				count += 1
				file_size += os.path.getsize(file_path)

				logger.debug("Wrote %s to S3 of size %s bytes", file, str(os.path.getsize(file_path)))
		logger.debug("Total size of %s files uploaded to S3 bucket %s is %s bytes",str(count),bucket_name,str(file_size))
	except Exception as error2:
		logger.error("Couldn't find files in the folder given to write to S3",error2)
		sys.exit(1)
	return file_names,count
