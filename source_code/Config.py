import os

path = os.path

ROOT_DIR = path.realpath(path.dirname(__file__))

SERVER_FILE_STORAGE_PATH = f"{ROOT_DIR}/server/storage"

CLIENT_FILE_STORAGE_PATH = f"{ROOT_DIR}/client/storage"

DATA_MAPPING_LOCATION = f"{ROOT_DIR}/server/data_mapping.json"

SERVER_LOG_LOCATION = f"{ROOT_DIR}/server/server_log.csv"

CLIENT_LOG_LOCATION = f"{ROOT_DIR}/client/client_log.csv"

MAX_BUFFER_SIZE = 10000

DATE_FORMAT = "%m-%d-%Y"

CONTROL_CONNECTION_PORT_NUMBER = 21

DATA_CONNECTION_PORT_NUMBER = 20

SERVER_ERROR_LOG_FILE_PATH = f"{ROOT_DIR}/server/logs/error_log.csv"

CLIENT_ERROR_LOG_FILE_PATH = f"{ROOT_DIR}/client/logs/error_log.csv"

CLIENT_TRANSFERS_LOG_FILE_PATH = f"{ROOT_DIR}/client/logs/transfers_log.csv"

SERVER_TRANSFERS_LOG_FILE_PATH = f"{ROOT_DIR}/server/logs/transfers_log.csv"