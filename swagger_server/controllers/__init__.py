import json
import logging
from logging.handlers import TimedRotatingFileHandler

from swagger_server import constants as c

# Load database file, structure:
# test_id:
#     access_token:
#     status:
#     cert:
#     chart:
# test_id:
#     ...
with open(c.database, 'r') as f:
    cert_data = json.load(f)
cert_data = {int(k): v for k, v in cert_data.items()}

logger = logging.getLogger('cert_entity')
if logger.hasHandlers():
    logger.handlers = []
file_handler = TimedRotatingFileHandler(c.log_file, when='midnight', backupCount=14)
formatter = logging.Formatter('%(asctime)s %(name)s:%(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
