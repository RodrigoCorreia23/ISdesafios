import os
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server Configuration
GRPC_SERVER_PORT = os.getenv('GRPC_SERVER_PORT', '50052')
MAX_WORKERS = int(os.getenv('MAX_WORKERS', '10'))

# Media Files
MEDIA_PATH = os.getenv('MEDIA_PATH', f'{os.getcwd()}/app/media')

# Database Configuration
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBUSERNAME = os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD = os.getenv('DBPASSWORD', 'mypassword')
DBHOST = os.getenv('DBHOST', 'localhost')
DBPORT = int(os.getenv('DBPORT', '5432'))

# Log loaded configurations
logger.info(f"GRPC_SERVER_PORT: {GRPC_SERVER_PORT}")
logger.info(f"MAX_WORKERS: {MAX_WORKERS}")
logger.info(f"MEDIA_PATH: {MEDIA_PATH}")
logger.info(f"DBNAME: {DBNAME}")
logger.info(f"DBUSERNAME: {DBUSERNAME}")
logger.info(f"DBPASSWORD: {DBPASSWORD}")  
logger.info(f"DBHOST: {DBHOST}")
logger.info(f"DBPORT: {DBPORT}")
