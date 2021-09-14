from tqdm import tqdm
import logging
import os
import shutil
import sys
logging.basicConfig(filename=os.path.join(os.getcwd(),'config','logging','file_writer_test.log'),level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
# WRITE DATA TO S3


def test_copy_data(sink,src, dest):
	"""Copies data files from source to destinatin
	:param src `str`:Path to src folder
	:param dest `str`: Path to destination folder
	:return file_names `list`
	"""

	file_size, count, file_names = 0, 0, []
	source_files = sink
	# upload files to s3
	try:
		for file in tqdm(source_files):
			if file in os.listdir(dest):
				logger.debug("%s already present dest of size %s bytes",file,str(os.path.getsize(os.path.join(src,file))))
			else:
				count += 1
				file_names.append(file)
				print(file)
				file_size += os.path.getsize(os.path.join(src, file))
				shutil.copy(os.path.join(src, file), dest)

				logger.debug("Wrote %s to destination of size %s bytes", file,str(os.path.getsize(os.path.join(src, file))))
		logger.debug("Total size of %s files uploaded to %s is %s bytes",file,dest,str(file_size))
	except Exception as error2:
		logger.error("Couldn't find files in the folder given to write to dest",error2)
		sys.exit(1)
	return file_names
