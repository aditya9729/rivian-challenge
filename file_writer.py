import yaml
import time
from boto3.s3.transfer import TransferConfig
import logging.config
from src.file_writer_s3 import write_to_s3
from src.file_writer_test import test_copy_data
from config import config
import argparse
import sys
import os

logging.basicConfig(filename=os.path.join(os.getcwd(),'config','logging','file_writer_main.log'),level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

logger.setLevel("INFO")

def fill_buffer(folder,timing=config.timing,time_type=config.time_type):
    """Time_type can only be hourly, minute wise or second wise, 12 'h' means 12 hour period"""

    terminate_signal = False
    start_time = time.time()
    while not terminate_signal:
        sink = set(os.listdir(folder))
        end_time = time.time() -start_time
        if time_type=='h':
            final_time = end_time/3600
        elif time_type=='m':
            final_time = end_time/60
        else:
            final_time = end_time
        if final_time>=timing:
            terminate_signal=True
            return sink

def delete_files(src,file_names):

    for file in file_names:
        print(file)
        os.remove(os.path.join(src, file))
        print(os.path.exists(os.path.join(src, file)))
        logger.debug("File %s removed from src to save memory",file)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="File writer to S3")

    parser.add_argument('step', help='Which step to run',
                        choices=['write_to_s3', 'test'])
    parser.add_argument('--input', '-i', default=None,
                        help='Path to input data (optional,default=None)')
    parser.add_argument('--config', default=None,
                        help='Path to configuration file')
    parser.add_argument('--output', '-o', default=None,
                        help='Path to save output file (optional, default = None)')

    args = parser.parse_args()

    # Load configuration file for parameters and tmo path
    with open(args.config, "r") as f:
        yaml_config = yaml.load(f, Loader=yaml.FullLoader)

    logger.info("Configuration file loaded from %s" % args.config)

    # S3 configurations
    bucket_name = yaml_config['file_writer_s3']['bucket_name']
    folder = yaml_config['file_writer_s3']['folder_name']
    use_threads = yaml_config['file_writer_s3']['usethreads']
    max_concurrency = yaml_config['file_writer_s3']['concurrency']
    storage = yaml_config['file_writer_s3']['storage']
    src = yaml_config['file_writer_test']['source_folder']
    dest = yaml_config['file_writer_test']['destination_folder']
    access_key = config.AWS_ACCESS_KEY_ID
    secret_key = config.AWS_SECRET_ACCESS_KEY
    region_name = config.AWS_REGION
    s3_folder =config.s3_folder
    # capacity planning - storage here is 5GB, uses threads and concurrency is 10. You can reduce it to make it simpler.
    trans_config = TransferConfig(multipart_threshold=storage*(1024**3),
                                  max_concurrency=max_concurrency, use_threads=use_threads)
    if args.step == 'write_to_s3':
        while True:

            sink = fill_buffer(folder,timing=1,time_type='m')
            try:
                file_names,num_files = write_to_s3(
                    bucket_name, access_key, secret_key, sink, folder,trans_config, region_name,s3_folder)  # Transfer config here
                logger.info(
                    "Successfully stored %s on S3, there were already %s files",str(num_files),str(len(os.listdir(folder))-num_files))
                delete_files(folder, file_names)
            except Exception as e:
                logger.error("Couldn't write to S3", e)
                sys.exit(1)
    else:
        # run tests
        if not os.path.exists(dest):
                os.makedirs(dest)
        while True:
            try:
                sink = fill_buffer(src,timing=1,time_type='m')
                file_names=test_copy_data(sink,src, dest)
                delete_files(src, file_names)
            except Exception as e:
                logger.error("Couldn't test the writer", e)
                sys.exit(1)
