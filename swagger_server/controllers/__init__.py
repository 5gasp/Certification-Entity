import logging
import redis
import os
from logging.handlers import TimedRotatingFileHandler
from swagger_server import constants as c

# Read REDIS Location
REDIS_LOCATION = os.environ.get('REDIS_LOCATION')
pool = redis.ConnectionPool(host=REDIS_LOCATION, port=6379, db=0)
mRedis = redis.Redis(connection_pool=pool)


logger = logging.getLogger('cert_entity')
if logger.hasHandlers():
    logger.handlers = []
file_handler = TimedRotatingFileHandler(c.log_file, when='midnight', backupCount=14)
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
